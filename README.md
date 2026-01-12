# Attio MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for integrating Attio CRM with AI agents. Developed by the tech team of [Red River West](https://redriverwest.com) and [>commit](https://commit.fund/).

## Features

- 🏢 **Companies**: Search companies, retrieve detailed record information, and access internal notes.
- 👥 **People**: Search contacts, get full profiles, and view activity notes.
- 🔒 **Secure**: Optional Bearer token authentication for deployment in non-trusted environments.
- 🐳 **Deployment Ready**: Optimized Docker images and support for both Stdio and SSE transports.

## Prerequisites

- Python 3.10 or higher
- [UV](https://github.com/astral-sh/uv) package manager (recommended) or pip
- Attio API Key

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/redriverwest/attio-mcp.git
cd attio-mcp

# Install using uv
uv pip install -e .

# Or using standard pip
pip install -e .
```

### Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your `ATTIO_API_KEY`.

### Running the Server

You can run the server directly using the installed script:

```bash
# Run with stdio transport (default)
attio-mcp

# Run with SSE transport
MCP_TRANSPORT=sse attio-mcp
```

## Tools

| Tool                  | Description                                            |
| --------------------- | ------------------------------------------------------ |
| `search_companies`    | Search for companies by name or domain.                |
| `get_company_details` | Retrieve all attributes for a specific company record. |
| `get_company_notes`   | Fetch all internal notes linked to a company.          |
| `search_people`       | Find contacts by name or email address.                |
| `get_person_details`  | Get comprehensive details for a specific person.       |
| `get_person_notes`    | Retrieve activity history and notes for a contact.     |

## Authentication

When exposing the server over HTTP (SSE transport), you should enable bearer token authentication:

1. Generate a secure token:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
2. Set `MCP_BEARER_TOKEN` in your `.env`.
3. Client requests must include `Authorization: Bearer <your_token>`.

## Docker Deployment

### Local Development

To run the server locally with Docker Compose:

```bash
docker compose -f deploy/docker-compose.local.yml up --build
```

This will build and run the server with port mapping to your host (default `8080`).

### Production Deployment

For production environments, you can use `deploy/docker-compose.yml` as a base. It is designed to be minimal and transport-agnostic.

## Development

### Setup

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### Testing

```bash
pytest
```

### Linting & Types

```bash
ruff check .
black .
mypy .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
