COMPOSE_PROJECT_NAME_DEV = tugan-dev

COMPOSE_MAIN_DEV = docker/docker-compose.dev.yaml

ENV_MAIN = .env

DC_DEV = docker compose -f $(COMPOSE_MAIN_DEV) -p $(COMPOSE_PROJECT_NAME_DEV) --env-file $(ENV_MAIN)
PICCOLO_DEV = $(DC_DEV) exec backend piccolo


.PHONY: dev-build dev-up dev-down dev-stop dev-restart dev-logs dev-shell \
        dev-makemigrations dev-migrate dev-superuser dev-static

# ================= DEV =================

dev-build:
	$(DC_DEV) build

dev-up:
	$(DC_DEV) up -d

dev-down:
	$(DC_DEV) down $(args)

dev-stop:
	$(DC_DEV) stop

dev-restart:
	$(DC_DEV) restart $(s)

dev-logs:
	$(DC_DEV) logs -f $(s)

dev-shell:
	$(DC_DEV) exec $(s) bash

dev-makemigrations:
	$(PICCOLO_DEV) migrations new db --auto

dev-makemigrations-manual:
	$(PICCOLO_DEV) migrations new db --desc="$(or $(desc),manual_migration)"

dev-migrate:
	$(PICCOLO_DEV) migrations forwards all

dev-superuser:
	$(PICCOLO_DEV) user create
