"""Image processing using pyvips (libvips)."""
import pyvips
from io import BytesIO
from typing import Optional
from dataclasses import dataclass

from app.config import config


@dataclass
class ImageInfo:
    """Image metadata."""
    width: int
    height: int
    format: str
    size_bytes: int


@dataclass
class ProcessResult:
    """Processing result."""
    data: bytes
    original_info: ImageInfo
    output_info: ImageInfo
    processing_time_ms: float


class ImageProcessor:
    """Image processor using libvips."""

    FIT_MODES = ("cover", "contain", "fill", "inside", "outside")

    def __init__(self):
        # Set memory limits
        pyvips.cache_set_max(config.max_memory_per_request_mb * 1024 * 1024)

    def load(self, data: bytes) -> pyvips.Image:
        """Load image from bytes."""
        return pyvips.Image.new_from_buffer(data, "")

    def get_info(self, image: pyvips.Image, format_hint: str = "") -> ImageInfo:
        """Get image information."""
        return ImageInfo(
            width=image.width,
            height=image.height,
            format=format_hint,
            size_bytes=0  # Will be set by caller
        )

    def validate(self, image: pyvips.Image) -> None:
        """Validate image dimensions."""
        if image.width > config.max_dimensions[0]:
            raise ValueError(f"Image width {image.width} exceeds max {config.max_dimensions[0]}")
        if image.height > config.max_dimensions[1]:
            raise ValueError(f"Image height {image.height} exceeds max {config.max_dimensions[1]}")

    def resize(
        self,
        image: pyvips.Image,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fit: str = "cover"
    ) -> pyvips.Image:
        """Resize image with fit mode."""
        if not width and not height:
            return image

        fit = fit.lower()
        if fit not in self.FIT_MODES:
            fit = "cover"

        # Calculate scale
        if width and height:
            scale_x = width / image.width
            scale_y = height / image.height

            if fit == "cover":
                # Fill area, may crop
                scale = max(scale_x, scale_y)
                resized = image.resize(scale)
                # Center crop to exact dimensions
                left = (resized.width - width) // 2
                top = (resized.height - height) // 2
                return resized.crop(left, top, width, height)

            elif fit == "contain":
                # Fit within area, maintain aspect
                scale = min(scale_x, scale_y)
                return image.resize(scale)

            elif fit == "fill":
                # Stretch to exact dimensions
                return image.resize(scale_x, vscale=scale_y)

            elif fit == "inside":
                # Fit within, no crop, never exceed
                scale = min(scale_x, scale_y)
                return image.resize(scale)

            elif fit == "outside":
                # Cover area, may exceed
                scale = max(scale_x, scale_y)
                return image.resize(scale)

        elif width:
            scale = width / image.width
            return image.resize(scale)

        else:  # height only
            scale = height / image.height
            return image.resize(scale)

    def compress(
        self,
        image: pyvips.Image,
        quality: int = 85,
        format: str = "jpeg"
    ) -> bytes:
        """Compress and encode image."""
        format = format.lower()
        if format == "jpg":
            format = "jpeg"

        options = {}

        if format == "jpeg":
            options = {
                "Q": quality,
                "interlace": True,  # Progressive JPEG
                "strip": True,  # Remove metadata
            }
        elif format == "png":
            options = {
                "compression": 9,
                "strip": True,
            }
        elif format == "webp":
            options = {
                "Q": quality,
                "strip": True,
            }
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Add alpha channel handling for JPEG
        if format == "jpeg" and image.has_alpha():
            # Composite onto white background
            background = pyvips.Image.black(image.width, image.height)
            background = background.add(255).cast("uchar")
            if image.bands == 4:
                image = image.composite2(background, "over")
            elif image.bands == 2:  # Grayscale + alpha
                image = image.extract_band(0).add(background)

        return image.write_to_buffer(f".{format}", **options)

    def convert(
        self,
        image: pyvips.Image,
        format: str,
        quality: int = 85
    ) -> bytes:
        """Convert image to another format."""
        return self.compress(image, quality, format)

    def crop(
        self,
        image: pyvips.Image,
        left: int,
        top: int,
        width: int,
        height: int
    ) -> pyvips.Image:
        """Crop image to specified region."""
        if left < 0 or top < 0:
            raise ValueError("Crop coordinates must be non-negative")
        if left + width > image.width:
            raise ValueError(f"Crop region exceeds image width ({left + width} > {image.width})")
        if top + height > image.height:
            raise ValueError(f"Crop region exceeds image height ({top + height} > {image.height})")

        return image.crop(left, top, width, height)

    def auto_orient(self, image: pyvips.Image) -> pyvips.Image:
        """Auto-orient image based on EXIF data."""
        if "exif-ifd0-Orientation" in image.get_fields():
            orientation = image.get("exif-ifd0-Orientation")
            # Handle orientation
            if orientation == 2:
                image = image.flip("horizontal")
            elif orientation == 3:
                image = image.rot("d180")
            elif orientation == 4:
                image = image.flip("vertical")
            elif orientation == 5:
                image = image.rot("d90").flip("horizontal")
            elif orientation == 6:
                image = image.rot("d90")
            elif orientation == 7:
                image = image.rot("d270").flip("horizontal")
            elif orientation == 8:
                image = image.rot("d270")
        return image

    def process(
        self,
        data: bytes,
        operations: dict
    ) -> tuple[bytes, ImageInfo, ImageInfo]:
        """Process image with operations."""
        import time
        start = time.time()

        # Load
        image = self.load(data)
        original_info = self.get_info(image)
        original_info.size_bytes = len(data)

        # Validate
        self.validate(image)

        # Auto-orient based on EXIF
        image = self.auto_orient(image)

        # Apply operations
        if "crop" in operations:
            crop = operations["crop"]
            image = self.crop(
                image,
                crop.get("left", 0),
                crop.get("top", 0),
                crop.get("width", image.width),
                crop.get("height", image.height)
            )

        if "resize" in operations:
            resize = operations["resize"]
            image = self.resize(
                image,
                width=resize.get("width"),
                height=resize.get("height"),
                fit=resize.get("fit", "cover")
            )

        # Output
        quality = operations.get("quality", config.default_quality)
        format = operations.get("format", "jpeg")

        output = self.compress(image, quality, format)

        # Get output info
        output_image = self.load(output)
        output_info = self.get_info(output_image, format)
        output_info.size_bytes = len(output)

        return output, original_info, output_info