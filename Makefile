.PHONY: up up-d down logs migrate seed backend-tests frontend-tests

up:
	docker-compose up --build

up-d:
	docker-compose up --build -d

down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	docker-compose run --rm backend alembic upgrade head

seed:
	docker-compose run --rm backend python -m backend.app.db.seed

backend-tests:
	cd backend && pytest

frontend-tests:
	cd frontend && npm install && npm run test -- --run
