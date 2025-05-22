from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from name_origin.models import Country, Name, NameCountryStat


class NameStatsViewTest(APITestCase):
    def setUp(self):
        # Create user and generate JWT token
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        # Pre-create a country
        self.country = Country.objects.create(
            code="US", name="United States", alpha3="USA"
        )

        # Pre-create a name with a recent timestamp to test cache
        self.name = Name.objects.create(value="John", count_of_requests=2)
        NameCountryStat.objects.create(
            name=self.name, country=self.country, probability=0.75
        )

    def test_missing_name_param(self):
        # Should return 400 if no name is provided
        response = self.client.get("/api/v1/names/", **self.auth_headers)
        self.assertEqual(response.status_code, 400)

    def test_cached_name_returns_data(self):
        # Should return stored data from DB for a recently accessed name
        response = self.client.get("/api/v1/names/?name=John", **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "John")
        self.assertIn("countries", response.data)

    def test_name_triggers_api_call(self):
        # Should trigger external API call for a new name
        response = self.client.get("/api/v1/names/?name=Maria", **self.auth_headers)
        self.assertIn(response.status_code, [200, 404])  # Accept if no country found

    def test_unauthorized_request(self):
        # Should return 401 for unauthenticated request
        response = self.client.get("/api/v1/names/?name=John")
        self.assertEqual(response.status_code, 401)


class PopularNamesViewTest(APITestCase):
    def setUp(self):
        # Create user and JWT token
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        # Create test data
        self.country = Country.objects.create(
            code="US", name="United States", alpha3="USA"
        )
        name1 = Name.objects.create(value="John", count_of_requests=50)
        name2 = Name.objects.create(value="Mike", count_of_requests=30)
        NameCountryStat.objects.create(
            name=name1, country=self.country, probability=0.85
        )
        NameCountryStat.objects.create(
            name=name2, country=self.country, probability=0.55
        )

    def test_popular_names_success(self):
        # Should return top 5 names sorted by probability
        response = self.client.get(
            "/api/v1/popular-names/?country=US", **self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("top_names", response.data)
        self.assertEqual(len(response.data["top_names"]), 2)
        self.assertEqual(response.data["top_names"][0]["name"], "John")

    def test_missing_country_param(self):
        # Should return 400 if country code is not provided
        response = self.client.get("/api/v1/popular-names/", **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_country(self):
        # Should return 404 if country code not found in DB
        response = self.client.get(
            "/api/v1/popular-names/?country=ZZ", **self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access(self):
        # Should return 401 for unauthenticated request
        response = self.client.get("/api/v1/popular-names/?country=US")
        self.assertEqual(response.status_code, 401)
