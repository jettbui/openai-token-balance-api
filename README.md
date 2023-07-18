# OpenAI Token-Balance API

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
[![License](https://img.shields.io/github/license/Ileriayo/markdown-badges?style=for-the-badge)](./LICENSE.md)

## About the Project

This project is a utility API for managing user token balances and OpenAI API usage.
It is built with [Django](https://www.djangoproject.com/) and [Django REST Framework](https://www.django-rest-framework.org/).
Users will be able authenticate and make requests to the OpenAI API through a single provided API key, with limited usage based on their token balance.

### Features

- Simplified user token authentication and user balance management
- OpenAI API integration and usage control on a per-user basis
- Extensibility for additional endpoints and API consolidation

## Getting Started

### Prerequisites

This project utilizes [Docker (>= v24.0.2)](https://www.docker.com/) and [Docker Compose (>= v2.18.1)](https://docs.docker.com/compose/). 
Please install this before continuing!

A full list of dependencies can be found in [requirements.txt](requirements.txt).

### Setup

First, clone the repository:

```bash
git clone <repo-url>
```

Then, build the Docker image and run the migrations:

```bash
docker-compose build
docker-compose run --rm app sh -c "python manage.py makemigrations"
docker-compose run --rm app sh -c "python manage.py migrate"
```

Create an initial superuser account with the following:

```bash
docker-compose run --rm app sh -c "python manage.py createsuperuser"
```

Django will prompt you to enter an email and password.
You can use these credentials to log into the admin panel at `/admin`. You can start the development server with:

```bash
docker-compose up
```

If you plan to use the OpenAI API, you will need to create an account and [obtain an API key](https://platform.openai.com/account/api-keys). Then, create a `.env` file in the root directory with the following:

```bash
OPENAI_ORGANIZATION=<ORGANIZATION_ID>
OPENAI_API_KEY=<API_KEY>
```

Additional commands can be run with:

- `docker-compose run --rm app sh -c "python manage.py test"` to run the test suite
- `docker-compose run --rm app sh -c "python manage.py flake8"` to run the linter
- `docker-compose run --rm app sh -c "python manage.py startapp <app_name>"` to create a new Django app

### Documentation

Documentation can be found at `/api/docs` and is automatically generated by [Swagger](https://swagger.io/) and [drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/).

### Example

Retrieve an authentication token with a `POST` request to `/api/user/auth` (refer to the documentation above). 
You can set a user's balance with either a `PATCH` request to `/api/balance/{user_id}` (note that this route is only available to superusers) or through the Django Admin panel. 

1. Start by setting the user's balance to 30:

```json
// PATCH /balance/{user_id}
{
    "balance": 30
}
```

The response will contain the user's new balance, as well as the id of the user whose balance was set. 
You can also view this information by submitting a `GET` request to `/api/balance` (available to all authenticated users).

The project is setup with practical routes for interacting with OpenAI's API (make sure your `.env` file is setup correctly). 

2. Make a `POST` request to `/api/openai/chat/completions` with the following content:

```json
// POST /api/openai/chat/completions
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    }, 
    {
      "role": "user",
      "content": "Hello!"
    }
  ]
}
```

You will see that the response is similar to `POST https://api.openai.com/v1/chat/completions` ([OpenAI docs](https://platform.openai.com/docs/api-reference/chat/create)).
Additionally, the authenticated user's balance will be decremented by the token cost of the request, which, in almost all successful cases, will be the total token usage returned in the response. If a user's balance is less than the token cost of **the input**, the request to OpenAI will not be made.

You can view the logic in more detail in [views.py](app/openai_app/views.py) for the `openai_app` application.
