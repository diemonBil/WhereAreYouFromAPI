# 🌍 WhereAreYouFromAPI

A Django REST API that predicts the origin countries for a given name using [Nationalize.io](https://api.nationalize.io) and enriches the country data from [REST Countries](https://restcountries.com/).

## 📦 Features

* `/api/v1/names/?name=John` – Get probable countries by name. Additional country metadata is stored internally (e.g., flags, capital, borders).
* `/api/v1/popular-names/?country=US` – Get top 5 most common names requested for a specific country
* 🧠 Caching: avoids redundant API calls within 24h
* 🔒 JWT Authentication (all endpoints require it)
* 🧪 Unit tests included (using DRF test client)
* 🐋 Docker + Docker Compose ready
* 📄 Swagger/OpenAPI docs at `/api/v1/docs/`

## 🚀 Getting Started

### 1. Clone & setup environment

```bash
git clone https://github.com/diemonBil/WhereAreYouFromAPI.git
cd WhereAreYouFromAPI
cp .env.example .env  # Add DB connection & secret
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

The app will be available at: `http://localhost:8000`

## 🔐 Authentication

All endpoints require JWT:

1. Obtain token via `/api/token/` using registered credentials
2. Use `Authorization: Bearer <token>` header in requests

## Example Usage

```bash
curl -H "Authorization: Bearer <token>" "http://localhost:8000/api/v1/names/?name=Maria"
```

Response:

```json
{
    "name": "Maria",
    "countries": [
        {
            "code": "RO",
            "name": "Romania",
            "probability": 0.1576
        },
        {
            "code": "BR",
            "name": "Brazil",
            "probability": 0.0684
        },
        {
            "code": "PT",
            "name": "Portugal",
            "probability": 0.0431
        },
        {
            "code": "AO",
            "name": "Angola",
            "probability": 0.0308
        },
        {
            "code": "GR",
            "name": "Greece",
            "probability": 0.029
        }
    ]
}
```

## 🗃️ Technologies

* Python 3.11
* Django + DRF
* PostgreSQL
* JWT (djangorestframework-simplejwt)
* Swagger via `drf-spectacular`
* Docker, docker-compose
* `.env` support via `python-dotenv`

## 📁 Project Structure

```
├── name_origin/                  # Django app with views, serializers, models
├── WhereAreYouFromAPI/           # Main Django project configuration 
                                   (settings, URLs, WSGI/ASGI entry points)
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── .dockerignore
├── .env
└── README.md
```
