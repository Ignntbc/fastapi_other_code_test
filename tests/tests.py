from fastapi.testclient import TestClient

from main import app  

client = TestClient(app)

def test_read_article():
    response = client.get("/articles/1")
    assert response.status_code == 200
    assert "title" in response.json()
    assert "content" in response.json()



def test_read_articles():
    response = client.get("/articles/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_article():
    response = client.post("/articles/", json={
        "title": "Test Article",
        "content": "This is a test article",
        "author_id": 1,
        "published_date": "2022-01-01"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Test Article"