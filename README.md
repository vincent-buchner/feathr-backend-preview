> **Note:** This is a public preview of our senior project backend from early 2024. The original repository has been made private. Big thanks to @dahalsabina, @SorenBasnet, and @millie178 for their contributions.

# Senior Project Backend: Feathr Services

## Overview

This repository contains backend services for the Feathr project, developed by Team B for the academic year 2024/25. The project consists of multiple microservices designed to support different functionalities.

## Table of Contents

- [Project Structure](#project-structure)
- [Services](#services)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [Testing](#testing)

## Project Structure

The backend is composed of four primary services:

1. **Boids Simulation Service**
2. **User Service**
3. **Discussion Service**
4. **Django Backend**

## Services Details

### 1. Boids Simulation Service

#### Main Configuration

```
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('hello_world/', include('helloWorld.urls')),
    path('boids_service/', include('boidsSimulation.urls')),
    path('discussion_service/', include('discussion.urls')),
    path('user_service/', include('user_service.urls')),
]
```

#### Key Endpoints

| Method | Endpoint              | Description                       |
| ------ | --------------------- | --------------------------------- |
| GET    | `/boids/`             | Retrieve all boids from database  |
| POST   | `/boids/`             | Create a new boid                 |
| GET    | `/boids/<id>/`        | Get specific boid details         |
| PATCH  | `/boids/<id>/`        | Update boid information           |
| DELETE | `/boids/<id>/`        | Remove a boid                     |
| GET    | `/simulation/config/` | Retrieve simulation configuration |

### 2. User Service

#### Key Endpoints

| Method | Endpoint       | Description               |
| ------ | -------------- | ------------------------- |
| GET    | `/users/`      | Retrieve all user records |
| POST   | `/users/`      | Create a new user         |
| GET    | `/users/<id>/` | Get user details          |
| PATCH  | `/users/<id>/` | Update user information   |
| DELETE | `/users/<id>/` | Remove a user             |

### 3. Discussion Service

#### Key Endpoints

| Method | Endpoint             | Description              |
| ------ | -------------------- | ------------------------ |
| GET    | `/discussions/`      | Retrieve all discussions |
| POST   | `/discussions/`      | Create a new discussion  |
| GET    | `/discussions/<id>/` | Get specific discussion  |
| PATCH  | `/discussions/<id>/` | Update discussion        |
| DELETE | `/discussions/<id>/` | Remove a discussion      |

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- Django
- Other dependencies listed in `requirements.txt`

### Installation

1. Clone the repository
2. Create a virtual environment
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Testing

To test the project, we use the builtin Django tester along with the coverage library to get our test coverage
Run the following command to test the whole application:

```
coverage run manage.py test
```

then run this command to get the report:

```
coverage report
```

