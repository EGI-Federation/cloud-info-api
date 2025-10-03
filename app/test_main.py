"""Testing our glue component"""

from unittest import TestCase, mock

from app.glue import VO
from app.main import _get_site, app, site_store, vo_store
from app.test_fixtures import (
    another_site_fixture,
    disciplines,
    images_fixture,
    site_fixture,
)
from fastapi import HTTPException
from fastapi.testclient import TestClient

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

    def test_get_disciplines(self):
        with mock.patch("builtins.open", mock.mock_open(read_data=disciplines)):
            response = self.client.get("/disciplines/")
            assert response.status_code == 200
            assert response.json() == ["a", "b", "c"]

    def test_get_sites_summary(self):
        with mock.patch.object(site_store, "get_sites") as m_get_sites:
            m_get_sites.return_value = [site_fixture]
            response = self.client.get("/sites/", params={"include_projects": "true"})
            assert response.status_code == 200
            assert response.json() == [
                {
                    "id": "12249G0",
                    "name": "BIFI",
                    "url": "https://colossus.cesar.unizar.es:5000/v3",
                    "state": "",
                    "hostname": "foo",
                    "projects": [
                        {"id": "038db3eeca5c4960a443a89b92373cd2", "name": "ops"}
                    ],
                }
            ]
            m_get_sites.assert_called()

    def test_get_sites_no_name(self):
        with mock.patch.object(site_store, "get_sites") as m_get_sites:
            m_get_sites.return_value = [site_fixture]
            response = self.client.get("/sites/", params={"vo_name": "foo"})
            assert response.status_code == 200
            assert response.json() == [bifi_summary]

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
        with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
            m_get_site.return_value = site_fixture
            s = _get_site("foo")
            assert s == site_fixture
            # supported VO
            s = _get_site("foo", "ops")
            assert s == site_fixture
            # unsupported VO
            with self.assertRaises(HTTPException):
                _get_site("foo", "bar")

    def test__get_site_not_found(self):
        with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
            m_get_site.return_value = None
            with self.assertRaises(HTTPException):
                _get_site("foo")

    def test_get_site(self):
        with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
            m_get_site.return_value = site_fixture
            response = self.client.get("/site/foo/")
            assert response.status_code == 200
            assert response.json() == bifi_summary

    def test_get_site_404(self):
        with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
            m_get_site.return_value = None
            response = self.client.get("/site/foo/")
            assert response.status_code == 404

    def test_get_site_images(self):
        with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
            m_get_site.return_value = site_fixture
            response = self.client.get("/site/foo/images/")
            assert response.status_code == 200
            assert response.json() == [images_fixture[0]]

    def test_get_site_vo_images(self):
        with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
            m_get_site.return_value = site_fixture
            response = self.client.get("/site/foo/ops/images/")
            assert response.status_code == 200
            assert response.json() == [images_fixture[0]]

    def test_get_site_projects(self):
        with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
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
        with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
            m_get_site.return_value = site_fixture
            response = self.client.get("/site/foo/ops/project")
            assert response.status_code == 200
            assert response.json() == {
                "id": "038db3eeca5c4960a443a89b92373cd2",
                "name": "ops",
            }

    def test_get_all_images(self):
        with mock.patch.object(site_store, "get_sites") as m_get_sites:
            m_get_sites.return_value = [site_fixture, another_site_fixture]
            response = self.client.get("/images")
            assert response.status_code == 200
            assert response.json() == images_fixture

    def test_get_all_vo_images(self):
        with mock.patch.object(site_store, "get_sites") as m_get_sites:
            m_get_sites.return_value = [site_fixture]
            response = self.client.get("/images", params={"vo_name": "ops"})
            assert response.status_code == 200
            assert response.json() == [images_fixture[0]]

    def test_get_images_non_egi(self):
        with mock.patch.object(site_store, "get_sites") as m_get_sites:
            m_get_sites.return_value = [site_fixture, another_site_fixture]
            response = self.client.get("/images", params={"only_egi_images": False})
            assert response.status_code == 200
            images = images_fixture.copy()
            images.append(
                {
                    "egi_id": "",
                    "endpoint": "https://example.com/v3",
                    "id": "foobar",
                    "mpuri": "https://example.com/glance/vo/image/foobar",
                    "name": "Another fake Image",
                    "version": "0.02",
                    "vo": "access",
                }
            )
            assert response.json() == images
