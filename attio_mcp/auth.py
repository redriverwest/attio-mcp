"""Authentication module for Attio MCP server."""

import logging

from mcp.server.auth.provider import AccessToken, TokenVerifier

from attio_mcp.config import settings

logger = logging.getLogger(__name__)


class BearerTokenVerifier(TokenVerifier):
    """Simple bearer token verifier using environment variable."""

    def verify_token(self, token: str) -> AccessToken | None:
        """
        Verify the bearer token against the configured token.

        Args:
            token: The bearer token to verify

        Returns:
            AccessToken if valid, None if invalid
        """
        expected_token = settings.mcp_bearer_token

        if not expected_token:
            logger.warning("MCP_BEARER_TOKEN not configured - authentication disabled")
            # If no token is configured, allow all requests
            return AccessToken(
                token=token,
                client_id="anonymous",
                scopes=["*"],
                expires_at=None,
                resource=None,
            )

        if token == expected_token:
            logger.debug("Bearer token verified successfully")
            return AccessToken(
                token=token,
                client_id="attio-mcp-client",
                scopes=["*"],
                expires_at=None,
                resource=None,
            )

        logger.warning("Invalid bearer token provided")
        return None
