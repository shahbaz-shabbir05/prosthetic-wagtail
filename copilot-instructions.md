# Copilot Instructions for this Repository

This repository is a Django-based monorepo with Docker support, static site assets, and custom scripts. Please follow these guidelines when generating code or suggestions:

### Required After Editing a file
- Run `poetry run ruff <FILENAME>` after any changes to .py files to ensure proper code formatting
- Run `poetry run python manage.py makemigrations` to create new migrations if any models have changed
- Run `poetry run python manage.py test` to run tests after making changes to the codebase

## Python & Django
- Use Django best practices for models, views, forms, and templates.
- Place new Django apps in the `apps/` directory.
- Use class-based views unless a function-based view is more appropriate.
- Use Django migrations for all model changes.
- Place management commands in the `management/commands/` subfolder of each app.
- Use snake_case for Python variables and functions, PascalCase for class names.
- Keep business logic in models or services, not in views.
- Use Django's built-in User model unless otherwise specified.

## JavaScript & Node
- Place Node.js scripts in the `bin/` or `scripts/` directory.
- Use ES6+ syntax for JavaScript files.
- For static site generation, use the `static_build/` directory.
- Use npm or yarn for managing JS dependencies (see `package.json`).

## Docker
- Use the provided Dockerfiles and `docker-compose.yaml` for local development and deployment.
- Place new Docker-related scripts in the `docker/` directory.
- Keep environment-specific overrides in separate compose files (e.g., `docker-compose-ecslike.yaml`).

## Static Assets
- Place static files in `static_build/static/` or app-specific `static/` folders.
- Use hashed filenames for static assets when possible.
- Organize images, fonts, and CSS in their respective subfolders.

## Testing
- Place Django tests in the `tests/` subfolder of each app.
- Use pytest or Django's test runner.
- Name test files as `test_*.py`.

## Documentation
- Update `README.md` for major changes.
- Add docstrings to all public Python classes and functions.
- Use comments to explain non-obvious code.

## General
- Follow PEP8 for Python code style.
- Use 4 spaces for Python indentation, 2 spaces for JavaScript.
- Prefer explicit over implicit code.
- Use descriptive commit messages.

---

These instructions are intended to help AI code assistants and contributors generate code that fits the project's structure and conventions.
