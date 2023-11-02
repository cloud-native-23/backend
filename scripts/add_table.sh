docker-compose build
docker-compose up -d

docker-compose exec backend alembic revision --autogenerate -m "Add on delete for MR FK constraint"
docker-compose exec backend alembic upgrade head
docker-compose down