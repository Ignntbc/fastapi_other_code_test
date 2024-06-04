from fastapi.testclient import TestClient
import pytest
from main import app
from config import TEST_USERNAME, TEST_PASSWORD
from db.db import DatabaseManager


def override_db_manager():
    """Функция для переопределения зависимости DatabaseManager в тестах"""
    return DatabaseManager(test_mode=True) 

app.dependency_overrides[DatabaseManager] = override_db_manager
client = TestClient(app)


@pytest.fixture(scope="module")
def access_token():
    """Функция для получения токена доступа"""

    test_username = TEST_USERNAME
    test_password = TEST_PASSWORD

    response = client.post("auth/token", json={"username": test_username, "password": test_password})

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

    return response.json()["access_token"]


def test_login_for_access_token_invalid_credentials():
    """Тест для проверки аутентификации с неверными учетными данными"""

    response = client.post("auth/token", data={"username": "invalid", "password": "invalid"})
    assert response.status_code == 422


def test_read_article():
    """Тест для проверки получения статьи по id"""

    test_article_id = 1
    response = client.get(f"/articles/{test_article_id}")

    assert response.status_code == 200
    assert "id" in response.json()
    assert "title" in response.json()
    assert "content" in response.json()
    assert "author_id" in response.json()
    assert response.json()["id"] == test_article_id

def test_read_article_not_found():
    """Тест для проверки получения несуществующей статьи"""

    response = client.get("/articles/-1")
    assert response.status_code == 404

def test_create_article(access_token):
    """Тест для создания статьи"""

    test_article_data = {
"title" :"Article TEST ARTICLE",
"content":"This is the content of the test article.",
"author_id": 2,
"published_date": "2024-01-09"
}
    response = client.post("/articles", json=test_article_data,
                        headers={"Authorization": f"Bearer {access_token}"})

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
    """Тест для создания статьи без аутентификации"""

    response = client.post("/articles/", json={"title": "Test Article",
                                            "content": "Test Content", "author_id": 1})
    assert response.status_code == 401  
    assert response.json() == {"detail": "Not authenticated"}

def test_create_article_with_invalid_data(access_token):
    """Тест для создания статьи с неверными данными"""

    response = client.post("/articles/", json={"title": "", "content": ""},
                           headers={"Authorization": f"Bearer {access_token}"})
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
    """Тест для создания статьи с отсутствующими полями"""

    data = {"title": "Test Article", "content": "Test Content", "author_id": 1}
    data[field] = value
    response = client.post("/articles/", json=data,
                            headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 422
    assert "detail" in response.json()

def test_update_nonexistent_article(access_token):
    """Тест для обновления несуществующей статьи"""

    response = client.put("/articles/9999", json={
    "title": "Updated Title",
    "content": "Updated Content",
    "author_id": 1,
    "published_date": "2022-01-01"
}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 404

def test_update_article_as_author(access_token):
    """Тест для обновления статьи автором"""

    response = client.put(f"/articles/2", json={
    "title": "Updated Title",
    "content": "Updated Content",
    "author_id": 1,
    "published_date": "2022-01-01"
}, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["content"] == "Updated Content"

def test_read_articles_with_author_id_filter():
    """Тест для получения статей по id автора"""

    response = client.get("/articles?author_id=1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for article in response.json():
        assert article["author_id"] == 1


def test_read_articles_with_date_form_filter():
    """Тест для получения статей по дате публикации"""

    response = client.get("/articles?date_form=2024-01-01")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for article in response.json():
        assert article["published_date"] >= "2024-01-01"

def test_read_articles_with_pagination():
    """Тест для получения статей с пагинацией"""

    response = client.get("/articles?page=2&per_page=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 5