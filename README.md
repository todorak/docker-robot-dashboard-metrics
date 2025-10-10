# 🤖 Robot Framework Metrics Dashboard

A powerful, **production-grade metrics dashboard** for Robot Framework — featuring advanced analytics, beautiful visualizations, and a comprehensive REST API.

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Architecture](#️-architecture)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Advanced Features](#-advanced-features)
- [Troubleshooting](#-troubleshooting)
- [Changelog](#-changelog)
- [License](#-license)
- [Authors](#-authors)
- [Acknowledgments](#-acknowledgments)
- [Support](#-support)
- [Roadmap](#-roadmap)

---

## ✨ Features

### 📊 Dashboard & Analytics
- **Real-time Metrics** – Live test execution statistics  
- **Trend Analysis** – Track pass rate and duration trends over time  
- **Test Distribution** – Visual breakdown of passed/failed/skipped tests  
- **Tag-based Analytics** – Performance tracking by test tags  
- **Flaky Test Detection** – Automatically identify unstable tests  
- **Slowest Tests** – Identify performance bottlenecks  

### 🏷️ Tag Analysis
- **Dedicated Tag Pages** – Deep dive into specific tag performance  
- **Historical Tracking** – Track tag performance across multiple runs  
- **Run Comparison** – Side-by-side comparison of test runs  
- **CSV Export** – Download tag data for external analysis  
- **Individual Test Performance** – Per-test statistics and history  

### 📈 Advanced Visualizations
- **Interactive Charts** – Click to drill down into details  
- **Time Range Filters** – Analyze specific time periods  
- **Status Filtering** – Filter by PASS/FAIL/SKIP status  
- **Gradient Styling** – Modern UI with smooth animations  

### 🔌 REST API
- **Comprehensive API** – Full programmatic access to metrics  
- **Interactive Documentation** – Built-in API explorer with Try-it-out  
- **JSON Responses** – Easy integration with CI/CD pipelines  
- **Data Export** – CSV export for external tools  

### 🚀 Production Ready
- **Docker-based** – Easy deployment with Docker Compose  
- **Multi-architecture** – AMD64/ARM64 support  
- **Persistent Storage** – Preserve historical data  
- **Health Checks** – Built-in monitoring endpoints  
- **Scalable** – Efficiently handle large test suites  

---

## ⚡ Quick Start

Get up and running in 5 minutes!

### 🧩 Prerequisites
- Docker & Docker Compose  
- 2GB free disk space  
- Port **5000** available  

### 🚀 1. Clone the Repository
```bash
git clone <your-repo-url>
cd robot-framework-metrics
```

### 🏗️ 2. Start the Services
```bash
docker-compose up -d
```

### 🤖 3. Run Your Tests
```bash
docker-compose run --rm robot robot --outputdir /robot_results /robot_src/tests/
```

### 📊 4. View the Dashboard
Open your browser and visit:  
👉 [http://localhost:5000](http://localhost:5000)

That’s it! 🎉

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Metrics Dashboard                        │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐     │
│  │  Dashboard  │  │ Tag Analysis │  │  API Docs       │     │
│  │   (Home)    │  │   Pages      │  │  /api-docs      │     │
│  └─────────────┘  └──────────────┘  └─────────────────┘     │
│         │                  │                   │            │
│         └──────────────────┴───────────────────┘            │
│                            │                                │
│                    ┌───────▼────────┐                       │
│                    │   Flask API    │                       │
│                    │   (app.py)     │                       │
│                    └───────┬────────┘                       │
│                            │                                │
│                    ┌───────▼────────┐                       │
│                    │ Metrics Parser │                       │
│                    │(metrics_parser)│                       │
│                    └───────┬────────┘                       │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Robot Framework │
                    │   output.xml     │
                    └──────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Historical Data │
                    │   (JSON files)   │
                    └──────────────────┘
```

### Components

**Metrics Service**
- Flask web server  
- RESTful API  
- Jinja2 templates  
- Chart.js visualizations  

**Metrics Parser**
- Robot Framework XML parsing  
- Test result aggregation  
- Historical data management  
- Flaky test detection  

**Data Storage**
- JSON-based persistence  
- Run history tracking  
- Incremental updates  

---

## 📦 Installation

### Method 1: Docker Compose (Recommended)

#### 1. Project Structure
```bash
mkdir robot-framework-metrics && cd robot-framework-metrics
mkdir -p {metrics-service/{templates,static},robot/tests,data/{history}}
chmod -R 755 data/
```

#### 2. Environment Variables
Create a `.env` file:

```bash
# Metrics Service
METRICS_PORT=5000
METRICS_DATA_DIR=/app/data
ROBOT_RESULTS_DIR=/robot_results

# Robot Framework
ROBOT_THREADS=6
BROWSER=headlesschrome
```

#### 3. Docker Compose
Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  metrics:
    build:
      context: .
      dockerfile: ./metrics-service/Dockerfile
    container_name: metrics_dashboard
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./robot-results:/robot_results:ro
    environment:
      - METRICS_DATA_DIR=/app/data
      - ROBOT_RESULTS_DIR=/robot_results
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  robot:
    image: your-robot-image:latest
    container_name: robot_tests
    volumes:
      - ./robot:/robot_src:ro
      - ./robot-results:/robot_results
    command: ["robot", "--outputdir", "/robot_results", "/robot_src/tests"]
```

#### 4. Build & Run
```bash
docker-compose build
docker-compose up -d
docker-compose ps
docker-compose logs -f metrics
```

---

### Method 2: Manual Installation
```bash
cd metrics-service
pip install -r requirements.txt

export METRICS_DATA_DIR=/path/to/data
export ROBOT_RESULTS_DIR=/path/to/robot/results

python app.py
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|-----------|----------|-------------|
| METRICS_PORT | 5000 | Web server port |
| METRICS_DATA_DIR | /app/data | Historical data storage |
| ROBOT_RESULTS_DIR | /robot_results | Robot Framework output directory |
| CHECK_INTERVAL | 10 | Output.xml check interval (seconds) |
| KEEP_HISTORY | true | Enable historical data retention |

---

## 🎯 Usage

### Running Tests
```bash
# Run all tests
docker-compose run --rm robot robot --outputdir /robot_results /robot_src/tests/

# Run specific tags
docker-compose run --rm robot robot --include smoke --outputdir /robot_results /robot_src/tests/

# Run with variables
docker-compose run --rm robot robot --variable BROWSER:chrome --outputdir /robot_results /robot_src/tests/
```

### Accessing the Dashboard
- **Main Dashboard:** [http://localhost:5000](http://localhost:5000)  
- **Tag Analysis:** [http://localhost:5000/tag/{tag_name}](#)  
- **Run Details:** [http://localhost:5000/run/{run_id}](#)  
- **API Docs:** [http://localhost:5000/api-docs](#)

---

## 📚 API Documentation

### General Endpoints
```bash
GET /health          # Health check
GET /api/status      # Service status
```

### Test Runs
```bash
GET /api/runs                 # List all runs
GET /api/runs/{run_id}        # Run details
DELETE /api/delete/{run_id}   # Delete a run
```

### Analytics
```bash
GET /api/trends
GET /api/flaky-tests
GET /api/slowest-tests
GET /api/compare
```

### Tags
```bash
GET /api/tag-stats
GET /api/tag/{tag}
GET /api/tag/{tag}/history
GET /api/tag/{tag}/export
```

### Data Management
```bash
POST /api/parse
POST /api/clear
```

### Response Format
```json
{
  "status": "success",
  "data": { ... },
  "timestamp": "2025-10-10T00:00:00"
}
```

Error example:
```json
{
  "error": "Description of error",
  "status_code": 404
}
```

---

## 🚀 Advanced Features

### Flaky Test Detection
Automatically identifies tests that fail intermittently:
```python
flaky_threshold = 0.1  # 10% fail rate
if 0 < fail_rate < (1 - flaky_threshold):
    mark_as_flaky(test)
```

### Tag-based Analysis
- Aggregate statistics by tag  
- Historical performance tracking  
- Per-test metrics and CSV export  

### Run Comparison
```json
{
  "run1": { "pass_rate": 87.5, "total": 8 },
  "run2": { "pass_rate": 100, "total": 8 },
  "difference": { "pass_rate": +12.5 }
}
```

### Filtering & Search
- Filter by **status**, **tag**, **time range**, or **run count**

### Data Export
- **CSV:** Tag analysis, test results  
- **JSON:** API responses  
- **HTML:** Robot Framework reports  

---

## 🔧 Troubleshooting

### 1. Dashboard shows no data
```bash
ls -la robot-results/output.xml
curl -X POST http://localhost:5000/api/parse
docker-compose logs metrics
```

### 2. Port already in use
```bash
echo "METRICS_PORT=5001" >> .env
docker-compose down && docker-compose up -d
```

### 3. Permission denied
```bash
sudo chown -R $USER:$USER data/
chmod -R 755 data/
docker-compose restart metrics
```

### 4. Output.xml not parsed
```bash
ls -la robot-results/output.xml
docker-compose exec metrics ls -la /robot_results/
curl -X POST http://localhost:5000/api/parse
```

### 5. Charts not displaying
```bash
curl http://localhost:5000/api/trends
```

### Debug Mode
```bash
export FLASK_DEBUG=1
```

### Health Checks
```bash
curl http://localhost:5000/health
curl http://localhost:5000/api/status
```

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

**Latest Version:** `v1.0.0 (2025-10-10)`  
- Initial release  
- Dashboard with analytics  
- Tag analysis pages  
- API documentation  
- Docker support  

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 👥 Authors
**Sunday Natural Products GmbH** – Initial development

---

## 🙏 Acknowledgments
- [Robot Framework](https://robotframework.org/)  
- [Flask](https://flask.palletsprojects.com/)  
- [Chart.js](https://www.chartjs.org/)  
- [Docker](https://www.docker.com/)  

---

## 📞 Support
- **Documentation:** [http://localhost:5000/api-docs](http://localhost:5000/api-docs)  
- **Issues:** Open an issue in this repository  
- **Email:** support@sunday.de  

---

## 🗺️ Roadmap

**Planned Features:**
- Dark mode toggle  
- Suite analysis pages  
- Real-time WebSocket updates  
- Advanced search functionality  
- PDF report generation  
- Email notifications for failures  
- CI/CD integration  
- Custom themes  
- Multi-project support  
- User authentication  

---

**⭐ If you find this project helpful, please consider giving it a star!**
