# 🚀 HOW-TO: Sunday Natural Robot Framework + Custom Allure Setup

## 📋 Какво ще постигнеш

Ще построиш пълен Docker-базиран setup за Robot Framework тестове с:
- ✅ Custom Allure service (без external dependencies)
- ✅ Multi-architecture support (AMD64/ARM64)
- ✅ Parallel test execution с pabot
- ✅ Beautiful dashboard и REST API
- ✅ Production-ready конфигурация

---

## 🏗️ Стъпка 1: Подготовка на проектната структура

### 1.1 Създаване на директории
```bash
mkdir sunday-robot-framework && cd sunday-robot-framework

# Основна структура
mkdir -p {robot/{tests,resources,libraries},allure-service/{templates,static},nginx,config/robot,data/{robot/allure,allure/reports}}

# Permissions (важно за Docker)
sudo chown -R $USER:$USER data/
chmod -R 755 data/
```

### 1.2 Environment variables
```bash
# Създай .env файл в root директорията
cat > .env << 'EOF'
PROJECT_NAME=sunday
ROBOT_ARCH=amd64
UID=1000
GID=1000
TEST_TAG=Smoke
PROCESSES=6
ODOO_HOST=odoo
ODOO_PORT=8069
ALLURE_PORT=5050
ROBOT_PORT=7778
EOF

# Зареди environment
source .env
export $(cat .env | xargs)
```

---

## 🐳 Стъпка 2: Docker файлове

### 2.1 Robot Framework Dockerfile
```bash
# Създай robot/Dockerfile
cat > robot/Dockerfile << 'EOF'
FROM python:3.11-slim
LABEL version="latest" maintainer="Sunday Natural Products GmbH"

ARG UID=1000
ARG GID=1000

# Копиране на requirements
COPY ./robot/requirements.txt /tmp/requirements.txt

# Системни пакети и Chrome setup
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        wget \
        sudo \
        procps && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/google-chrome.gpg] https://dl-ssl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list

# Инсталиране на Chrome и Java
RUN apt-get update -y && apt-get install -y --no-install-recommends \
        google-chrome-stable \
        default-jre && \
    apt-get -y autoremove && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/tmp/*

# Инсталиране на Allure
RUN wget -O allure.tgz https://github.com/allure-framework/allure2/releases/download/2.24.0/allure-2.24.0.tgz && \
    tar -zxvf allure.tgz -C /opt/ && \
    ln -s /opt/allure-2.24.0/bin/allure /usr/bin/allure && \
    rm allure.tgz

# Python пакети
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    rm -rf /tmp/*

# Потребител
RUN groupadd headless -g $GID && \
    useradd headless --shell /bin/bash --create-home -u $UID -g $GID && \
    usermod -a -G sudo headless && \
    echo 'headless ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

# Директории
RUN mkdir -p /robot_src \
             /robot_results/results \
             /robot_results/allure \
             /allure-results \
             /allure-report && \
    chown -R headless:headless /robot_src \
                               /robot_results \
                               /allure-results \
                               /allure-report

# Скриптове
COPY --chown=headless:headless ./robot/entrypoint.sh /entrypoint.sh
COPY --chown=headless:headless ./robot/test_runner.py /test_runner.py
RUN chmod +x /entrypoint.sh

USER headless
WORKDIR /robot_src

ENTRYPOINT ["/entrypoint.sh"]
CMD ["Smoke"]
EXPOSE 7778
EOF
```

### 2.2 Requirements файл
```bash
# Създай robot/requirements.txt
cat > robot/requirements.txt << 'EOF'
# Core Robot Framework
robotframework==7.1.1
robotframework-pabot==2.18.0
robotframework-pythonlibcore==4.4.1

# Selenium
selenium==4.26.1
robotframework-seleniumlibrary==6.6.1
webdriver-manager==4.0.1

# Allure
allure-robotframework==2.13.5

# Допълнителни библиотеки
robotframework-requests==0.9.5
robotframework-databaselibrary==1.2.4
robotframework-sshlibrary==3.8.0

# Утилити
colorama==0.4.6
click==8.1.7
requests==2.31.0
EOF
```

