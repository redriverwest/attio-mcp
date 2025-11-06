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
cp .env.example .env
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
