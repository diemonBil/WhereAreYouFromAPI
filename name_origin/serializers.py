from rest_framework import serializers
from .models import Country, NameCountryStat


# Serializes full Country model with all metadata fields
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            "code",
            "name",
            "official_name",
            "region",
            "independent",
            "capital",
            "capital_lat",
            "capital_lng",
            "google_maps_url",
            "openstreetmap_url",
            "flag_png",
            "flag_svg",
            "flag_alt",
            "coat_of_arms_png",
            "coat_of_arms_svg",
        ]


# Serializes NameCountryStat including:
# - country as a nested object (using CountrySerializer)
# - name as plain string (via source='name.value')
class NameCountryStatSerializer(serializers.ModelSerializer):
    country = CountrySerializer()  # Embed full country info
    name = serializers.CharField(source="name.value")  # Just return the name string

    class Meta:
        model = NameCountryStat
        fields = ["name", "country", "probability"]


# A lightweight version of the NameCountryStatSerializer for compact responses.
# Returns only: country code, name, and rounded probability.
class CompactCountryStatSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="country.code")
    name = serializers.CharField(source="country.name")
    probability = serializers.SerializerMethodField()

    class Meta:
        model = NameCountryStat
        fields = ["code", "name", "probability"]

    def get_probability(self, obj):
        return round(obj.probability, 4)
