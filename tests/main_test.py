# encoding=utf8

import pytest
import json
import subprocess

import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from urllib import parse
from fastapi import status as fastapi_status
from fastapi.testclient import TestClient
from main import app

# from db.methods import update_user
# from db.database import SessionLocal

from pathlib import Path

client = TestClient(app)
AUTHORIZATION = "dG6Soif%K0odbM2w27zC2Lzoq#1USOl9mkVssg#&jRk!kOWJp^"
USERID = 242306128


def deep_sort_children(node):
    if node.get("children"):
        node["children"].sort(key=lambda x: x["id"])

        for child in node["children"]:
            deep_sort_children(child)


def print_diff(expected, response):
    parent_path = Path(__file__).parent.parent
    with open(parent_path / "expected.json", "w") as f:
        json.dump(expected, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    with open(parent_path / "response.json", "w") as f:
        json.dump(response, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    subprocess.run(["git", "--no-pager", "diff", "--no-index",
                    "expected.json", "response.json"])


def request(url: str, method: str = "GET", json_data=None, json_response=True):
    headers = {"Authorization": AUTHORIZATION}
    response = client.request(method=method, url=url, json=json_data, headers=headers)
    return response.status_code, response.json() if json_response else response


def test_get_me():
    status, data = request("/users/me", method="GET")
    result = {
        "id": 242306128,
        "role": 0,
        "rubles": 0,
        "first_name": "Александр",
        "last_name": "Бульбенков",
    }

    assert 'avatar' in data and data['avatar'] != None
    del data['avatar']
    del data['city']

    assert data == result, print_diff(result, data)
    assert status == fastapi_status.HTTP_200_OK, f"Expected HTTP status code 200, got {status}"


def test_set_city():
    status, data = request("/users/set_city?city_id=1", method="POST")
    result = {"name": "Тула", "id": 1}

    assert data.get("city", {}) == result, print_diff(data.get("city", {}), result)


def test_access_denied():
    status, data = request("/users/set_role", method="POST", json_data={"user_id": 1, "role": 0})
    assert status == 403


def test_upload_photo():
    pass


def test_create_organisation():
    pass


def test_delete_organisation():
    pass


if __name__ == '__main__':
    pytest.main()
