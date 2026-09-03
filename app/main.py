"""
Appdb Information System

A simple wrapper around the cloud-info jsons to deliver the information
needed by IM
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

import yaml
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from .glue import Discipline, FileSiteStore, VOStore


class Image(BaseModel):
    egi_id: str
    id: str
    endpoint: str
    mpuri: str
    name: str
    version: str
    vo: str


class Project(BaseModel):
    id: str
    name: str


class SiteEndpoint(BaseModel):
    id: str
    name: str
    site_name: str
    url: str
    state: str
    hostname: str
    projects: Optional[list[Project]] = None


class Settings(BaseSettings):
    vo_disciplines_file: str = "data/vo-disciplines.json"
    ops_portal_url: str = "https://operations-portal.egi.eu/api/vo-list/json"
    ops_portal_token: str = ""
    cloud_info_dir: str = "cloud-info"
    s3_url: str = (
        "https://stratus-stor.ncg.ingrid.pt:8080/swift/v1/"
        "AUTH_bd5a81e1670b48f18af33b05512a9d77/cloud-info/"
    )
    gocdb_url: str = "https://goc.egi.eu"
    check_glue_validity: bool = True


settings = Settings()
site_store = FileSiteStore(**settings.model_dump())
vo_store = VOStore(**settings.model_dump())


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(vo_store.start())
    asyncio.create_task(site_store.start())
    yield


tags_metadata = [
    {
        "name": "vos",
        "description": "Discovery of VOs.",
    },
    {
        "name": "sites",
        "description": "Discovery of sites.",
    },
    {
        "name": "endpoints",
        "description": "Discovery of fedcloud endpoints.",
    },
    {
        "name": "images",
        "description": "Discovery of images.",
    },
    {
        "name": "fedcloudclient",
        "description": "Fedcloudclient configuration files.",
    },
]


app = FastAPI(
    title="cloud-info-api",
    summary="Fedcloud info API",
    version="0.1.0",
    contact={
        "name": "EGI Cloud Compute",
        "url": "https://www.egi.eu/service/cloud-compute/",
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/EGI-Federation/cloud-info-api/blob/main/LICENSE",
    },
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)


#
# Helper functions
#
def _get_site(site_name: str, vo_name: str = ""):
    """Gets site given a name and optionally a VO"""
    site = site_store.get_site_by_name(site_name)
    if not site:
        raise HTTPException(status_code=404, detail=f"Site {site_name} not found")
    if vo_name and not site.supports_vo(vo_name):
        raise HTTPException(
            status_code=404, detail=f"VO {vo_name} not supported by Site {site_name}"
        )
    return site


def _get_endpoint(ep_id: str, vo_name: str = ""):
    ep = site_store.get_site_by_goc_id(ep_id)
    if not ep:
        raise HTTPException(status_code=404, detail=f"Endpoint {ep_id} not found")
    if vo_name and not ep.supports_vo(vo_name):
        raise HTTPException(
            status_code=404, detail=f"VO {vo_name} not supported by Endpoint {ep_id}"
        )
    return ep


def filter_images(images: list[Image], only_egi_images: bool = True):
    """Filters images if only_egi_images is True"""
    if only_egi_images:
        return filter(lambda x: x.egi_id, images)
    else:
        return images


#
# API functions
#
@app.get("/vos/", tags=["vos"])
def get_vos() -> list[str]:
    """Get a list of available VOs."""
    vos = sorted([vo.name for vo in vo_store.get_vos()])
    return vos


@app.get("/disciplines/", tags=["vos"])
def get_disciplines() -> list[Discipline]:
    return vo_store.get_disciplines()


@app.get("/sites/", tags=["sites"], response_model_exclude_none=True)
def get_sites(
    vo_name: str = "", site_name: str = "", include_projects: bool = False
) -> list[SiteEndpoint]:
    """Get a list of available sites.

    Optionally filter by VO or site name (as listed in GOCDB).
    Optionally add details on projects
    """
    if site_name:
        site = site_store.get_site_by_name(site_name)
        if vo_name:
            if site.supports_vo(vo_name):
                return [SiteEndpoint(**site.summary(include_projects=include_projects))]
            else:
                return []
        else:
            return [SiteEndpoint(**site.summary(include_projects=include_projects))]
    return [
        SiteEndpoint(**s.summary(include_projects=include_projects))
        for s in site_store.get_sites(vo_name)
    ]


@app.get("/site/{site_name}/", tags=["sites"], response_model_exclude_none=True)
def get_site(site_name: str, include_projects: bool = False) -> SiteEndpoint:
    """Get site information

    Name of the site in the GOCDB
    """
    return SiteEndpoint(
        **_get_site(site_name).summary(include_projects=include_projects)
    )


@app.get("/site/{site_name}/projects", tags=["sites"])
def get_site_project_ids(site_name: str) -> list[Project]:
    """Get information about the projects supported at a site"""
    site = _get_site(site_name)
    return [Project(**share.get_project()) for share in site.shares]


@app.get("/site/{site_name}/images", tags=["sites"])
def get_site_images(site_name: str, only_egi_images: bool = True) -> list[Image]:
    """Get all images from a site"""
    site = _get_site(site_name)
    return filter_images(
        [Image(**img, endpoint=site.url) for img in site.image_list()], only_egi_images
    )


@app.get("/site/{site_name}/{vo_name}/project", tags=["sites"])
def get_project_id(site_name: str, vo_name: str) -> Project:
    """Get information about the project supporting a VO at a site"""
    site = _get_site(site_name, vo_name)
    return Project(**site.vo_share(vo_name).get_project())


@app.get("/site/{site_name}/{vo_name}/images", tags=["sites"])
def get_images(
    site_name: str, vo_name: str, only_egi_images: bool = True
) -> list[Image]:
    """Get information about the images of a VO"""
    site = _get_site(site_name, vo_name)
    return filter_images(
        [
            Image(**img, endpoint=site.url)
            for img in site.vo_share(vo_name).image_list()
        ],
        only_egi_images,
    )


@app.get("/images/", tags=["images"])
def get_all_images(vo_name: str = "", only_egi_images: bool = True) -> list[Image]:
    """Get a list of available images.

    Optionally filter by VO and EGI images.
    """
    images: list[Image] = []
    for site in site_store.get_sites(vo_name):
        if vo_name:
            images.extend(
                Image(**img, endpoint=site.url)
                for img in site.vo_share(vo_name).image_list()
            )
        else:
            images.extend(Image(**img, endpoint=site.url) for img in site.image_list())
    return filter_images(images, only_egi_images)


@app.get("/fedcloudclient/", tags=["fedcloudclient"])
def get_fedcloudclient_sites(request: Request) -> list[str]:
    """Get a list of available site configurations for fedcloudclient."""
    return [
        str(request.url_for("get_fedcloudclient_site", site_name=s.name))
        for s in site_store.get_sites()
    ]


@app.get("/fedcloudclient/{site_name}/", tags=["fedcloudclient"])
def get_fedcloudclient_site(site_name: str) -> str:
    """Get site information as yaml compatible with fedcloudclient

    ID of the site in GOCDB
    """
    site = _get_site(site_name)
    fedcloud_site = {
        "gocdb": site.site_name,
        "endpoint": site.url,
        "vos": [
            {"name": p.vo, "auth": {"project_id": p.project_id}} for p in site.shares
        ],
    }
    return Response(content=yaml.dump(fedcloud_site), media_type="application/yaml")


@app.get("/endpoints/", tags=["endpoints"], response_model_exclude_none=True)
def get_endpoints(
    vo_name: str = "", site_name: str = "", include_projects: bool = False
) -> list[SiteEndpoint]:
    """Get a list of available endpoints.

    Optionally filter by VO or site name (as listed in GOCDB).
    Optionally add details on projects
    """
    if site_name:
        eps = site_store.get_endpoints_by_site_name(site_name)
    else:
        eps = site_store.get_sites()
    if vo_name:
        eps = [ep for ep in eps if ep.supports_vo(vo_name)]
    return [SiteEndpoint(**ep.summary(include_projects=include_projects)) for ep in eps]


@app.get("/endpoint/{ep_id}/", tags=["endpoints"], response_model_exclude_none=True)
def get_endpoint(ep_id: str, include_projects: bool = False) -> SiteEndpoint:
    """Get endpoint information"""
    return SiteEndpoint(
        **_get_endpoint(ep_id).summary(include_projects=include_projects)
    )


@app.get("/endpoint/{ep_id}/projects", tags=["endpoints"])
def get_endpoint_project_ids(ep_id: str) -> list[Project]:
    """Get information about the projects supported at a endpoint"""
    endpoint = _get_endpoint(ep_id)
    return [Project(**share.get_project()) for share in endpoint.shares]


@app.get("/endpoint/{ep_id}/images", tags=["endpoints"])
def get_endpoint_images(ep_id: str, only_egi_images: bool = True) -> list[Image]:
    """Get all images from a endpoint"""
    endpoint = _get_endpoint(ep_id)
    return filter_images(
        [Image(**img, endpoint=endpoint.url) for img in endpoint.image_list()],
        only_egi_images,
    )


@app.get("/endpoint/{ep_id}/{vo_name}/project", tags=["endpoints"])
def get_endpoint_project_id(ep_id: str, vo_name: str) -> Project:
    """Get information about the project supporting a VO at a endpoint"""
    endpoint = _get_endpoint(ep_id, vo_name)
    return Project(**endpoint.vo_share(vo_name).get_project())


@app.get("/endpoint/{ep_id}/{vo_name}/images", tags=["endpoints"])
def get_endpoint_vo_images(ep_id: str, vo_name: str, only_egi_images: bool = True) -> list[Image]:
    """Get information about the images of a VO"""
    endpoint = _get_endpoint(ep_id, vo_name)
    return filter_images(
        [
            Image(**img, endpoint=endpoint.url)
            for img in endpoint.vo_share(vo_name).image_list()
        ],
        only_egi_images,
    )
