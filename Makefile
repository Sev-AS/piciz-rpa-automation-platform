.PHONY: setup up up-tunnel down logs ps seed validate test lint clean

setup:
	@if [ ! -f .env ]; then cp .env.example .env && echo "Created .env from .env.example — remember to fill in your credentials."; else echo ".env already exists."; fi

up:
	docker compose up --build -d

up-tunnel:
	docker compose --profile tunnel up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

seed:
	docker compose exec -T postgres psql -U $${POSTGRES_USER:-piciz_admin} -d $${RPA_DB_NAME:-gestion_usuarios} < database/seed.example.sql

validate:
	docker compose config --quiet && docker compose --profile tunnel config --quiet && echo "docker-compose.yml is valid"

test:
	cd services/rpa-api && python3 -m unittest discover -s tests -v

lint:
	cd services/rpa-api && ruff check app tests

clean:
	rm -rf services/rpa-api/results services/rpa-api/app/__pycache__ services/rpa-api/tests/__pycache__ services/rpa-api/.ruff_cache
