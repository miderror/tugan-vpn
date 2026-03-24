COMPOSE_PROJECT_NAME_DEV = tugan-dev
COMPOSE_PROJECT_NAME_NODE = tugan-node

COMPOSE_MAIN_DEV = deploy/docker-compose.dev.yaml
COMPOSE_NODE = vpn-node/docker-compose.yaml

ENV_MAIN = .env
ENV_NODE = vpn-node/.env

DC_DEV = docker compose -f $(COMPOSE_MAIN_DEV) -p $(COMPOSE_PROJECT_NAME_DEV) --env-file $(ENV_MAIN)
MANAGE_DEV = $(DC_DEV) exec backend python manage.py

DC_NODE = docker compose -f $(COMPOSE_NODE) -p ${COMPOSE_PROJECT_NAME_NODE} --env-file ${ENV_NODE}

.PHONY: dev-build dev-up dev-down dev-stop dev-restart dev-logs dev-shell \
        dev-makemigrations dev-migrate dev-superuser dev-static dev-startapp \
		node-build node-up node-down node-stop node-restart node-logs node-shell

dev-build:
	$(DC_DEV) build

dev-up:
	$(DC_DEV) up -d --build

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
	$(MANAGE_DEV) makemigrations $(args)

dev-migrate:
	$(MANAGE_DEV) migrate

dev-superuser:
	$(MANAGE_DEV) createsuperuser

dev-static:
	$(MANAGE_DEV) collectstatic --noinput


node-build:
	${DC_NODE} build

node-up:
	${DC_NODE} up -d --build

node-down:
	${DC_NODE} down $(args)

node-stop:
	$(DC_NODE) stop

node-restart:
	$(DC_NODE) restart $(s)

node-logs:
	${DC_NODE} logs -f $(s)

node-shell:
	${DC_NODE} exec $(s) bash
