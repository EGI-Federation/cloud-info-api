"""
Glue Objects and the helpers to manage them
"""

import asyncio
import glob
import itertools
import json
import logging
import os.path

import httpx
import xmltodict
from pydantic import BaseModel
from watchfiles import awatch


class VO(BaseModel):
    serial: int
    name: str


class VOStore:
    def __init__(
        self, ops_portal_url="", ops_portal_token="", httpx_client=None, **kwargs
    ):
        self.ops_portal_url = ops_portal_url
        self.ops_portal_token = ops_portal_token
        self._vos = []
        self._update_period = 60 * 60 * 2  # Every 2 hours
        if httpx_client:
            self.httpx_client = httpx_client
        else:
            self.httpx_client = httpx.Client()

    def update_vos(self):
        try:
            r = self.httpx_client.get(
                self.ops_portal_url,
                headers={
                    "accept": "application/json",
                    "X-API-Key": self.ops_portal_token,
                },
            )
            r.raise_for_status()
            vos = []
            for vo_info in r.json()["data"]:
                vo = VO(**vo_info)
                vos.append(vo)
            self._vos = vos
        except httpx.HTTPStatusError as e:
            logging.error(f"Unable to load VOs: {e}")
            self._vos = []

    def get_vos(self):
        if not self._vos:
            self.update_vos()
        return self._vos

    async def start(self):
        while True:
            self.update_vos()
            await asyncio.sleep(self._update_period)


class GlueImage(BaseModel):
    id: str
    name: str
    appdb_id: str
    mpuri: str
    version: str


class GlueInstanceType(BaseModel):
    name: str


class GlueShare(BaseModel):
    name: str
    vo: str
    project_id: str
    images: list[GlueImage]
    instancetypes: list[GlueInstanceType]

    def image_list(self):
        return [img.model_dump() for img in self.images]

    def get_project(self):
        return dict(id=self.project_id, name=self.vo)


class GlueSite(BaseModel):
    name: str
    url: str
    shares: list[GlueShare]
    hostname: str
    gocdb_id: str

    def supports_vo(self, vo_name):
        return any(share.vo == vo_name for share in self.shares)

    def vo_share(self, vo_name):
        for share in self.shares:
            if share.vo == vo_name:
                return share
        else:
            return None

    def image_list(self):
        return itertools.chain.from_iterable(s.image_list() for s in self.shares)

    def summary(self):
        return dict(
            id=self.gocdb_id,
            name=self.name,
            url=self.url,
            state="",
            hostname=self.hostname,
        )


class SiteStore:
    def __init__(self, gocdb_url="", appdb_images_file="", httpx_client=None, **kwargs):
        self.gocdb_hostnames = {}
        self.gocdb_url = gocdb_url
        if httpx_client:
            self.httpx_client = httpx_client
        else:
            self.httpx_client = httpx.Client()
        self._image_info = self._get_image_info(appdb_images_file)

    def _get_image_info(self, appdb_images_file):
        image_info = {}
        try:
            # This file contains the result of the GraphQL query
            # {
            #  siteCloudComputingImages {
            #    items {
            #      marketPlaceURL
            #      imageVAppCName
            #      imageVAppName
            #      version
            #    }
            #  }
            # }
            with open(appdb_images_file) as f:
                all_images = json.loads(f.read())
                for image in (
                    all_images.get("data", {})
                    .get("siteCloudComputingImages", {})
                    .get("items", [])
                ):
                    image_info[image["marketPlaceURL"]] = {
                        k: v for k, v in image.items() if v
                    }
        except OSError as e:
            logging.error(f"Not able to load image info: {e.strerror}")
        return image_info

    def _get_gocdb_hostname(self, gocid):
        if not self.gocdb_hostnames:
            try:
                r = self.httpx_client.get(
                    os.path.join(self.gocdb_url, "gocdbpi/public/"),
                    params={
                        "method": "get_service",
                        "service_type": "org.openstack.nova",
                    },
                )
                data = xmltodict.parse(r.text.replace("\n", ""))["results"]
                # xmltodict may return just the dict if only one element
                endpoints = data["SERVICE_ENDPOINT"]
                if not isinstance(endpoints, list):
                    endpoints = [endpoints]
                for endpoint in endpoints:
                    self.gocdb_hostnames[endpoint["@PRIMARY_KEY"]] = endpoint[
                        "HOSTNAME"
                    ]
            except httpx.HTTPStatusError as e:
                logging.error(f"Unable to load site information: {e}")
            except KeyError:
                logging.error("Unable to load site information")
        return self.gocdb_hostnames.get(gocid, "")

    async def start(self):
        return

    def _appdb_image_data(self, image_url):
        return self._image_info.get(image_url, {})

    def create_site(self, info):
        svc = info["CloudComputingService"][0]
        ept = info["CloudComputingEndpoint"][0]

        shares = []
        for share_info in info["Share"]:
            for policy in info["MappingPolicy"]:
                if policy["Associations"]["Share"] == share_info["ID"]:
                    vo_name = policy["Associations"]["PolicyUserDomain"]
                    break
            else:
                logging.warning("No VO Name!?")
                continue
            images = []
            for image_info in info["CloudComputingImage"]:
                if share_info["ID"] in image_info["Associations"]["Share"]:
                    image_info.update(
                        self._appdb_image_data(image_info["MarketPlaceURL"])
                    )
                    images.append(
                        GlueImage(
                            appdb_id=image_info.get("imageVAppCName", ""),
                            id=image_info.get("ID"),
                            mpuri=image_info.get("MarketPlaceURL", ""),
                            name=image_info.get("imageVAppName", image_info["Name"]),
                            version=image_info.get("version", ""),
                        )
                    )
            instances = []
            for instance_info in info["CloudComputingInstanceType"]:
                if share_info["ID"] in instance_info["Associations"]["Share"]:
                    # who does not love a long attribute name?
                    acc_id = instance_info["Associations"].get(
                        "CloudComputingInstanceTypeCloudComputingVirtualAccelerator"
                    )
                    if acc_id:
                        for acc in info["CloudComputingVirtualAccelerator"]:
                            if acc["ID"] == acc_id:
                                instance_info.update({"accelerator": acc})
                    instances.append(GlueInstanceType(name=instance_info["Name"]))
            share = GlueShare(
                name=share_info["Name"],
                project_id=share_info["ProjectID"],
                vo=vo_name,
                images=images,
                instancetypes=instances,
            )
            shares.append(share)
        gocdb_id = svc["OtherInfo"]["gocdb_id"]
        site = GlueSite(
            name=svc["Associations"]["AdminDomain"][0],
            gocdb_id=gocdb_id,
            url=ept["URL"],
            shares=shares,
            hostname=self._get_gocdb_hostname(gocdb_id),
        )
        return site

    def _sites(self):
        return []

    def get_sites(self, vo_name=None):
        if vo_name:
            sites = list(filter(lambda s: s.supports_vo(vo_name), self._sites()))
        else:
            sites = self._sites()
        return sites

    def get_site_by_goc_id(self, gocdb_id):
        for site in self.get_sites():
            if site.gocdb_id == gocdb_id:
                return site
        return None

    def get_site_by_name(self, name):
        for site in self.get_sites():
            if site.name == name:
                return site
        return None

    def get_site_summary(self, vo_name=None):
        if vo_name:
            sites = filter(lambda s: s.supports_vo(vo_name), self.get_sites())
        else:
            sites = self.get_sites()
        return (s.summary() for s in sites)


