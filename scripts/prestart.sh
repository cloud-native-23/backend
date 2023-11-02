#! /usr/bin/env bash
docker-compose build
docker-compose up -d

# Let the DB start
# docker-compose exec backend python3 -m app.backend_pre_start

# Run migrations
docker-compose exec backend alembic upgrade head

# Create initial data in DB
docker-compose exec backend python3 -m app.initial_data
docker-compose exec backend python3 -m app.database.test.test_database
docker-compose exec backend python3 -m app.database.test.initial_test_data

docker-compose down