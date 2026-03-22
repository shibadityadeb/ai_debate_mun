"""Configuration helpers for the application."""
import os
from dataclasses import dataclass, field


def _split_csv(value: str) -> list[str]:
    """Convert a comma-separated env var into a clean list."""
    return [item.strip() for item in value.split(',') if item.strip()]


@dataclass
class Config:
    """App configuration loader."""

    cors_allow_origins: list[str] = field(default_factory=list)
    cors_allow_origin_regex: str | None = None

    @classmethod
    def from_env(cls) -> 'Config':
        """Build configuration from environment variables."""
        default_origins = [
            'http://localhost:3000',
            'http://localhost:5173',
            'https://ai-debate-mun.vercel.app',
            'https://diplomatrix-ai.vercel.app',
        ]
        configured_origins = os.getenv('CORS_ALLOW_ORIGINS', '')
        allow_origins = _split_csv(configured_origins) if configured_origins else default_origins

        return cls(
            cors_allow_origins=allow_origins,
            cors_allow_origin_regex=os.getenv(
                'CORS_ALLOW_ORIGIN_REGEX',
                r'https://.*\.vercel\.app',
            ),
        )
