"""Unit tests for API endpoints using AAA (Arrange-Act-Assert) pattern."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, fresh_activities):
        """
        ARRANGE: Fresh activities are loaded
        ACT: GET /activities
        ASSERT: Returns 200 and all activities with correct structure
        """
        # ARRANGE is done by fixtures
        
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_has_required_fields(self, client, fresh_activities):
        """
        ARRANGE: Fresh activities are loaded
        ACT: GET /activities
        ASSERT: Each activity has required fields
        """
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)
    
    def test_get_activities_participants_count(self, client, fresh_activities):
        """
        ARRANGE: Chess Club has 2 participants
        ACT: GET /activities
        ASSERT: Participants list matches expected count
        """
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestRoot:
    """Tests for GET / endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """
        ARRANGE: TestClient follows redirects by default
        ACT: GET /
        ASSERT: Returns 200 with HTML content
        """
        # ACT
        response = client.get("/", follow_redirects=True)
        
        # ASSERT
        assert response.status_code == 200
        # Should contain HTML content from index.html
        assert "<!DOCTYPE html" in response.text.lower() or "extracurricular" in response.text.lower()


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, fresh_activities):
        """
        ARRANGE: Fresh activities loaded, new email ready
        ACT: POST signup for Chess Club
        ASSERT: Returns 200 and participant is added
        """
        # ARRANGE
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in fresh_activities[activity_name]["participants"]
    
    def test_signup_duplicate_returns_400(self, client, fresh_activities):
        """
        ARRANGE: michael@mergington.edu already in Chess Club
        ACT: POST signup with same email
        ASSERT: Returns 400 error
        """
        # ARRANGE
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_nonexistent_activity_returns_404(self, client, fresh_activities):
        """
        ARRANGE: Activity doesn't exist
        ACT: POST signup for non-existent activity
        ASSERT: Returns 404 error
        """
        # ARRANGE
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_updates_participant_count(self, client, fresh_activities):
        """
        ARRANGE: Programming Class has 2 participants
        ACT: POST signup for Programming Class
        ASSERT: Participant count increases to 3
        """
        # ARRANGE
        email = "newstudent@mergington.edu"
        activity_name = "Programming Class"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert len(fresh_activities[activity_name]["participants"]) == initial_count + 1


class TestRemove:
    """Tests for DELETE /activities/{activity_name}/remove endpoint."""
    
    def test_remove_success(self, client, fresh_activities):
        """
        ARRANGE: michael@mergington.edu in Chess Club
        ACT: DELETE remove participant
        ASSERT: Returns 200 and participant is removed
        """
        # ARRANGE
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email not in fresh_activities[activity_name]["participants"]
    
    def test_remove_nonexistent_participant_returns_400(self, client, fresh_activities):
        """
        ARRANGE: Student not in Chess Club
        ACT: DELETE remove non-existent participant
        ASSERT: Returns 400 error
        """
        # ARRANGE
        email = "nonexistent@mergington.edu"
        activity_name = "Chess Club"
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_remove_nonexistent_activity_returns_404(self, client, fresh_activities):
        """
        ARRANGE: Activity doesn't exist
        ACT: DELETE remove from non-existent activity
        ASSERT: Returns 404 error
        """
        # ARRANGE
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_updates_participant_count(self, client, fresh_activities):
        """
        ARRANGE: Chess Club has 2 participants
        ACT: DELETE remove one participant
        ASSERT: Participant count decreases to 1
        """
        # ARRANGE
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert len(fresh_activities[activity_name]["participants"]) == initial_count - 1
