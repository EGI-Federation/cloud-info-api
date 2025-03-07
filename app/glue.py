"""
Glue Objects and the helpers to manage them
"""

import glob
import json
import logging
import os.path

import httpx
from pydantic import BaseModel, computed_field


class VO(BaseModel):
    serial: int
    name: str


class VOStore:
    def __init__(self, ops_portal_url="", ops_portal_key=""):
        self._vos = []
        self.ops_portal_url = ops_portal_url
        self.ops_portal_key = ops_portal_key

    def update_vos(self):
        try:
            r = httpx.get(
                self.ops_portal_url,
                headers={
                    "accept": "application/json",
                    "X-API-Key": self.ops_portal_key,
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

    def start(self):
        self.get_vos()


class GlueImage(BaseModel):
    name: str
    image: dict


class GlueInstanceType(BaseModel):
    name: str
    instance_type: dict


class GlueShare(BaseModel):
    name: str
    vo: str
    share: dict
    images: list[GlueImage]
    instancetypes: list[GlueInstanceType]

    def image_list(self):
        return [
            dict(
                appdb_id=img.image.get("imageVAppCName", ""),
                id=img.image.get("ID", ""),
                mpuri=img.image.get("MarketPlaceURL", ""),
                name=img.image.get("imageVAppName", ""),
            )
            for img in self.images
        ]

    def get_project(self):
        return dict(id=self.share["ProjectID"], name=self.vo)


class GlueSite(BaseModel):
    name: str
    service: dict
    service_id: str
    manager: dict
    manager_id: str
    endpoint: dict
    endpoint_id: str
    shares: list[GlueShare]

    def supports_vo(self, vo_name):
        return any(share.vo == vo_name for share in self.shares)

    def vo_share(self, vo_name):
        for share in self.shares:
            if share.vo == vo_name:
                return share
        else:
            return None

    @computed_field
    def gocdb_id(self) -> str:
        return self.service["OtherInfo"]["gocdb_id"]

    def summary(self):
        return dict(
            id=self.gocdb_id, name=self.name, url=self.endpoint["URL"], state=""
        )


class SiteStore:
    def __init__(self, appdb_images_file="", cloud_info_dir=""):
        self._sites = []
        self.cloud_info_dir = cloud_info_dir
        try:
            # This file contains the result of the GraphQL query
            # {
            #  siteCloudComputingImages {
            #    items {
            #      marketPlaceURL
            #      imageVAppCName
            #      imageVAppName
            #    }
            #  }
            # }
            # and then cleaned up
            with open(appdb_images_file) as f:
                self._image_info = json.loads(f.read())
        except OSError as e:
            logging.error(f"Not able to load image info: {e.strerror}")
            self._image_info = {}

    def start(self):
        self._update_sites()

    def appdb_image_data(self, image_url):
        return self._image_info.get(image_url, {})

    def create_site(self, info):
        svc = info["CloudComputingService"][0]
        # yet another incongruency here
        mgr = info["CloudComputingManager"]
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
                        self.appdb_image_data(image_info["MarketPlaceURL"])
                    )
                    images.append(GlueImage(name=image_info["Name"], image=image_info))
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
                    instances.append(
                        GlueInstanceType(
                            name=instance_info["Name"], instance_type=instance_info
                        )
                    )
            share = GlueShare(
                name=share_info["Name"],
                share=share_info,
                vo=vo_name,
                images=images,
                instancetypes=instances,
            )
            shares.append(share)
        site = GlueSite(
            name=svc["Associations"]["AdminDomain"][0],
            service=svc,
            service_id=svc["ID"],
            manager=mgr,
            manager_id=mgr["ID"],
            endpoint=ept,
            endpoint_id=ept["ID"],
            shares=shares,
        )
        return site

    def _load_site_file(self, filename):
        with open(filename) as f:
            try:
                s = self.create_site(json.loads(f.read()))
                self._sites.append(s)
            except Exception as e:
                logging.error(f"Unable to load site {filename}: {e}")

    def _update_sites(self):
        if not self._sites:
            for json_file in glob.glob(os.path.join(self.cloud_info_dir, "*.json")):
                self._load_site_file(json_file)

    def get_sites(self, vo_name=None):
        self._update_sites()
        if vo_name:
            sites = filter(lambda s: s.supports_vo(vo_name), self._sites)
        else:
            sites = self._sites
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
