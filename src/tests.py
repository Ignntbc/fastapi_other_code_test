from fastapi.testclient import TestClient
import pytest
from main import app
from config import TEST_USERNAME, TEST_PASSWORD
from db.db import DatabaseManager,TestDatabaseManager

# test_db_manager = DatabaseManager(test_mode=True)
def override_db_manager():
    return DatabaseManager(test_mode=True) 

app.dependency_overrides[DatabaseManager] = override_db_manager
client = TestClient(app)


@pytest.fixture(scope="module")
def access_token():

    test_username = TEST_USERNAME
    test_password = TEST_PASSWORD

    response = client.post("auth/token", json={"username": test_username, "password": test_password})

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

    return response.json()["access_token"]


def test_login_for_access_token_invalid_credentials():
    response = client.post("auth/token", data={"username": "invalid", "password": "invalid"})
    assert response.status_code == 422


def test_read_article():
    test_article_id = 1
    response = client.get(f"/articles/{test_article_id}")

    assert response.status_code == 200
    assert "id" in response.json()
    assert "title" in response.json()
    assert "content" in response.json()
    assert "author_id" in response.json()
    assert response.json()["id"] == test_article_id

def test_read_article_not_found():
    response = client.get("/articles/-1")
    assert response.status_code == 404

def test_create_article(access_token):
    test_article_data = {
"title" :"Article TEST ARTICLE",
"content":"This is the content of the test article.",
"author_id": 2,
"published_date": "2022-01-09"
}
    response = client.post("/articles", json=test_article_data, headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert "id" in response.json()
    assert "title" in response.json()
    assert "content" in response.json()
    assert "author_id" in response.json()
    assert "published_date" in response.json()

    assert response.json()["title"] == test_article_data["title"]
    assert response.json()["content"] == test_article_data["content"]
    assert response.json()["published_date"] == test_article_data["published_date"]

def test_create_article_without_authentication():
    response = client.post("/articles/", json={"title": "Test Article", "content": "Test Content", "author_id": 1})
    assert response.status_code == 401  
    assert response.json() == {"detail": "Not authenticated"}

def test_create_article_with_invalid_data(access_token):
    response = client.post("/articles/", json={"title": "", "content": ""}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", None),
        ("content", None),
        ("author_id", None),
        ("title", 0),
        ("content", -6),
        ("author_id", ""),
    ],
)
def test_create_article_with_missing_field(field, value, access_token):
    data = {"title": "Test Article", "content": "Test Content", "author_id": 1}
    data[field] = value
    response = client.post("/articles/", json=data, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 422
    assert "detail" in response.json()