### 2.3 Custom Allure Service
```bash
# Създай allure-service/Dockerfile
cat > allure-service/Dockerfile << 'EOF'
FROM openjdk:11-jre-slim

LABEL maintainer="Sunday Natural Products GmbH"
ARG UID=1000
ARG GID=1000
ARG ALLURE_VERSION=2.24.0

# Системни пакети
RUN apt-get update && apt-get install -y \
    wget curl unzip python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Потребител
RUN groupadd -g $GID allure && \
    useradd -u $UID -g $GID -m -s /bin/bash allure

# Allure
RUN wget -O allure.tgz https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz && \
    tar -zxvf allure.tgz -C /opt/ && \
    ln -s /opt/allure-${ALLURE_VERSION}/bin/allure /usr/bin/allure && \
    rm allure.tgz

# Python пакети
RUN pip3 install --no-cache-dir flask==2.3.3 gunicorn==21.2.0 watchdog==3.0.0

# Директории
RUN mkdir -p /app/{allure-results,reports,static,templates} && \
    chown -R allure:allure /app

# Приложение
COPY --chown=allure:allure ./allure-service/app.py /app/
COPY --chown=allure:allure ./allure-service/templates/ /app/templates/
COPY --chown=allure:allure ./allure-service/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV ALLURE_RESULTS_DIR=/app/allure-results
ENV ALLURE_REPORTS_DIR=/app/reports
ENV PORT=5050

WORKDIR /app
USER allure
EXPOSE 5050

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--workers", "2", "app:app"]
EOF
```

---

## ⚙️ Стъпка 3: Конфигурационни файлове

### 3.1 Robot Framework конфигурация
```bash
# Създай config/robot/.env
cat > config/robot/.env << 'EOF'
# Robot Framework Configuration
BROWSER=headlesschrome
PROCESSES=6
TIMEOUT=30

# Odoo Connection
ODOO_HOST=odoo
ODOO_PORT=8069
ODOO_DATABASE=test_db
ODOO_USER=admin
ODOO_PASSWORD=admin

# Browser Settings
CHROME_OPTIONS=--headless --no-sandbox --disable-dev-shm-usage --disable-gpu
SELENIUM_TIMEOUT=10

# Allure
ALLURE_RESULTS_DIR=/robot_results/allure
START_ALLURE_SERVER=false

# Debug
DEBUG_MODE=false
VERBOSE_LOGGING=false
EOF
```

### 3.2 Docker Compose
```bash
# Създай docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: "3.8"

services:
  robot:
    image: ${PROJECT_NAME}_robot:${ROBOT_ARCH}_latest
    platform: linux/${ROBOT_ARCH}
    build:
      context: .
      dockerfile: ./robot/Dockerfile
      args:
        - UID=${UID:-1000}
        - GID=${GID:-1000}
    container_name: ${PROJECT_NAME}_robot_${ROBOT_ARCH}
    shm_size: '2gb'
    ports:
      - ${ROBOT_PORT:-7778}:7778
    env_file:
      - ./config/robot/.env
    environment:
      - ODOO_HOST=${ODOO_HOST:-odoo}
      - PROCESSES=${PROCESSES:-6}
      - PROJECT_NAME=${PROJECT_NAME}
    volumes:
      - ./data/robot/allure:/robot_results
      - ./robot:/robot_src:ro
      - ./config/robot:/config:ro
    networks:
      - robot_network
    command: ["${TEST_TAG:-Smoke}"]

  allure:
    image: ${PROJECT_NAME}_allure:latest
    build:
      context: .
      dockerfile: ./allure-service/Dockerfile
      args:
        - UID=${UID:-1000}
        - GID=${GID:-1000}
    container_name: ${PROJECT_NAME}_allure
    environment:
      - ALLURE_RESULTS_DIR=/app/allure-results
      - CHECK_RESULTS_EVERY_SECONDS=5
      - KEEP_HISTORY=true
    ports:
      - "${ALLURE_PORT:-5050}:5050"
    volumes:
      - ./data/robot/allure:/app/allure-results:ro
      - ./data/allure/reports:/app/reports
    networks:
      - robot_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5050/health"]
      interval: 30s

networks:
  robot_network:
    driver: bridge
EOF
```

### 3.3 Makefile
```bash
# Създай Makefile
cat > Makefile << 'EOF'
# Sunday Natural Robot Framework Makefile
PROJECT_NAME ?= sunday
ROBOT_ARCH ?= amd64
UID ?= $(shell id -u)
GID ?= $(shell id -g)
TEST_TAG ?= Smoke

export PROJECT_NAME ROBOT_ARCH UID GID TEST_TAG

.PHONY: help build test allure clean

help: ## Показва помощ
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build всички services
	docker-compose build

test: ## Стартиране на тестове
	docker-compose up --abort-on-container-exit robot

test-smoke: ## Smoke тестове
	$(MAKE) test TEST_TAG=Smoke

allure: ## Стартиране на Allure сървър
	docker-compose up -d allure
	@echo "Allure server: http://localhost:5050"

allure-generate: ## Force генериране на отчет
	curl -X POST http://localhost:5050/api/generate -H "Content-Type: application/json" -d '{"force": true}'

clean: ## Почистване
	docker-compose down -v
	rm -rf data/robot/allure/* data/allure/*

status: ## Статус на услугите
	docker-compose ps

logs: ## Логове
	docker-compose logs -f

setup: ## Първоначален setup
	mkdir -p data/{robot/allure,allure/reports}
	chmod -R 755 data/
	@echo "Setup complete!"
EOF
```

