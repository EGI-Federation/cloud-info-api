"""Testing our glue component"""

import json
from unittest import mock

from http import HTTPStatus
import httpx

from app.glue import *
from app.test_fixtures import *


def test_gluesite_object():
    site = site_fixture
    # supports a VO?
    assert site.supports_vo("foo") == False
    assert site.supports_vo("ops") == True
    # get shares
    assert site.vo_share("foo") == None
    assert site.vo_share("ops") == site_fixture.shares[0]
    # summary
    assert site.summary() == {
        "hostname": "foo",
        "id": "12249G0",
        "name": "BIFI",
        "state": "",
        "url": "https://colossus.cesar.unizar.es:5000/v3",
    }
    # share project
    assert site_fixture.shares[0].get_project() == {
        "id": "038db3eeca5c4960a443a89b92373cd2",
        "name": "ops",
    }
    # images
    assert site_fixture.shares[0].image_list() == [
        {
            "name": "EGI Small Ubuntu for Monitoring",
            "version": "2024.11.18",
            "appdb_id": "egi.small.ubuntu.16.04.for.monitoring",
            "id": "06c8bfac-0f93-48da-b0eb-4fbad3356f73",
            "mpuri": "https://appdb.egi.eu/store/vo/image/63fcad1c-b737-5091-9668-1342b6d4f84c:15705/",
        }
    ]


def test_vo_store_get_vos():
    test_client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                HTTPStatus.OK, content=json.dumps(ops_portal_fixture)
            )
        )
    )
    vos = [VO(**vo) for vo in ops_portal_fixture["data"]]
    vo_store = VOStore(ops_portal_url="https://example.com", httpx_client=test_client)
    assert vos == vo_store.get_vos()


def test_vo_store_get_vos_failure():
    test_client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(HTTPStatus.FORBIDDEN, content="foo")
        )
    )
    vo_store = VOStore(ops_portal_url="https://example.com", httpx_client=test_client)
    assert [] == vo_store.get_vos()


def test_gocdb_info():
    test_client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(HTTPStatus.OK, content=gocdb_fixture)
        )
    )
    with mock.patch("app.glue.SiteStore._get_image_info"):
        site_store = SiteStore(
            gocdb_url="https://exmaple.com", httpx_client=test_client
        )
        hostname = site_store._get_gocdb_hostname("7513G0")
        assert hostname == "api.cloud.ifca.es"


def test_create_site():
    with (
        mock.patch("app.glue.SiteStore._get_image_info") as get_image_info,
        mock.patch("app.glue.SiteStore._get_gocdb_hostname") as goc_hostname,
    ):
        goc_hostname.return_value = "foo"
        get_image_info.return_value = appdb_image_fixture
        site_store = SiteStore()
        loaded_site = site_store.create_site(site_info_fixture)
        assert site_fixture == loaded_site


def test_get_sites():
    with (
        mock.patch("app.glue.SiteStore._get_image_info"),
        mock.patch("app.glue.SiteStore._sites") as _sites,
    ):
        site_store = SiteStore()
        _sites.return_value = [site_fixture]
        # no VO
        assert site_store.get_sites() == [site_fixture]
        # not supported VO
        assert site_store.get_sites("foo") == []
        # supported VO
        assert site_store.get_sites("ops") == [site_fixture]


def test_get_site_by_goc_id():
    with (
        mock.patch("app.glue.SiteStore._get_image_info"),
        mock.patch("app.glue.SiteStore._sites") as _sites,
    ):
        site_store = SiteStore()
        _sites.return_value = [site_fixture]
        # unknown ID
        assert site_store.get_site_by_goc_id("foo") == None
        # good ID
        assert site_store.get_site_by_goc_id("12249G0") == site_fixture


def test_get_site_by_name():
    with (
        mock.patch("app.glue.SiteStore._get_image_info"),
        mock.patch("app.glue.SiteStore._sites") as _sites,
    ):
        site_store = SiteStore()
        _sites.return_value = [site_fixture]
        # unknown name
        assert site_store.get_site_by_name("foo") == None
        # good name
        assert site_store.get_site_by_name("BIFI") == site_fixture


def test_get_site_summary():
    with (
        mock.patch("app.glue.SiteStore._get_image_info"),
        mock.patch("app.glue.SiteStore._sites") as _sites,
    ):
        site_store = SiteStore()
        _sites.return_value = [site_fixture]
        site_summary = site_fixture.summary()
        # no VO
        assert list(site_store.get_site_summary()) == [site_summary]
        # not supported VO
        assert list(site_store.get_site_summary("foo")) == []
        # supported VO
        assert list(site_store.get_site_summary("ops")) == [site_summary]
