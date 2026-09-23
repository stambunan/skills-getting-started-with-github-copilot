from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_root_redirects_to_static_page():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_known_activity():
    # Arrange
    activity_name = "Chess Club"
    expected_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert activity_name in activities
    assert expected_fields <= activities[activity_name].keys()


def test_signup_and_unregister_activity():
    # Arrange
    activity_name = "Art Club"
    email = "pytest-student@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup"
    unregister_url = f"/activities/{activity_name}/participants/{email}"
    signup_completed = False

    # Act
    signup_response = client.post(signup_url, params={"email": email})
    signup_completed = signup_response.status_code == 200

    try:
        # Assert
        assert signup_response.status_code == 200
        assert signup_response.json() == {
            "message": f"Signed up {email} for {activity_name}"
        }

        # Arrange
        expected_message = f"Unregistered {email} from {activity_name}"

        # Act
        unregister_response = client.delete(unregister_url)

        # Assert
        assert unregister_response.status_code == 200
        assert unregister_response.json() == {"message": expected_message}
        signup_completed = False
    finally:
        if signup_completed:
            client.delete(unregister_url)