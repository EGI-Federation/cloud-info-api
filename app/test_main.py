"""Testing our glue component"""

from unittest import mock

import pytest
from app.glue import VO, Discipline
from app.main import _get_site, app, site_store, vo_store
from fastapi import HTTPException
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_vos():
    with mock.patch.object(vo_store, "get_vos") as m_get_vos:
        m_get_vos.return_value = [
            VO(serial=1, name="foo"),
            VO(serial=2, name="bar"),
        ]
        response = client.get("/vos/")
        assert response.status_code == 200
        assert response.json() == ["bar", "foo"]


def test_get_disciplines(discipline):
    with mock.patch.object(vo_store, "get_disciplines") as m_get_disciplines:
        m_get_disciplines.return_value = [Discipline(**discipline)]
        response = client.get("/disciplines/")
        assert response.status_code == 200
        assert response.json() == [discipline]


def test_get_sites_summary(site):
    with mock.patch.object(site_store, "get_sites") as m_get_sites:
        m_get_sites.return_value = [site]
        response = client.get("/sites/", params={"include_projects": "true"})
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": "12249G0",
                "name": "BIFI",
                "url": "https://colossus.cesar.unizar.es:5000/v3",
                "state": "",
                "hostname": "foo",
                "projects": [{"id": "038db3eeca5c4960a443a89b92373cd2", "name": "ops"}],
            }
        ]
        m_get_sites.assert_called()


def test_get_sites_no_name(site, bifi_summary):
    with mock.patch.object(site_store, "get_sites") as m_get_sites:
        m_get_sites.return_value = [site]
        response = client.get("/sites/", params={"vo_name": "foo"})
        assert response.status_code == 200
        assert response.json() == [bifi_summary]


def test_get_sites_with_name(site, bifi_summary):
    with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
        m_get_site.return_value = site
        # no VO
        response = client.get("/sites/", params={"site_name": "BIFI"})
        assert response.status_code == 200
        assert response.json() == [bifi_summary]
        m_get_site.assert_called_with("BIFI")
        # unsupported VO
        m_get_site.return_value = site
        response = client.get("/sites/", params={"vo_name": "foo", "site_name": "BIFI"})
        assert response.status_code == 200
        assert response.json() == []
        m_get_site.assert_called_with("BIFI")
        # supported VO
        m_get_site.return_value = site
        response = client.get("/sites/", params={"vo_name": "ops", "site_name": "BIFI"})
        assert response.status_code == 200
        assert response.json() == [bifi_summary]
        m_get_site.assert_called_with("BIFI")


def test__get_site(site):
    with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
        m_get_site.return_value = site
        s = _get_site("foo")
        assert s == site
        # supported VO
        s = _get_site("foo", "ops")
        assert s == site
        # unsupported VO
        with pytest.raises(HTTPException):
            _get_site("foo", "bar")


def test__get_site_not_found():
    with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
        m_get_site.return_value = None
        with pytest.raises(HTTPException):
            _get_site("foo")


def test_get_site(site, bifi_summary):
    with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
        m_get_site.return_value = site
        response = client.get("/site/foo/")
        assert response.status_code == 200
        assert response.json() == bifi_summary


def test_get_site_404():
    with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
        m_get_site.return_value = None
        response = client.get("/site/foo/")
        assert response.status_code == 404


def test_get_site_images(site, images):
    with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
        m_get_site.return_value = site
        response = client.get("/site/foo/images/")
        assert response.status_code == 200
        assert response.json() == [images[0]]


def test_get_site_vo_images(site, images):
    with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
        m_get_site.return_value = site
        response = client.get("/site/foo/ops/images/")
        assert response.status_code == 200
        assert response.json() == [images[0]]


def test_get_site_projects(site):
    with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
        m_get_site.return_value = site
        response = client.get("/site/foo/projects/")
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": "038db3eeca5c4960a443a89b92373cd2",
                "name": "ops",
            }
        ]


def test_get_site_vo_project(site):
    with mock.patch.object(site_store, "get_site_by_name") as m_get_site:
        m_get_site.return_value = site
        response = client.get("/site/foo/ops/project")
        assert response.status_code == 200
        assert response.json() == {
            "id": "038db3eeca5c4960a443a89b92373cd2",
            "name": "ops",
        }


def test_get_all_images(site, another_site, images):
    with mock.patch.object(site_store, "get_sites") as m_get_sites:
        m_get_sites.return_value = [site, another_site]
        response = client.get("/images")
        assert response.status_code == 200
        assert response.json() == images


def test_get_all_vo_images(site, images):
    with mock.patch.object(site_store, "get_sites") as m_get_sites:
        m_get_sites.return_value = [site]
        response = client.get("/images", params={"vo_name": "ops"})
        assert response.status_code == 200
        assert response.json() == [images[0]]


def test_get_images_non_egi(site, another_site, more_images):
    with mock.patch.object(site_store, "get_sites") as m_get_sites:
        m_get_sites.return_value = [site, another_site]
        response = client.get("/images", params={"only_egi_images": False})
        assert response.status_code == 200
        assert response.json() == more_images
