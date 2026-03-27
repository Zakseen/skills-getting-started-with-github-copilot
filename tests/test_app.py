import copy

from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    backup = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(copy.deepcopy(backup))


def test_root_redirect():
    response = client.get("/", allow_redirects=False)
    assert response.status_code in (301, 302, 307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_and_duplicate_error():
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}

    # duplicate signup should be rejected
    duplicate = client.post("/activities/Chess Club/signup", params={"email": email})
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_for_activity_and_error():
    existing_email = "michael@mergington.edu"
    response = client.delete("/activities/Chess Club/unregister", params={"email": existing_email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {existing_email} from Chess Club"}

    not_signed_up = client.delete("/activities/Chess Club/unregister", params={"email": "nobody@mergington.edu"})
    assert not_signed_up.status_code == 400
    assert not_signed_up.json()["detail"] == "Student is not signed up for this activity"
