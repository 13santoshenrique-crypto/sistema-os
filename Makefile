.PHONY: compose-up build test lint deploy-fly setup-secrets

compose-up:
	@docker compose up --build

build:
	docker build -t sistema-os:latest .

test:
	python manage.py test

deploy-fly:
	@echo "Use scripts/fly-setup.sh or run manually: flyctl deploy"

setup-secrets:
	@./scripts/setup-github-secrets.sh
