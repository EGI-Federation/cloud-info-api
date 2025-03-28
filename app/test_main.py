"""Testing our glue component"""

import json
from unittest import mock
from unittest import TestCase


from http import HTTPStatus
from fastapi import HTTPException
import httpx

from fastapi.testclient import TestClient

from app.main import app, vo_store, site_store, _get_site
from app.glue import VO, GlueSite
from app.test_fixtures import *


bifi_summary = {
    "id": "12249G0",
    "name": "BIFI",
    "url": "https://colossus.cesar.unizar.es:5000/v3",
    "state": "",
    "hostname": "foo",
}


class TestAPI(TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_vos(self):
        with mock.patch.object(vo_store, "get_vos") as m_get_vos:
            m_get_vos.return_value = [
                VO(serial=1, name="foo"),
                VO(serial=2, name="bar"),
            ]
            response = self.client.get("/vos/")
            assert response.status_code == 200
            assert response.json() == ["bar", "foo"]

    def test_get_sites_no_name(self):
        with mock.patch.object(site_store, "get_sites") as m_get_sites:
            m_get_sites.return_value = [site_fixture]
            response = self.client.get("/sites/", params={"vo_name": "foo"})
            assert response.status_code == 200
            assert response.json() == [bifi_summary]
            m_get_sites.assert_called_with("foo")

    def test_get_sites_with_name(self):
        with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
            m_get_site.return_value = site_fixture
            # no VO
            response = self.client.get("/sites/", params={"site_name": "BIFI"})
            assert response.status_code == 200
            assert response.json() == [bifi_summary]
            m_get_site.assert_called_with("BIFI")
            # unsupported VO
            m_get_site.return_value = site_fixture
            response = self.client.get(
                "/sites/", params={"vo_name": "foo", "site_name": "BIFI"}
            )
            assert response.status_code == 200
            assert response.json() == []
            m_get_site.assert_called_with("BIFI")
            # supported VO
            m_get_site.return_value = site_fixture
            response = self.client.get(
                "/sites/", params={"vo_name": "ops", "site_name": "BIFI"}
            )
            assert response.status_code == 200
            assert response.json() == [bifi_summary]
            m_get_site.assert_called_with("BIFI")

    def test__get_site(self):
        with mock.patch.object(site_store, "get_site_by_goc_id") as m_get_site:
            m_get_site.return_value = site_fixture
            s = _get_site("foo")
            assert s == site_fixture
            # supported VO
            s = _get_site("foo", "ops")
            assert s == site_fixture
            # unsupported VO
            with self.assertRaises(HTTPException):
                s = _get_site("foo", "bar")

    def test__get_site_not_found(self):
        with mock.patch.object(site_store, "get_site_by_goc_id") as m_get_site:
            m_get_site.return_value = None
            with self.assertRaises(HTTPException):
                s = _get_site("foo")

    def test_get_site(self):
        with mock.patch.object(site_store, "get_site_by_goc_id") as m_get_site:
            m_get_site.return_value = site_fixture
            response = self.client.get("/site/foo/")
            assert response.status_code == 200
            assert response.json() == bifi_summary

    def test_get_site(self):
        with mock.patch.object(site_store, "get_site_by_goc_id") as m_get_site:
            m_get_site.return_value = None
            response = self.client.get("/site/foo/")
            assert response.status_code == 404

    def test_get_site_images(self):
        with mock.patch.object(site_store, "get_site_by_goc_id") as m_get_site:
            m_get_site.return_value = site_fixture
            response = self.client.get("/site/foo/images/")
            assert response.status_code == 200
            assert response.json() == [
                {
                    "appdb_id": "egi.small.ubuntu.16.04.for.monitoring",
                    "id": "06c8bfac-0f93-48da-b0eb-4fbad3356f73",
                    "mpuri": "https://appdb.egi.eu/store/vo/image/63fcad1c-b737-5091-9668-1342b6d4f84c:15705/",
                    "name": "EGI Small Ubuntu for Monitoring",
                    "version": "2024.11.18",
                },
            ]

    def test_get_site_vo_images(self):
        with mock.patch.object(site_store, "get_site_by_goc_id") as m_get_site:
            m_get_site.return_value = site_fixture
            response = self.client.get("/site/foo/ops/images/")
            assert response.status_code == 200
            assert response.json() == [
                {
                    "appdb_id": "egi.small.ubuntu.16.04.for.monitoring",
                    "id": "06c8bfac-0f93-48da-b0eb-4fbad3356f73",
                    "mpuri": "https://appdb.egi.eu/store/vo/image/63fcad1c-b737-5091-9668-1342b6d4f84c:15705/",
                    "name": "EGI Small Ubuntu for Monitoring",
                    "version": "2024.11.18",
                },
            ]

    def test_get_site_projects(self):
        with mock.patch.object(site_store, "get_site_by_goc_id") as m_get_site:
            m_get_site.return_value = site_fixture
            response = self.client.get("/site/foo/projects/")
            assert response.status_code == 200
            assert response.json() == [
                {
                    "id": "038db3eeca5c4960a443a89b92373cd2",
                    "name": "ops",
                }
            ]

    def test_get_site_vo_project(self):
        with mock.patch.object(site_store, "get_site_by_goc_id") as m_get_site:
            m_get_site.return_value = site_fixture
            response = self.client.get("/site/foo/ops/project")
            assert response.status_code == 200
            assert response.json() == {
                "id": "038db3eeca5c4960a443a89b92373cd2",
                "name": "ops",
            }
