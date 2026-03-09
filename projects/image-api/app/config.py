"""Configuration for Image Optimization API."""
import os
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Limits
    max_file_size_mb: int = 20
    max_dimensions: tuple[int, int] = (10000, 10000)
    max_memory_per_request_mb: int = 100
    
    # Processing defaults
    default_quality: int = 85
    default_fit: str = "cover"
    
    # Supported formats
    supported_formats: tuple = ("jpeg", "jpg", "png", "webp")
    output_formats: tuple = ("jpeg", "png", "webp")
    
    # Redis (optional caching)
    redis_url: str = ""
    cache_ttl_seconds: int = 3600
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "20")),
            max_memory_per_request_mb=int(os.getenv("MAX_MEMORY_PER_REQUEST_MB", "100")),
            redis_url=os.getenv("REDIS_URL", ""),
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "3600")),
        )


config = Config.from_env()