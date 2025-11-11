"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

# Create a test client
client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that response contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Basketball Club",
            "Art Club",
            "Drama Club",
            "Science Club",
            "Debate Team"
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity {activity_name} missing {field}"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_duplicate_email_fails(self):
        """Test that duplicate signup returns 400 error"""
        email = "test_duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity_fails(self):
        """Test that signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_adds_participant_to_activity(self):
        """Test that signup actually adds participant to activity"""
        email = "verify_signup@mergington.edu"
        activity_name = "Drama Club"
        
        # Get activities before signup
        response_before = client.get("/activities")
        participants_before = response_before.json()[activity_name]["participants"]
        
        # Signup
        response_signup = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response_signup.status_code == 200
        
        # Get activities after signup
        response_after = client.get("/activities")
        participants_after = response_after.json()[activity_name]["participants"]
        
        # Verify participant was added
        assert len(participants_after) == len(participants_before) + 1
        assert email in participants_after


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self):
        """Test successful unregister from an activity"""
        email = "test_unregister@mergington.edu"
        activity_name = "Science Club"
        
        # First signup
        response_signup = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response_signup.status_code == 200
        
        # Then unregister
        response_unregister = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response_unregister.status_code == 200
        assert "Unregistered" in response_unregister.json()["message"]

    def test_unregister_nonexistent_activity_fails(self):
        """Test that unregister from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_not_registered_participant_fails(self):
        """Test that unregister of non-registered participant returns 400"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "not_registered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_removes_participant_from_activity(self):
        """Test that unregister actually removes participant from activity"""
        email = "verify_unregister@mergington.edu"
        activity_name = "Basketball Club"
        
        # Signup
        response_signup = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response_signup.status_code == 200
        
        # Get activities after signup
        response_after_signup = client.get("/activities")
        participants_after_signup = response_after_signup.json()[activity_name]["participants"]
        assert email in participants_after_signup
        
        # Unregister
        response_unregister = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response_unregister.status_code == 200
        
        # Get activities after unregister
        response_after_unregister = client.get("/activities")
        participants_after_unregister = response_after_unregister.json()[activity_name]["participants"]
        
        # Verify participant was removed
        assert email not in participants_after_unregister
        assert len(participants_after_unregister) == len(participants_after_signup) - 1


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static(self):
        """Test that GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
