from django.conf import settings
from django.test import TestCase
from user_management.models import User


class DjangoClientWithDB(TestCase):
    def setUp(self):
        # Set up test database in memory
        settings.DATABASES["test"]["ENGINE"] = "django.db.backends.sqlite3"
        settings.DATABASES["test"]["test_lcl_backend"] = ":memory:"

        # Create the schema for the test database
        from django.core.management import call_command

        call_command("migrate")

        # Create a Test User
        self.user = User.objects.create_user(
            username="testuser",
            email="test@yopmail.com",
            password="test1234",
        )

        # Test if user data is saved in Model
        self.assertEqual(self.user.email, "test@yopmail.com")

        # Login User to Create Access Token
        response = self.client.post(
            "/login",
            {"email": "test@yopmail.com", "password": "test1234"},
            content_type="application/json",
        ).json()

        # Grab Access Token
        access_token = response.get("data").get("token")

        # Verify and Assign token
        self.assertFalse(len(access_token) < 5)
        self.token = "Bearer " + access_token

    def tearDown(self):
        # Destroy the test database after each test
        del settings.DATABASES["test"]["test_lcl_backend"]