class FileSiteStore(SiteStore):
    """
    Loads Site information from a directory that's watched for changes
    """

    def __init__(self, cloud_info_dir="", **kwargs):
        super().__init__(**kwargs)
        self.cloud_info_dir = cloud_info_dir
        self._site_store = []

    def _load_site_file(self, path):
        try:
            with open(path) as f:
                return self.create_site(json.loads(f.read()))
        except Exception as e:
            logging.error(f"Unable to load site {path}: {e}")

    def _sites(self):
        return self._site_store

    def _load_sites(self):
        sites = []
        for file in glob.iglob(
            os.path.join(self.cloud_info_dir, "**/*.json"), recursive=True
        ):
            if os.path.isfile(file):
                sites.append(self._load_site_file(file))
                logging.debug(f"Loaded {file}")
        logging.info(f"Re-loaded info about {len(sites)} sites")
        self._site_store = sites

    async def start(self):
        self._load_sites()
        if os.path.exists(self.cloud_info_dir):
            async for changes in awatch(self.cloud_info_dir):
                # just reload everything
                self._load_sites()


class S3SiteStore(SiteStore):
    def __init__(self, s3_url="", **kwargs):
        super().__init__(**kwargs)
        self.s3_url = s3_url
        self._sites_info = {}
        self._update_period = 60 * 10  # 10 minutes

    def _load_site(self, site):
        name = site["name"]
        if name in self._sites_info:
            if site["last_modified"] == self._sites_info[name]["last_modified"]:
                # same update, no need to reload
                logging.info(f"No update neeeded for {name}")
                return {name: self._sites_info[name]}
        try:
            r = self.httpx_client.get(
                os.path.join(self.s3_url, name),
                headers={
                    "accept": "application/json",
                },
            )
            r.raise_for_status()
            try:
                site.update({"info": self.create_site(r.json())})
            except Exception as e:
                logging.error(f"Unable to load site {name}: {e}")
                return {}
            logging.info(f"Loaded info from {name}")
            return {name: site}
        except httpx.HTTPStatusError as e:
            logging.error(f"Unable to load site information: {e}")

    def _update_sites(self):
        new_sites = {}
        try:
            r = self.httpx_client.get(
                self.s3_url,
                headers={
                    "accept": "application/json",
                },
            )
            r.raise_for_status()
            for site in r.json():
                logging.error(f'Update site {site["name"]}')
                new_sites.update(self._load_site(site))
        except Exception as e:
            logging.error(f"Unable to load Sites: {e}")
        # change all at once
        self._sites_info = new_sites

    def _sites(self):
        return [site["info"] for site in self._sites_info.values()]

    async def start(self):
        while True:
            self._update_sites()
            await asyncio.sleep(self._update_period)
