"""
Glue Objects and the helpers to manage them
"""

import glob
import json

import httpx

from pydantic import BaseModel, computed_field


# This file contains the result of the GraphQL query
# {
#  siteCloudComputingImages {
#    totalCount
#    count
#    limit
#    items {
#      marketPlaceURL
#      imageVAppCName
#      imageVAppName
#    }
#  }
# }
# and then cleaned up
APPDB_IMAGES_FILE = "appdb-images.json"
OPS_PORTAL_URL = "https://operations-portal.egi.eu/api/vo-list/json"


class VO(BaseModel):
    serial: int
    name: str


class VOStore:
    def __init__(self, ops_portal_url=OPS_PORTAL_URL, ops_portal_key=""):
        self._vos = []
        self._portal_url = ops_portal_url
        self._portal_key = ops_portal_key

    def update_vos(self):
        try:
            r = httpx.get(
                OPS_PORTAL_URL,
                headers={"accept": "application/json", "X-API-Key": self._portal_key},
            )
            vos = []
            for vo_info in r.json()["data"]:
                vo = VO(**vo_info)
                vos.append(vo)
            self._vos = vos
        except Exception as e:
            # TODO: proper error handling
            print("BU")
            print(e)
            pass

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
    def __init__(self, appdb_images_file=APPDB_IMAGES_FILE):
        self._sites = []
        with open(appdb_images_file) as f:
            self._image_info = json.loads(f.read())

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
                print("NO VO NAME!")
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
                # Do not care, but maybe log?
                print(e)
                print("HU")

    def _update_sites(self):
        if not self._sites:
            for json_file in glob.glob("jsons/*.json"):
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
            print(site.gocdb_id, gocdb_id)
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
