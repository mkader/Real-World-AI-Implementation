.PHONY: build up down logs index-worker index-rebuild

build:
	docker compose build

up:
	docker compose up --detach

down:
	docker compose down

logs:
	docker compose logs -f api

index-worker:
	# run worker process_unindexed once inside container (dev)
	docker compose run --rm api python -c "from api.worker import process_unindexed; print(process_unindexed())"

index-rebuild:
	docker compose run --rm index-builder
