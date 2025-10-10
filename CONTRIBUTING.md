# Contributing to Robot Framework Metrics Dashboard

Thank you for considering contributing! 🎉

## Table of Contents

* [Code of Conduct](#code-of-conduct)
* [How to Contribute](#how-to-contribute)
* [Development Setup](#development-setup)
* [Coding Standards](#coding-standards)
* [Pull Request Process](#pull-request-process)
* [Testing Guidelines](#testing-guidelines)
* [Commit Messages](#commit-messages)
* [Issue Reporting](#issue-reporting)
* [Development Workflow](#development-workflow)
* [Getting Help](#getting-help)
* [Recognition](#recognition)

---

## Code of Conduct

This project is governed by our Code of Conduct. Participation means you agree to uphold it.

### Our Pledge

We pledge to keep this project harassment-free for everyone, regardless of:

* Age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, sexual orientation.

### Our Standards

Positive behavior:

* Welcoming, inclusive language
* Respectful of differing viewpoints
* Gracefully accepting constructive criticism
* Focusing on the community's best interests
* Showing empathy

Unacceptable behavior:

* Trolling, insulting comments, personal attacks
* Harassment, public or private
* Publishing private info without consent
* Any inappropriate conduct

---

## How to Contribute

### Reporting Bugs

Check for duplicates first. Include:

* **Title**: Clear and specific
* **Steps to reproduce**
* **Expected vs Actual behavior**
* **Environment** (OS, Docker, browser)
* **Logs & Screenshots**

**Example:**

```text
Bug: Dashboard fails to load trends
Environment: Ubuntu 22.04, Docker 24.0.5, Chrome 119
Steps: 1. docker-compose up -d, 2. Open localhost:5000, 3. Click "Trends"
Expected: Chart displays trend data
Actual: Shows "Loading..." indefinitely
Logs: [ERROR] ...
```

### Suggesting Enhancements

Use issues to suggest enhancements:

* Clear title
* Detailed description
* Explain usefulness and use cases
* Provide examples/mockups

**Example:**

```text
Feature Request: Dark Mode Toggle
Description: Add a toggle for low-light viewing
Use Case: Nighttime monitoring
Implementation: Toggle button in nav, save preference, CSS theming
```

### Pull Requests

* **Good first issues:** docs, bug fixes, UI/UX, tests
* **More involved:** features, performance, API extensions

---

## Development Setup

### Prerequisites

* Python 3.11+
* Docker & Docker Compose
* Git
* Text editor (VS Code recommended)

### Setup Steps

```bash
git clone https://github.com/YOUR_USERNAME/robot-framework-metrics.git
cd robot-framework-metrics
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r metrics-service/requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```

### Run in Development Mode

```bash
cd metrics-service
export FLASK_DEBUG=1
export METRICS_DATA_DIR=../data
export ROBOT_RESULTS_DIR=../robot-results
python app.py
```

### Run Tests

```bash
pytest tests/
```

---

## Coding Standards

### Python

* PEP8, max 100 chars
* Black formatting, flake8 linting
* Google-style docstrings
* Type hints

### JavaScript

* 2-space indent, semicolons required, single quotes preferred

### HTML/CSS

* 2-space indent, kebab-case classes, camelCase IDs

---

## Pull Request Process

1. Create feature branch
2. Make changes, add tests/docs
3. Run tests, lint, format
4. Commit (`feat: add feature`)
5. Push branch
6. Open PR with clear title, description, issue refs
7. Review & address feedback
8. Squash if requested, merge

---

## Testing Guidelines

* `pytest tests/` to run all
* `pytest --cov=metrics-service tests/` for coverage
* Structure: reusable fixtures, aim >80% coverage

---

## Commit Messages

Follow [Conventional Commits]: `<type>(<scope>): <subject>`

* `feat` - feature
* `fix` - bug
* `docs` - documentation
* `style` - formatting
* `refactor` - code changes
* `perf` - performance
* `test` - tests
* `chore` - maintenance

Good: `feat(dashboard): add skip support`
Bad: `updated stuff`

---

## Issue Reporting

* **Security vulnerabilities:** Email [security@sunday.de](mailto:security@sunday.de)
* **Bug reports:** Use template with description, steps, environment, logs
* **Feature requests:** Use template with problem, solution, alternatives

---

## Development Workflow

* **Branches:** main, develop, feature/*, fix/*, docs/*
* **Release:** branch from develop, update version, CHANGELOG.md, PR to main, tag release, deploy

---

## Getting Help

* Docs: README.md
* Issues: search existing
* Discussions: GitHub
* Email: [support@sunday.de](mailto:support@sunday.de)

---

## Recognition

* Contributors listed in README.md
* Mentioned in release notes
* Credited in CHANGELOG.md
