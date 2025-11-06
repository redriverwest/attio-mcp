# Attio MCP Server

MCP server for integrating Attio CRM with AI agents.

## Features

- 🏢 **Companies**: Search companies, get details, and access notes
- 👥 **People**: Search people, get details, and access notes
- 🔒 **Secure**: Bearer token authentication for API access
- 🐳 **Docker Ready**: Containerized for easy deployment

## Prerequisites

- Python 3.10 or higher
- [UV](https://github.com/astral-sh/uv) package manager
- Attio API key

## Installation

```bash
# Clone the repository
git clone https://github.com/redriverwest/attio-mcp.git
cd attio-mcp

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

After installation, configure your environment:

```bash
cp env.example .env
```

Edit `.env` and add your **Attio API key** from [Attio's API settings](https://app.attio.com/settings/api).

## Tools

This MCP server provides the following tools for working with Attio CRM data:

- **search_companies**: Search for companies by name or criteria
- **get_company_details**: Retrieve detailed information about a specific company
- **get_company_notes**: Fetch notes and activity history for a company
- **search_people**: Search for people by name or criteria
- **get_person_details**: Retrieve detailed information about a specific person
- **get_person_notes**: Fetch notes and activity history for a person

## Authentication

The server optionally supports bearer token authentication. To enable it, set `MCP_BEARER_TOKEN` in your `.env` file:

```bash
MCP_BEARER_TOKEN=your_secure_token_here
```

Generate a token with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

When `MCP_BEARER_TOKEN` is set, all requests require the token in the Authorization header:

```bash
Authorization: Bearer your_secure_token_here
```

If not set, the server runs without authentication (useful for development).

## Docker Deployment

### Build and run locally

1. Create a `.env` file with the required variables:

   ```bash
   ATTIO_API_KEY=your_attio_api_key
   MCP_TRANSPORT=sse
   MCP_HOST=0.0.0.0
   MCP_PORT=8080
   # Optional extras
   MCP_BEARER_TOKEN=your_generated_token
   LOG_LEVEL=INFO
   ```

2. Build and start the container:

   ```bash
   docker compose up --build
   ```

   The MCP server listens on the port specified by `MCP_PORT` (defaults to `8080`). Set `MCP_TRANSPORT=stdio` for local CLI usage or `sse` when exposing over HTTP.

### Deploy with Coolify

1. Create a new project in Coolify (e.g., `attio-mcp`) to keep it isolated from existing services.
2. Add a Docker Compose application pointing to this repository and select the `docker-compose.yml` file.
3. Configure environment variables in the Coolify UI:
   - `ATTIO_API_KEY`
   - Optionally `MCP_BEARER_TOKEN`
   - `MCP_TRANSPORT=sse`
   - `MCP_PORT` (match the exposed port, default `8080`)
4. Set the desired domain/FQDN in Coolify to match the `coolify.fqdn` label defined in `docker-compose.yml` (or override via `COOLIFY_FQDN`).
5. Deploy the application. Coolify will handle image builds, networking, and SSL termination.

Adjust resource limits or scaling options within Coolify as needed for your OVH server. Ensure the `coolify` Docker network exists (it is created automatically on first Coolify deployment).
