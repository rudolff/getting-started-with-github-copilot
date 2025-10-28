from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_root():
    """Test the root endpoint redirects to static/index.html"""
    response = client.get("/")
    assert response.status_code in [200, 307]  # Either direct response or redirect
    if response.status_code == 307:  # If it's a redirect
        assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities

def test_signup_success():
    """Test successful activity signup"""
    activity_name = "Basketball Team"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity_name}"

    # Verify the student was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate():
    """Test signing up a student who is already registered"""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already registered in this activity
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up for this activity"

def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    activity_name = "Non Existent Club"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_unregister_success():
    """Test successful unregistration from an activity"""
    # First register a student
    activity_name = "Science Club"
    email = "test@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Then unregister them
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Unregistered {email} from {activity_name}"

    # Verify the student was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    """Test unregistering a student who is not registered"""
    activity_name = "Drama Club"
    email = "notregistered@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student is not registered for this activity"

def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    activity_name = "Non Existent Club"
    email = "test@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"