---

## 🎯 Стъпка 4: Копиране на файлове от artifacts

Копирай следните файлове от моите artifacts в съответните директории:
- `robot/entrypoint.sh`
- `robot/test_runner.py` 
- `allure-service/app.py`
- `allure-service/entrypoint.sh`
- `allure-service/templates/dashboard.html`
- `allure-service/templates/no_report.html`

---

## 🚀 Стъпка 5: Първи тест

### 5.1 Setup и build
```bash
# 1. Първоначален setup
make setup

# 2. Build на всички services
make build

# 3. Проверка на статуса
make status
```

### 5.2 Създаване на примерен тест
```bash
# Създай robot/tests/example.robot
mkdir -p robot/tests
cat > robot/tests/example.robot << 'EOF'
*** Settings ***
Library    SeleniumLibrary
Default Tags    smoke

*** Variables ***
${URL}    https://example.com
${BROWSER}    headlesschrome

*** Test Cases ***
Simple Web Test
    [Documentation]    Примерен тест
    [Tags]    smoke    web
    Open Browser    ${URL}    ${BROWSER}
    Page Should Contain    Example Domain
    Close Browser

API Test Example
    [Documentation]    Примерен API тест  
    [Tags]    smoke    api
    Log    API test placeholder
    Should Be Equal    1    1
EOF
```

### 5.3 Стартиране на тестовете
```bash
# 1. Стартирай тестовете
make test-smoke

# 2. Стартирай Allure сървъра
make allure

# 3. Отвори в браузъра
open http://localhost:5050
```

---

## 🎨 Стъпка 6: Използване и възможности

### 6.1 Основни команди
```bash
# Различни типове тестове
make test TEST_TAG=Accounting
make test TEST_TAG=Sales  
make test TEST_TAG=Inventory

# Паралелни тестове
make test PROCESSES=10

# Статус и логове
make status
make logs

# Почистване
make clean
```

### 6.2 Allure API
```bash
# Статус на service
curl http://localhost:5050/api/status

# Генериране на отчет
curl -X POST http://localhost:5050/api/generate \
  -H "Content-Type: application/json" \
  -d '{"force": true}'

# Почистване на данни
curl -X POST http://localhost:5050/api/clear
```

### 6.3 Интерактивен режим
```bash
# Стартиране на интерактивен mode
docker-compose run --rm robot python3 /test_runner.py --interactive

# Debug режим
docker-compose run --rm robot bash
```

---

## 🔧 Стъпка 7: Troubleshooting

### 7.1 Общи проблеми
```bash
# Проверка на permissions
ls -la data/
sudo chown -R $USER:$USER data/

# Проверка на Docker
docker --version
docker-compose --version

# Health checks
curl http://localhost:5050/health
docker-compose ps
```

### 7.2 Debug логове
```bash
# Robot логове
docker-compose logs robot

# Allure логове  
docker-compose logs allure

# Системни логове
docker-compose exec robot df -h
docker-compose exec robot ps aux
```

### 7.3 Port конфликти
```bash
# Промяна на портове в .env
echo "ALLURE_PORT=5051" >> .env
echo "ROBOT_PORT=7779" >> .env

# Рестарт
make clean
make build
```

---

## ✅ Стъпка 8: Готово!

Имаш пълнофункционален Docker setup с:
- ✅ Robot Framework с паралелни тестове
- ✅ Custom Allure service без external dependencies  
- ✅ Beautiful dashboard на http://localhost:5050
- ✅ REST API за автоматизация
- ✅ Multi-architecture support
- ✅ Production-ready конфигурация

### Полезни линкове:
- **Allure Dashboard:** http://localhost:5050
- **Allure Report:** http://localhost:5050/report/
- **API Status:** http://localhost:5050/api/status

### Следващи стъпки:
1. Добави твоите съществуващи тестове в `robot/tests/`
2. Настрой Odoo connection в `config/robot/.env`
3. Customize Allure dashboard в `allure-service/templates/`
4. Setup CI/CD pipeline
5. Production deployment с Nginx

**Enjoy your new Robot Framework setup! 🚀**
