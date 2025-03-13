Dockerized Flask App with PostgreSQL & Redis

This project is a Flask web application that connects to PostgreSQL and Redis, running inside Docker containers using docker-compose.

Features:

Flask web app

PostgreSQL database integration

Redis caching

Docker & docker-compose for easy setup

Setup Instructions:

Clone the Repository:
git clone https://github.com/yourusername/Docker_project2.git
cd Docker_project2

Create a .env File:
Create a .env file in the project root with the following content:
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=mydatabase
REDIS_HOST=redis

Build & Start Containers:
docker-compose up --build -d

Access the Web App:
Open in browser: http://localhost:8000 or curl http://localhost:8000

Check Database (Inside Container):
docker exec -it docker_task3-db-1 psql -U user -d mydatabase

List tables: \dt

Query data: SELECT * FROM visits;
