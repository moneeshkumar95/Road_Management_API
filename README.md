# Road Network Management API

A FastAPI-based REST API for managing road networks with PostGIS integration. This system allows customers to upload, update, and retrieve road network data in GeoJSON format with versioning and authentication.

## Features

- **Multi-customer support** with token-based authentication
- **GeoJSON format** support for road network data
- **Versioning system** with historical data preservation
- **PostGIS integration** for efficient geospatial data storage
- **Docker containerization** for easy deployment
- **RESTful API** with comprehensive endpoints

## Architecture

### Tech Stack

- **API Framework**: FastAPI (asyncio)
- **Database**: PostgreSQL + PostGIS
- **ORM**: SQLModel (based on SQLAlchemy)
- **Auth**: JWT-based (admin/user roles)
- **Python Version**: 3.12
- **Package Manager**: Poetry
- **Containerized**: Docker + Docker Compose

### API Endpoints

1. **POST /api/v1/road-network**
   - Upload new road network from GeoJSON file
   - Requires authentication token
   - Creates network record and associated edges

2. **PUT /api/v1/road-network**
   - Update existing network with new version
   - Marks old edges as non-current (preserves history)
   - Increments version number

3. **GET /api/v1/road-network/edges**
   - Retrieve network edges in GeoJSON format
   - Supports version parameter for historical data
   - Returns only current customer's data

4. **GET /api/v1/road-network**
   - List all road networks for authenticated customer

5. **POST /api/v1/auth/login**
   - Login and get token

6. **POST /api/v1/auth/register**
   - Create new user (admin only)

7. **POST /api/v1/csutomers**
   - Create customer (admin only)

7. **GET /health**
   - Health check endpoint

## Authentication

JWT/OAuth2 based authentication is implemented for demo purposes. 


## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- GeoJSON files to upload

### Quick Start

1. **Clone and navigate to project directory**
```bash
git clone <repository>
cd road-network-api
```

2. **Start the services**
```bash
docker-compose up --build
```

3. **Verify services are running**
- API: http://localhost:8000
- Database: localhost:5434
- API Documentation: http://localhost:8000/docs

### Project Structure
```
.
├── docker-compose.yml
├── Dockerfile
├── geojson_samples
│   ├── road_network_aying_1.0.geojson
│   ├── road_network_bayrischzell_1.0.geojson
│   └── road_network_bayrischzell_1.1.geojson
├── init_scripts
│   └── init-db.sql
├── poetry.lock
├── pyproject.toml
├── README.md
└── src
    ├── apps
    │   ├── auth
    │   │   ├── api
    │   │   │   ├── __init__.py
    │   │   │   ├── login_api.py
    │   │   │   └── register_api.py
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── router.py
    │   │   ├── schemas.py
    │   │   └── utils.py
    │   ├── customer
    │   │   ├── api
    │   │   │   ├── create_customer_api.py
    │   │   │   └── __init__.py
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── router.py
    │   │   ├── schemas.py
    │   │   └── utils.py
    │   ├── __init__.py
    │   ├── road_network
    │   │   ├── api
    │   │   │   ├── __init__.py
    │   │   │   ├── create_road_network_api.py
    │   │   │   ├── get_road_network_edges_api.py
    │   │   │   ├── list_road_networks_api.py
    │   │   │   └── update_road_network_api.py
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── router.py
    │   │   ├── schemas.py
    │   │   └── utils.py
    │   ├── router_registry.py
    │   └── user
    │       ├── api
    │       │   └── __init__.py
    │       ├── __init__.py
    │       ├── models.py
    │       ├── router.py
    │       ├── schemas.py
    │       └── utils.py
    ├── custom_middleware.py
    ├── database.py
    ├── global_models.py
    ├── global_schemas.py
    ├── global_utils.py
    ├── __init__.py
    ├── logger.py
    ├── main.py
    ├── settings.py
    └── setup.py
```

## Usage Screenshots

### 1. Upload Initial Networks

**Upload Network 1 (Aying):**


**Upload Network 2 (Bayrischzell v1.0):**


### 2. Update Network

**Update Bayrischzell to v1.1:**


### 3. Retrieve Network Edges

**Get current version:**


### 4. List Networks


## Task Implementation Details

### Task 1: Upload and Store Networks
- RESTful endpoint for uploading GeoJSON files
- PostgreSQL with PostGIS for efficient geometry storage
- Customer-based authorization and data isolation
- Proper database schema with relationships

### Task 2: Update Networks with Versioning
- Update endpoint that preserves historical data
- Original edges marked as `is_active=false` (not deleted)
- Version increment logic (1.0 → 1.1)
- Proper transaction handling

### Task 3: Retrieve Network Edges
- GeoJSON format response
- Customer authentication and authorization
- Version parameter for historical data retrieval

### Additional Features
- Docker containerization with docker-compose
- Health check endpoints
- Comprehensive error handling
- Logging for debugging and monitoring
- API documentation with FastAPI/Swagger


## Troubleshooting

**Common Issues:**

1. **Database Connection**: Ensure PostgreSQL is running and accessible
2. **File Upload**: Check file format is valid GeoJSON
3. **Authentication**: Verify token is included in Authorization header

**Logs:**
```bash
# View API logs
docker-compose logs -f api

# View database logs
docker-compose logs -f postgres
```

## Testing & Demo

You can test the API interactively via the Swagger UI at `http://localhost:8000/docs`.

## Demo Customers and Users

The app is preconfigured with 2 customers and 2 users for demo purposes:

| Customer                     | Username      | Password         |
| ---------------------------- | ------------- | ---------------- |
| Munich City Roads Department | munich\_admin | RoadNetwork\@123 |
| Berlin Transport Authority   | berlin\_admin | RoadNetwork\@123 |

* Each user belongs to their respective customer and can only manage that customer's road networks.