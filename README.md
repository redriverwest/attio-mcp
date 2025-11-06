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

- Attio API key
- MCP bearer token (generate a secure random string)

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
