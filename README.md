# Mini Discord - Backend

This repository contains the backend service for a real-time chat application, similar to a mini Discord. It's built with Django and the Django REST Framework, featuring a robust API for user authentication and real-time messaging via WebSockets.

The entire development environment is containerized using **Docker** and **Docker Compose**, ensuring a simple and repeatable setup process.

---

## Features

* **User Authentication**: Secure JWT-based authentication for users.
* **RESTful API**: A clean, browsable API for all resources like servers, channels, and messages.
* **Real-time Messaging**: WebSocket support using Django Channels and Redis for instant message delivery.
* **Containerized Environment**: Fully containerized with Docker for development and production consistency.

---

## Tech Stack

* **Framework**: Django, Django REST Framework, Django Channels
* **Database**: PostgreSQL
* **Real-time/Cache**: Redis
* **WSGI Server**: Gunicorn
* **Containerization**: Docker & Docker Compose

---

## Getting Started

Follow these instructions to get the project up and running on your local machine for development and testing.

### Prerequisites

* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/products/docker-desktop/)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/NIMATDGH/back.git](https://github.com/NIMATDGH/back.git)
    cd back
    ```

2.  **Create the environment file:**
    Copy the example environment file to create your own local configuration.
    ```bash
    cp .env.example .env.dev
    ```
    Now, open the `.env.dev` file and fill in your own secret values.

3.  **Build and run the Docker containers:**
    This command will build the images and start the Django, PostgreSQL, and Redis services.
    ```bash
    docker-compose up --build
    ```
    Your API will be running at `http://localhost:8000`.

4.  **Apply database migrations:**
    In a **new terminal window**, run the migrate command to set up your database schema.
    ```bash
    docker-compose run --rm web python manage.py migrate
    ```

5.  **Create a superuser (optional):**
    To access the Django admin panel, create a superuser.
    ```bash
    docker-compose run --rm web python manage.py createsuperuser
    ```
