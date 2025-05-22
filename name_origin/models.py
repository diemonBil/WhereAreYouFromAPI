from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Name(models.Model):
    value = models.CharField(max_length=100)
    count_of_requests = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(
        auto_now=True
    )  # Automatically updated each time the record is saved


class Country(models.Model):
    code = models.CharField(max_length=2, unique=True)  # Example: "US"
    alpha3 = models.CharField(max_length=3, blank=True)
    name = models.CharField(max_length=100)  # Example: "United States"
    official_name = models.CharField(max_length=150, blank=True, null=True)
    region = models.CharField(
        max_length=100, blank=True, null=True
    )  # Example: "Americas"
    independent = models.BooleanField(null=True)
    capital = models.CharField(max_length=100, blank=True, null=True)
    capital_lat = models.FloatField(
        blank=True, null=True
    )  # Latitude of the capital city
    capital_lng = models.FloatField(
        blank=True, null=True
    )  # Longitude of the capital city
    google_maps_url = models.URLField(blank=True, null=True)
    openstreetmap_url = models.URLField(blank=True, null=True)
    flag_png = models.URLField(blank=True, null=True)
    flag_svg = models.URLField(blank=True, null=True)
    flag_alt = models.TextField(blank=True, null=True)
    coat_of_arms_png = models.URLField(blank=True, null=True)
    coat_of_arms_svg = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class CountryBorder(models.Model):
    from_country = models.ForeignKey(
        "Country", on_delete=models.CASCADE, related_name="borders_from"
    )
    to_country = models.ForeignKey(
        "Country", on_delete=models.CASCADE, related_name="borders_to"
    )

    class Meta:
        # Ensure that each country pair is unique
        unique_together = ("from_country", "to_country")

    def save(self, *args, **kwargs):
        # Compare by alphabetical order of country codes
        if self.from_country.code > self.to_country.code:
            self.from_country, self.to_country = self.to_country, self.from_country
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.from_country.code} ↔ {self.to_country.code}"  # Use symmetric arrow to reflect bidirectional border


class NameCountryStat(models.Model):
    name = models.ForeignKey(
        Name, on_delete=models.CASCADE, related_name="country_stats"
    )
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="name_stats"
    )
    probability = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0),
        ]  # Restrict values to range 0.0–1.0
    )

    class Meta:
        # Ensure only one record exists per name-country pair
        unique_together = ("name", "country")

    def __str__(self):
        return f"{self.name.value} → {self.country.code} (prob: {self.probability})"
