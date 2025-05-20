from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.timezone import now, timedelta
from rest_framework import status
import requests

from .models import Name, Country, NameCountryStat, CountryBorder
from .serializers import CompactCountryStatSerializer


class NameStatsView(APIView):
    def get(self, request):
        name_value = request.query_params.get('name')
        if not name_value:
            return Response({"error": "Query parameter 'name' is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if name already exists in DB
        try:
            name_obj = Name.objects.get(value=name_value)
            # If cached and fresh → use it
            if name_obj.last_accessed >= now() - timedelta(days=1):
                name_obj.count_of_requests += 1
                name_obj.save(update_fields=["count_of_requests", "last_accessed"])
                stats = NameCountryStat.objects.filter(name=name_obj)
                serialized = CompactCountryStatSerializer(stats, many=True)
                return Response({
                    "name": name_obj.value,
                    "countries": serialized.data
                })
        except Name.DoesNotExist:
            name_obj = None  # Mark as missing

        # Fetch prediction data from Nationalize.io
        response = requests.get(f"https://api.nationalize.io/?name={name_value}")
        data = response.json()

        if not data.get("country"):
            return Response(
                {"error": f"No countries found for name '{name_value}'."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create or retrieve the Name object
        name_obj, created = Name.objects.get_or_create(value=name_value)

        # Increment request counter and update access time
        name_obj.count_of_requests += 1
        name_obj.save(update_fields=["count_of_requests", "last_accessed"])

        for country_info in data["country"]:
            country_code = country_info["country_id"]

            # Fetch country metadata from restcountries.com (e.g. flags, region, borders)
            country_data = self.fetch_country_data(country_code)

            # Extract borders (list of ISO alpha-3 codes) and remove from dictionary
            # so we can pass the rest to defaults safely
            borders = country_data.pop("borders", [])

            # Create or retrieve the Country object using ISO alpha-2 code
            country, _ = Country.objects.get_or_create(
                code=country_code,
                defaults=country_data
            )

            # Save or update the probability for name–country pair
            NameCountryStat.objects.update_or_create(
                name=name_obj,
                country=country,
                defaults={"probability": country_info["probability"]}
            )

            # For each bordering country code (ISO alpha-3), find the matching country by alpha3 field
            for border_code in borders:
                try:
                    # Try to find the neighbor country using its alpha-3 code
                    neighbor = Country.objects.get(alpha3=border_code)
                except Country.DoesNotExist:
                    # If the country hasn't been created yet (e.g. not in any name result), skip it
                    continue

                # Always store borders in sorted order to prevent duplicate A–B and B–A records
                from_country, to_country = sorted([country, neighbor], key=lambda c: c.code)

                # Store borders only if they don't already exist (symmetrically)
                if not CountryBorder.objects.filter(from_country=from_country, to_country=to_country).exists():
                    CountryBorder.objects.create(from_country=from_country, to_country=to_country)

        # Return freshly collected name–country probabilities
        stats = NameCountryStat.objects.filter(name=name_obj)
        serialized = CompactCountryStatSerializer(stats, many=True)
        return Response({
            "name": name_obj.value,
            "countries": serialized.data
        })

    def fetch_country_data(self, code):
        url = f"https://restcountries.com/v3.1/alpha/{code}"
        r = requests.get(url)
        if not r.ok:
            return {}

        data = r.json()[0]

        return {
            # Extract key metadata for country creation
            "name": data.get("name", {}).get("common"),
            "official_name": data.get("name", {}).get("official"),
            "alpha3": data.get("cca3"),
            "region": data.get("region"),
            "independent": data.get("independent"),
            "capital": (data.get("capital") or [None])[0],
            "capital_lat": (data.get("capitalInfo", {}).get("latlng") or [None, None])[0],
            "capital_lng": (data.get("capitalInfo", {}).get("latlng") or [None, None])[1],
            "google_maps_url": data.get("maps", {}).get("googleMaps"),
            "openstreetmap_url": data.get("maps", {}).get("openStreetMaps"),
            "flag_png": data.get("flags", {}).get("png"),
            "flag_svg": data.get("flags", {}).get("svg"),
            "flag_alt": data.get("flags", {}).get("alt"),
            "coat_of_arms_png": data.get("coatOfArms", {}).get("png"),
            "coat_of_arms_svg": data.get("coatOfArms", {}).get("svg"),
            "borders": data.get("borders", [])
        }