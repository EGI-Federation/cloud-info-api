"""
Appdb Information Sistem

A simple wrapper around the cloud-info jsons to deliver the information
needed by IM
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from app.glue import FileSiteStore, VOStore


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


class Site(BaseModel):
    id: str
    name: str
    url: str
    state: str
    hostname: str
    projects: Optional[list[Project]] = None


class Settings(BaseSettings):
    appdb_disciplines_file: str = "data/vo-disciplines.json"
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
        "name": "images",
        "description": "Discovery of images.",
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
def get_disciplines() -> list[str]:
    data = []
    try:
        with open(settings.appdb_disciplines_file) as f:
            data = json.loads(f.read())
    except OSError as e:
        logging.error(f"Not able to load disciplines: {e.strerror}")
    return data


@app.get("/sites/", tags=["sites"], response_model_exclude_none=True)
def get_sites(
    vo_name: str = "", site_name: str = "", include_projects: bool = False
) -> list[Site]:
    """Get a list of available sites.

    Optionally filter by VO or site name (as listed in GOCDB).
    Optionally add details on projects
    """
    if site_name:
        site = site_store.get_site_by_name(site_name)
        if vo_name:
            if site.supports_vo(vo_name):
                return [Site(**site.summary(include_projects=include_projects))]
            else:
                return []
        else:
            return [Site(**site.summary(include_projects=include_projects))]
    return [
        Site(**s.summary(include_projects=include_projects))
        for s in site_store.get_sites(vo_name)
    ]


@app.get("/site/{site_name}/", tags=["sites"], response_model_exclude_none=True)
def get_site(site_name: str, include_projects: bool = False) -> Site:
    """Get site information

    Name of the site in the GOCDB
    """
    return Site(**_get_site(site_name).summary(include_projects=include_projects))


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
