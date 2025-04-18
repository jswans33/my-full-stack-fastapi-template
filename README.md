# Full Stack FastAPI Template

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
  - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for the Python SQL database interactions (ORM).
  - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
  - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
- 🚀 [React](https://react.dev) for the frontend.
  - 💃 Using TypeScript, hooks, Vite, and other parts of a modern frontend stack.
  - 🎨 [Chakra UI](https://chakra-ui.com) for the frontend components.
  - 🤖 An automatically generated frontend client.
  - 🧪 [Playwright](https://playwright.dev) for End-to-End testing.
  - 🦇 Dark mode support.
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 📫 Email based password recovery.
- ✅ Tests with [Pytest](https://pytest.org).
- 📞 [Traefik](https://traefik.io) as a reverse proxy / load balancer.
- 🚢 Deployment instructions using Docker Compose, including how to set up a frontend Traefik proxy to handle automatic HTTPS certificates.
- 🏭 CI (continuous integration) and CD (continuous deployment) based on GitHub Actions.
- 📊 PlantUML diagram generation and viewing system.

## PlantUML Diagrams and Utilities

This project includes a PlantUML diagram viewer system for visualizing architecture and code structure. The utils directory has its own virtual environment that can be set up separately from the backend.

### Utils Virtual Environment

The utils directory has its own virtual environment that installs the backend as an editable package. This allows you to run the utils scripts independently while still having access to all the backend code and dependencies.

```bash
# Set up the utils virtual environment
python utils/setup_venv.py

# Or clean and recreate the environment
python utils/setup_venv.py --clean

# Activate the utils virtual environment
# On Windows CMD:
utils\.venv\Scripts\activate
# On Windows Git Bash:
source utils/.venv/Scripts/activate
# On Unix/Linux/Mac:
source utils/.venv/bin/activate
```

For more details, see [utils/README.md](utils/README.md).

### PlantUML Quick Start

```bash
# 1. Render diagrams
python -m utils.puml.cli render

# 2. Start viewer server (keep this running)
cd utils/puml
python -m uvicorn api:app --reload
```

### Dashboard Login

[![API docs](img/login.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Admin

[![API docs](img/dashboard.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Create User

[![API docs](img/dashboard-create.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Items

[![API docs](img/dashboard-items.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - User Settings

[![API docs](img/dashboard-user-settings.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Dark Mode

[![API docs](img/dashboard-dark.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Interactive API Documentation

[![API docs](img/docs.png)](https://github.com/fastapi/full-stack-fastapi-template)

## Documentation

The project includes comprehensive documentation:

- [Backend Development](./backend/README.md)
- [Frontend Development](./frontend/README.md)
- [Deployment Guide](./deployment.md)
- [Development Guide](./development.md)
- [Database Schema Management](docs/database-schema-management.md)
- [Makefile Reference](./MAKEFILE.md)

### Technical Documentation

The project includes detailed technical documentation built with Sphinx. To build and view the documentation:

```bash
# Install development dependencies
cd backend
python -m venv .venv
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate   # Linux/Mac
uv pip install -e ".[dev]"

# Build documentation
make docs

# Build and open documentation in browser
make docs-open
```

The documentation covers:

- Database schema and management
- Backend architecture and API
- Frontend components and state management
- Development workflow
- Deployment procedures

## How To Use It

You can **just fork or clone** this repository and use it as is.

✨ It just works. ✨

### How to Use a Private Repository

If you want to have a private repository, GitHub won't allow you to simply fork it as it doesn't allow changing the visibility of forks.

But you can do the following:

- Create a new GitHub repo, for example `my-full-stack`.
- Clone this repository manually, set the name with the name of the project you want to use, for example `my-full-stack`:

```bash
git clone git@github.com:fastapi/full-stack-fastapi-template.git my-full-stack
```

- Enter into the new directory:

```bash
cd my-full-stack
```

- Set the new origin to your new repository, copy it from the GitHub interface, for example:

```bash
git remote set-url origin git@github.com:octocat/my-full-stack.git
```

- Add this repo as another "remote" to allow you to get updates later:

```bash
git remote add upstream git@github.com:fastapi/full-stack-fastapi-template.git
```

- Push the code to your new repository:

```bash
git push -u origin master
```

### Update From the Original Template

After cloning the repository, and after doing changes, you might want to get the latest changes from this original template.

- Make sure you added the original repository as a remote, you can check it with:

```bash
git remote -v

origin    git@github.com:octocat/my-full-stack.git (fetch)
origin    git@github.com:octocat/my-full-stack.git (push)
upstream    git@github.com:fastapi/full-stack-fastapi-template.git (fetch)
upstream    git@github.com:fastapi/full-stack-fastapi-template.git (push)
```

- Pull the latest changes without merging:

```bash
git pull --no-commit upstream master
```

This will download the latest changes from this template without committing them, that way you can check everything is right before committing.

- If there are conflicts, solve them in your editor.

- Once you are done, commit the changes:

```bash
git merge --continue
```

### Configure

You can then update configs in the `.env` files to customize your configurations.

Before deploying it, make sure you change at least the values for:

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

You can (and should) pass these as environment variables from secrets.

Read the [deployment.md](./deployment.md) docs for more details.

### Generate Secret Keys

Some environment variables in the `.env` file have a default value of `changethis`.

You have to change them with a secret key, to generate secret keys you can run the following command:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the content and use that as password / secret key. And run that again to generate another secure key.

## How To Use It - Alternative With Copier

This repository also supports generating a new project using [Copier](https://copier.readthedocs.io).

It will copy all the files, ask you configuration questions, and update the `.env` files with your answers.

### Install Copier

You can install Copier with:

```bash
pip install copier
```

Or better, if you have [`pipx`](https://pipx.pypa.io/), you can run it with:

```bash
pipx install copier
```

**Note**: If you have `pipx`, installing copier is optional, you could run it directly.

### Generate a Project With Copier

Decide a name for your new project's directory, you will use it below. For example, `my-awesome-project`.

Go to the directory that will be the parent of your project, and run the command with your project's name:

```bash
copier copy https://github.com/fastapi/full-stack-fastapi-template my-awesome-project --trust
```

If you have `pipx` and you didn't install `copier`, you can run it directly:

```bash
pipx run copier copy https://github.com/fastapi/full-stack-fastapi-template my-awesome-project --trust
```

**Note** the `--trust` option is necessary to be able to execute a [post-creation script](https://github.com/fastapi/full-stack-fastapi-template/blob/master/.copier/update_dotenv.py) that updates your `.env` files.

### Input Variables

Copier will ask you for some data, you might want to have at hand before generating the project.

But don't worry, you can just update any of that in the `.env` files afterwards.

The input variables, with their default values (some auto generated) are:

- `project_name`: (default: `"FastAPI Project"`) The name of the project, shown to API users (in .env).
- `stack_name`: (default: `"fastapi-project"`) The name of the stack used for Docker Compose labels and project name (no spaces, no periods) (in .env).
- `secret_key`: (default: `"changethis"`) The secret key for the project, used for security, stored in .env, you can generate one with the method above.
- `first_superuser`: (default: `"admin@example.com"`) The email of the first superuser (in .env).
- `first_superuser_password`: (default: `"changethis"`) The password of the first superuser (in .env).
- `smtp_host`: (default: "") The SMTP server host to send emails, you can set it later in .env.
- `smtp_user`: (default: "") The SMTP server user to send emails, you can set it later in .env.
- `smtp_password`: (default: "") The SMTP server password to send emails, you can set it later in .env.
- `emails_from_email`: (default: `"info@example.com"`) The email account to send emails from, you can set it later in .env.
- `postgres_password`: (default: `"changethis"`) The password for the PostgreSQL database, stored in .env, you can generate one with the method above.
- `sentry_dsn`: (default: "") The DSN for Sentry, if you are using it, you can set it later in .env.

## Backend Development

Backend docs: [backend/README.md](./backend/README.md).

## Frontend Development

Frontend docs: [frontend/README.md](./frontend/README.md).

## Deployment

Deployment docs: [deployment.md](./deployment.md).

## Development

General development docs: [development.md](./development.md).

This includes using Docker Compose, custom local domains, `.env` configurations, etc.

## Code Formatting and Linting

This project uses automated code formatting and linting to maintain consistent code quality:

### Backend (Python)

- **Ruff**: Used for both linting and formatting Python code
  - Configuration in `pyproject.toml` and `.pre-commit-config.yaml`
  - Enforces PEP 8 style guide, import sorting, and other best practices
- **Mypy**: Static type checking for Python
  - Configuration in `pyproject.toml`
  - Runs in strict mode to ensure type safety

### Frontend (TypeScript/JavaScript)

- **Biome**: Modern JavaScript/TypeScript formatter and linter (alternative to Prettier + ESLint)
  - Configuration in `frontend/biome.json`
  - Handles formatting, linting, and import sorting
- **Prettier**: Used for VSCode integration for formatting

### VSCode Integration

The project includes VSCode settings for automatic formatting on save:

1. Install the recommended extensions:

   - [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) for Python
   - [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) for JavaScript/TypeScript

2. The `.vscode/settings.json` file configures:
   - Format on save for all supported file types
   - Automatic import organization
   - Linting as you type

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality before commits:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install
```

## Makefile Support

This project includes a Makefile to simplify common development tasks. You can use commands like:

```bash
# Start the development environment
make up

# Run tests
make test

# Apply database migrations
make migrate
```

For a complete list of available commands and detailed usage instructions, see [MAKEFILE.md](./MAKEFILE.md).

## Release Notes

Check the file [release-notes.md](./release-notes.md).

## License

The Full Stack FastAPI Template is licensed under the terms of the MIT license.
