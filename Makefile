# Sunday Natural Robot Framework Makefile
PROJECT_NAME ?= sunday
ROBOT_ARCH ?= amd64
UID ?= $(shell id -u)
GID ?= $(shell id -g)
TEST_TAG ?= Smoke
PROCESSES ?= 6

export PROJECT_NAME ROBOT_ARCH UID GID TEST_TAG PROCESSES

.PHONY: help setup build test metrics clean status logs

help: ## Show this help message
	@echo "Sunday Robot Framework Commands"
	@echo "========================================"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial project setup
	@echo "Setting up project directories..."
	mkdir -p data/{robot/{results,logs},metrics/history}
	chmod -R 755 data/
	@echo "✅ Setup complete!"

build: ## Build all Docker services
	@echo "Building all services..."
	docker-compose build
	@echo "✅ Build complete!"

build-robot: ## Build only Robot service
	docker-compose build robot

build-metrics: ## Build only Metrics service
	docker-compose build metrics

test: ## Run Robot tests (internal)
	@echo "Running tests with tag: $(TEST_TAG)"
	docker-compose up --abort-on-container-exit robot
	@echo "✅ Tests complete! Metrics will auto-parse in ~2 seconds"

test-smoke: ## Run smoke tests
	@$(MAKE) test TEST_TAG=Smoke

test-all: ## Run all tests
	@$(MAKE) test TEST_TAG=""

test-multi: ## Run tests N times (make test-multi N=5)
	@echo "Running tests $(or $(N),3) times..."
	@for i in $$(seq 1 $(or $(N),3)); do \
		echo "Run $$i of $(or $(N),3)"; \
		$(MAKE) test-smoke; \
		sleep 3; \
	done

metrics: ## Start Metrics dashboard
	@echo "Starting Metrics Dashboard..."
	docker-compose up -d metrics
	@sleep 2
	@echo "✅ Dashboard: http://localhost:$(METRICS_PORT)"

parse-metrics: ## Manually parse latest results
	@echo "Parsing test results..."
	@curl -s -X POST http://localhost:5000/api/parse || echo "⚠️  Metrics not running"

stop: ## Stop all services
	docker-compose down

clean: ## Clean all data
	docker-compose down -v
	@echo "⚠️  Remove data? (y/N)" && read ans && [ $${ans:-N} = y ] && rm -rf data/robot/results/* data/metrics/history/*

clean-results: ## Clean test results only
	rm -rf data/robot/results/* data/robot/logs/*

clean-history: ## Clean metrics history
	rm -rf data/metrics/history/*.json

logs: ## Show all logs
	docker-compose logs -f

logs-robot: ## Show Robot logs
	docker-compose logs -f robot

logs-metrics: ## Show Metrics logs
	docker-compose logs -f metrics

status: ## Show services status
	@docker-compose ps
	@curl -s http://localhost:5000/api/status | jq '.' 2>/dev/null || echo "Metrics not running"

shell-robot: ## Shell in Robot container
	docker-compose exec robot bash

shell-metrics: ## Shell in Metrics container
	docker-compose exec metrics bash

restart: ## Restart all services
	docker-compose restart

restart-robot: ## Restart Robot service
	docker-compose restart robot

restart-metrics: ## Restart Metrics service
	docker-compose restart metrics

ps: ## Show running containers
	docker-compose ps

info: ## Show project info
	@echo "📦 Project: $(PROJECT_NAME)"
	@echo "🏗️  Arch: $(ROBOT_ARCH)"
	@echo "🌐 Dashboard: http://localhost:5000"

-include .env