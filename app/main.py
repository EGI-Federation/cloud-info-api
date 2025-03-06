"""
Appdb Information Sistem

A simple wrapper around the cloud-info jsons to deliver the information
needed by IM
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from pydantic import BaseModel

from app.glue import SiteStore, VOStore


class Image(BaseModel):
    name: str
    appdb_id: str
    id: str
    mpuri: str


class Site(BaseModel):
    id: str
    name: str
    url: str
    state: str


class Project(BaseModel):
    id: str
    name: str


site_store = SiteStore()
vo_store = VOStore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    vo_store.start()
    site_store.start()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/vos/")
def get_vos() -> list[str]:
    vos = sorted([vo.name for vo in vo_store.get_vos()])
    return vos


@app.get("/sites/")
def get_sites(vo_name: str = "") -> list[Site]:
    return [Site(**s.summary()) for s in site_store.get_sites(vo_name)]


@app.get("/site/")
def get_site(site_name: str = "", service_type: str = "openstack") -> Site:
    if service_type != "openstack":
        return None
    site = site_store.get_site_by_name(site_name)
    if not site:
        raise HTTPException(status_code=404, detail=f"Site {site_name} not found")
    return Site(**site.summary())


def _get_site(site_id: str, vo_name: str = ""):
    site = site_store._get_site(site_id)
    if not site:
        raise HTTPException(status_code=404, detail=f"Site {site_id} not found")
    if vo_name and not site.supports_vo(vo_name):
        raise HTTPException(
            status_code=404, detail=f"VO {vo_name} not supported by Site {site_id}"
        )
    return site


@app.get("/site/{site_id}/")
def get_site_by_goc(site_id: str, service_type: str = "openstack") -> Site:
    if service_type != "openstack":
        return None
    return Site(**_get_site(site_id).summary())


@app.get("/site/{site_id}/{vo_name}/images")
def get_images(site_id: str, vo_name: str) -> list[Image]:
    site = _get_site(site_id, vo_name)
    return [Image(**img) for img in site.vo_share(vo_name).image_list()]


@app.get("/site/{site_id}/projects")
def get_site_project_ids(site_id: str) -> list[Project]:
    site = _get_site(site_id)
    return [Project(**share.get_project()) for share in site.shares]


@app.get("/site/{site_id}/{vo_name}/project")
def get_project_id(site_id: str, vo_name: str) -> Project:
    site = _get_site(site_id, vo_name)
    return Project(**site.vo_share(vo_name).get_project())
