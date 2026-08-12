"""Integration tests for complete workflows using AAA pattern."""

import pytest


class TestWorkflows:
    """Tests for complete user workflows."""
    
    def test_signup_workflow_then_verify_in_list(self, client, fresh_activities):
        """
        ARRANGE: Fresh activities loaded, new student email ready
        ACT: 1) GET /activities, 2) POST signup, 3) GET /activities again
        ASSERT: Student appears in participants list after signup
        """
        # ARRANGE
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # ACT - Step 1: Get initial state
        response_initial = client.get("/activities")
        initial_participants = response_initial.json()[activity_name]["participants"]
        assert email not in initial_participants
        
        # ACT - Step 2: Sign up
        response_signup = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response_signup.status_code == 200
        
        # ACT - Step 3: Get updated state
        response_updated = client.get("/activities")
        updated_participants = response_updated.json()[activity_name]["participants"]
        
        # ASSERT
        assert email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1
    
    def test_signup_then_remove_participant(self, client, fresh_activities):
        """
        ARRANGE: Fresh activities loaded
        ACT: 1) Sign up new student, 2) Remove that student
        ASSERT: Participant count returns to original
        """
        # ARRANGE
        email = "newstudent@mergington.edu"
        activity_name = "Programming Class"
        
        # Get initial count
        response_initial = client.get("/activities")
        initial_count = len(response_initial.json()[activity_name]["participants"])
        
        # ACT - Step 1: Sign up
        response_signup = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response_signup.status_code == 200
        
        # Verify signup worked
        response_after_signup = client.get("/activities")
        count_after_signup = len(response_after_signup.json()[activity_name]["participants"])
        assert count_after_signup == initial_count + 1
        
        # ACT - Step 2: Remove the participant
        response_remove = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        assert response_remove.status_code == 200
        
        # ACT - Step 3: Verify removal
        response_final = client.get("/activities")
        final_count = len(response_final.json()[activity_name]["participants"])
        
        # ASSERT
        assert final_count == initial_count
        assert email not in response_final.json()[activity_name]["participants"]
    
    def test_multiple_signups_for_different_activities(self, client, fresh_activities):
        """
        ARRANGE: Fresh activities, one student ready
        ACT: Sign up same student for multiple different activities
        ASSERT: Student appears in all activities
        """
        # ARRANGE
        email = "multi@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Gym Class"]
        
        # ACT: Sign up for multiple activities
        for activity_name in activities_to_join:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # ACT: Verify presence in all
        response_final = client.get("/activities")
        data = response_final.json()
        
        # ASSERT
        for activity_name in activities_to_join:
            assert email in data[activity_name]["participants"]
    
    def test_participant_capacity_tracking(self, client, fresh_activities):
        """
        ARRANGE: Gym Class has 2 participants and max 30
        ACT: Sign up multiple students
        ASSERT: Participant count increases accurately
        """
        # ARRANGE
        activity_name = "Gym Class"
        new_students = [
            "alice@mergington.edu",
            "bob@mergington.edu",
            "charlie@mergington.edu"
        ]
        
        # Get initial count
        response_initial = client.get("/activities")
        initial_count = len(response_initial.json()[activity_name]["participants"])
        
        # ACT: Sign up multiple students
        for email in new_students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # ACT: Check final count
        response_final = client.get("/activities")
        final_activity = response_final.json()[activity_name]
        final_count = len(final_activity["participants"])
        
        # ASSERT
        assert final_count == initial_count + len(new_students)
        for email in new_students:
            assert email in final_activity["participants"]
    
    def test_cannot_signup_twice_same_activity(self, client, fresh_activities):
        """
        ARRANGE: Student ready to sign up
        ACT: 1) First signup, 2) Attempt second signup for same activity
        ASSERT: Second attempt returns 400 error
        """
        # ARRANGE
        email = "student@mergington.edu"
        activity_name = "Chess Club"
        
        # ACT - Step 1: First signup succeeds
        response_first = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response_first.status_code == 200
        
        # ACT - Step 2: Second signup fails
        response_second = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response_second.status_code == 400
        assert "already signed up" in response_second.json()["detail"].lower()
