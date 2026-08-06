COMPOSE_PROJECT_NAME_DEV = tugan-dev
COMPOSE_PROJECT_NAME_PROD = tugan-prod

COMPOSE_MAIN_DEV = docker/docker-compose.dev.yaml
COMPOSE_MAIN_PROD = docker/docker-compose.prod.yaml

ENV_MAIN = .env

DC_DEV = docker compose -f $(COMPOSE_MAIN_DEV) -p $(COMPOSE_PROJECT_NAME_DEV) --env-file $(ENV_MAIN)
DC_PROD = docker compose -f $(COMPOSE_MAIN_PROD) -p $(COMPOSE_PROJECT_NAME_PROD) --env-file $(ENV_MAIN)

PICCOLO_DEV = $(DC_DEV) exec backend piccolo
PICCOLO_PROD = $(DC_PROD) exec backend piccolo

.PHONY: dev-build dev-up dev-down dev-stop dev-restart dev-logs dev-shell \
        dev-makemigrations dev-makemigrations-manual dev-migrate dev-superuser \
        dev-redis-flush dev-db-up dev-migrate-init dev-import-data \
        dev-webhook-set dev-webhook-delete \
        prod-build prod-up prod-down prod-stop prod-restart prod-logs prod-shell \
        prod-build-front prod-migrate prod-migrate-init prod-import-data prod-superuser \
        prod-webhook-set prod-webhook-delete \
        prod-test-ssl prod-get-ssl prod-renew-ssl

# ================= DEVELOPMENT =================

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

dev-redis-flush:
	$(DC_DEV) exec redis redis-cli FLUSHDB

dev-makemigrations:
	$(PICCOLO_DEV) migrations new db --auto

dev-makemigrations-manual:
	$(PICCOLO_DEV) migrations new db --desc="$(or $(desc),manual_migration)"

dev-migrate:
	$(PICCOLO_DEV) migrations forwards all

dev-superuser:
	$(PICCOLO_DEV) user create

dev-db-up:
	$(DC_DEV) up -d db redis

dev-migrate-init:
	$(DC_DEV) run --rm backend piccolo migrations forwards all

dev-import-data:
	$(DC_DEV) run --rm backend python app/tasks/migrate_old_data.py $(or $(file),data_logic.json)

dev-fix-payments:
	$(DC_DEV) exec backend python app/tasks/fix_payments_data.py $(or $(file),data_logic.json)

dev-webhook-set:
	$(DC_DEV) exec backend python app/tasks/manage_webhook.py set

dev-webhook-delete:
	$(DC_DEV) exec backend python app/tasks/manage_webhook.py delete

# ================= PRODUCTION =================

prod-build:
	$(DC_PROD) build

prod-up:
	$(DC_PROD) up -d --build

prod-down:
	$(DC_PROD) down

prod-stop:
	$(DC_PROD) stop

prod-restart:
	$(DC_PROD) restart $(s)

prod-logs:
	$(DC_PROD) logs -f $(s)

prod-shell:
	$(DC_PROD) exec $(s) bash

prod-build-front:
	@echo "Building frontend..."
	$(DC_PROD) --profile tools up --build frontend-builder
	@echo "Frontend asset build completed."

prod-migrate:
	$(PICCOLO_PROD) migrations forwards all

prod-db-up:
	$(DC_PROD) up -d db redis

prod-migrate-init:
	$(DC_PROD) run --rm backend piccolo migrations forwards all

prod-import-data:
	$(DC_PROD) run --rm -v $(shell pwd)/backend/data_logic.json:/app/data_logic.json backend python app/tasks/migrate_old_data.py data_logic.json

prod-fix-payments:
	$(DC_PROD) run --rm -v $(shell pwd)/backend/data_logic.json:/app/data_logic.json backend python app/tasks/fix_payments_data.py data_logic.json

prod-superuser:
	$(PICCOLO_PROD) user create

prod-webhook-set:
	$(DC_PROD) exec backend python app/tasks/manage_webhook.py set

prod-webhook-delete:
	$(DC_PROD) exec backend python app/tasks/manage_webhook.py delete

# ================= SSL =================

SSL_DIR = $(shell pwd)/ssl

prod-test-ssl:
	@echo "Testing SSL issuance for domain $(DOMAIN)..."
	-docker stop tugan-prod-nginx
	docker run --rm --name certbot \
		-p 80:80 \
		-v $(SSL_DIR):/etc/letsencrypt \
		certbot/certbot certonly --standalone \
		-d $(DOMAIN) \
		--non-interactive --agree-tos --register-unsafely-without-email --dry-run
	@echo "Test completed successfully."

prod-get-ssl:
	@echo "Obtaining production SSL certificate for $(DOMAIN)..."
	-docker stop tugan-prod-nginx
	docker run --rm --name certbot \
		-p 80:80 \
		-v $(SSL_DIR):/etc/letsencrypt \
		certbot/certbot certonly --standalone \
		-d $(DOMAIN) \
		--non-interactive --agree-tos --register-unsafely-without-email
	@echo "SSL certificate saved to ./ssl"

prod-renew-ssl:
	@echo "Renewing SSL certificate..."
	-docker stop tugan-prod-nginx
	docker run --rm --name certbot \
		-p 80:80 \
		-v $(SSL_DIR):/etc/letsencrypt \
		certbot/certbot renew --standalone
	docker start tugan-prod-nginx
	@echo "SSL renewal complete."
