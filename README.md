# Attio MCP Server

A Model Context Protocol (MCP) server for integrating Attio CRM with AI agents.

## Features

- 🏢 **Company Management**: Search companies, get details, and access notes
- 👥 **People Management**: Search people, get details, and access notes
- 🔒 **Secure**: Bearer token authentication for API access
- 🐳 **Docker Ready**: Containerized for easy deployment
- ⚡ **Efficient**: Built with modern Python async patterns

## Prerequisites

- Python 3.10 or higher
- [UV](https://github.com/astral-sh/uv) package manager
- Attio API key

## Installation

### 1. Install UV (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Setup

```bash
cd /Users/alessadro/Developer/attio-mcp
```

### 3. Create Virtual Environment

```bash
uv venv
```

This creates a `.venv` directory with your virtual environment.

### 4. Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 5. Install Dependencies

```bash
# Install production dependencies
uv pip install -e .

# Install development dependencies (optional)
uv pip install -e ".[dev]"
```

### 6. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your:

- **Attio API key** (required): Get from [Attio's API settings](https://app.attio.com/settings/api)
- **MCP bearer token** (optional): For authentication. Generate with:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

**Note**: If `MCP_BEARER_TOKEN` is not set, the server will run without authentication (useful for development)

## Authentication

The server supports **bearer token authentication** using the MCP SDK's built-in token verification.

### How It Works

1. **Token Configuration**: Set `MCP_BEARER_TOKEN` in your `.env` file
2. **Token Verification**: The server uses a custom `BearerTokenVerifier` to validate incoming tokens
3. **Secure Access**: Only requests with a valid bearer token are allowed

### Authentication Modes

**With Authentication** (Production):

```bash
# .env file
MCP_BEARER_TOKEN=your_secure_token_here
```

The server will:

- ✅ Verify bearer tokens on all requests
- ✅ Reject requests without valid tokens
- ✅ Log authentication attempts

**Without Authentication** (Development):

```bash
# .env file - MCP_BEARER_TOKEN not set or empty
```

The server will:

- ⚠️ Accept all requests without verification
- ⚠️ Log a warning on startup

### Using the Bearer Token

When making requests to the MCP server, include the token in the Authorization header:

```bash
Authorization: Bearer your_secure_token_here
```

### Security Best Practices

1. **Generate Strong Tokens**: Use cryptographically secure random tokens
2. **Keep Tokens Secret**: Never commit tokens to version control
3. **Rotate Tokens**: Change tokens periodically
4. **Use HTTPS**: Always use encrypted connections in production
5. **Enable Authentication**: Always use bearer token auth in production

## Development

### Running the Server

```bash
# Make sure you're in the project directory with venv activated
source .venv/bin/activate
python -m attio_mcp.server
```

Or run directly:

```bash
python attio_mcp/server.py
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy attio_mcp/
```

### Testing

```bash
pytest
```

## Docker Deployment

Coming soon...

## Project Structure

```
attio-mcp/
├── attio_mcp/          # Main package
│   ├── __init__.py
│   ├── server.py       # MCP server implementation
│   ├── attio_client.py # Attio API client
│   ├── config.py       # Configuration management
│   └── tools/          # MCP tools
├── tests/              # Test suite
├── pyproject.toml      # Project configuration
├── Dockerfile          # Docker configuration
└── README.md           # This file
```

## License

MIT
