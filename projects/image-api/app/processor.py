"""Image processing with auto-detect backend (pyvips preferred, Pillow fallback)."""
from io import BytesIO
from typing import Optional
from dataclasses import dataclass

from app.config import config

# Auto-detect backend
try:
    import pyvips
    # Test if libvips is actually available
    pyvips.Operation.new("black")
    PYVIPS_AVAILABLE = True
except (ImportError, OSError, Exception):
    PYVIPS_AVAILABLE = False

if PYVIPS_AVAILABLE:
    from app.processor_pyvips import ImageProcessor as PyvipsProcessor
    from app.processor_pyvips import ImageInfo, ProcessResult
else:
    from app.processor_pillow import ImageProcessor as PillowProcessor
    from app.processor_pillow import ImageInfo, ProcessResult


class ImageProcessor:
    """Image processor with auto-detected backend."""

    def __init__(self):
        if PYVIPS_AVAILABLE:
            self._impl = PyvipsProcessor()
            self._backend = "pyvips"
        else:
            self._impl = PillowProcessor()
            self._backend = "pillow"

    @property
    def backend(self) -> str:
        """Return the active backend."""
        return self._backend

    def load(self, data: bytes):
        """Load image from bytes."""
        return self._impl.load(data)

    def get_info(self, image, format_hint: str = "") -> ImageInfo:
        """Get image information."""
        return self._impl.get_info(image, format_hint)

    def validate(self, image) -> None:
        """Validate image dimensions."""
        return self._impl.validate(image)

    def resize(self, image, width: Optional[int] = None, height: Optional[int] = None, fit: str = "cover"):
        """Resize image with fit mode."""
        return self._impl.resize(image, width, height, fit)

    def compress(self, image, quality: int = 85, format: str = "jpeg") -> bytes:
        """Compress and encode image."""
        return self._impl.compress(image, quality, format)

    def convert(self, image, format: str, quality: int = 85) -> bytes:
        """Convert image to another format."""
        return self._impl.convert(image, format, quality)

    def crop(self, image, left: int, top: int, width: int, height: int):
        """Crop image to specified region."""
        return self._impl.crop(image, left, top, width, height)

    def auto_orient(self, image):
        """Auto-orient image based on EXIF data."""
        return self._impl.auto_orient(image)

    def process(self, data: bytes, operations: dict) -> tuple[bytes, ImageInfo, ImageInfo]:
        """Process image with operations."""
        return self._impl.process(data, operations)