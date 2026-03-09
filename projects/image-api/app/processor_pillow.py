"""Image processing using Pillow (fallback for environments without libvips)."""
from PIL import Image as PILImage
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
    """Image processor using Pillow (fallback implementation)."""

    FIT_MODES = ("cover", "contain", "fill", "inside", "outside")

    def __init__(self):
        pass

    def load(self, data: bytes) -> PILImage.Image:
        """Load image from bytes."""
        return PILImage.open(BytesIO(data))

    def get_info(self, image: PILImage.Image, format_hint: str = "") -> ImageInfo:
        """Get image information."""
        return ImageInfo(
            width=image.width,
            height=image.height,
            format=format_hint or (image.format.lower() if image.format else "jpeg"),
            size_bytes=0
        )

    def validate(self, image: PILImage.Image) -> None:
        """Validate image dimensions."""
        if image.width > config.max_dimensions[0]:
            raise ValueError(f"Image width {image.width} exceeds max {config.max_dimensions[0]}")
        if image.height > config.max_dimensions[1]:
            raise ValueError(f"Image height {image.height} exceeds max {config.max_dimensions[1]}")

    def resize(
        self,
        image: PILImage.Image,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fit: str = "cover"
    ) -> PILImage.Image:
        """Resize image with fit mode."""
        if not width and not height:
            return image

        fit = fit.lower()
        if fit not in self.FIT_MODES:
            fit = "cover"

        orig_width, orig_height = image.size
        aspect = orig_width / orig_height

        if width and height:
            target_aspect = width / height

            if fit == "cover":
                # Fill area, crop center
                if aspect > target_aspect:
                    new_height = height
                    new_width = int(height * aspect)
                else:
                    new_width = width
                    new_height = int(width / aspect)
                resized = image.resize((new_width, new_height), PILImage.LANCZOS)
                left = (new_width - width) // 2
                top = (new_height - height) // 2
                return resized.crop((left, top, left + width, top + height))

            elif fit == "contain":
                # Fit within, maintain aspect
                if aspect > target_aspect:
                    new_width = width
                    new_height = int(width / aspect)
                else:
                    new_height = height
                    new_width = int(height * aspect)
                return image.resize((new_width, new_height), PILImage.LANCZOS)

            elif fit == "fill":
                # Stretch to exact
                return image.resize((width, height), PILImage.LANCZOS)

            elif fit == "inside":
                scale = min(width / orig_width, height / orig_height)
                new_width = int(orig_width * scale)
                new_height = int(orig_height * scale)
                return image.resize((new_width, new_height), PILImage.LANCZOS)

            elif fit == "outside":
                scale = max(width / orig_width, height / orig_height)
                new_width = int(orig_width * scale)
                new_height = int(orig_height * scale)
                return image.resize((new_width, new_height), PILImage.LANCZOS)

        elif width:
            scale = width / orig_width
            new_height = int(orig_height * scale)
            return image.resize((width, new_height), PILImage.LANCZOS)

        else:
            scale = height / orig_height
            new_width = int(orig_width * scale)
            return image.resize((new_width, height), PILImage.LANCZOS)

    def compress(
        self,
        image: PILImage.Image,
        quality: int = 85,
        format: str = "jpeg"
    ) -> bytes:
        """Compress and encode image."""
        format = format.lower()
        if format == "jpg":
            format = "jpeg"

        buffer = BytesIO()

        if format == "jpeg":
            # Convert to RGB if necessary (JPEG doesn't support alpha)
            if image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGB")
            image.save(buffer, format="JPEG", quality=quality, progressive=True)

        elif format == "png":
            image.save(buffer, format="PNG", compress_level=9)

        elif format == "webp":
            image.save(buffer, format="WEBP", quality=quality)

        else:
            raise ValueError(f"Unsupported format: {format}")

        return buffer.getvalue()

    def convert(
        self,
        image: PILImage.Image,
        format: str,
        quality: int = 85
    ) -> bytes:
        """Convert image to another format."""
        return self.compress(image, quality, format)

    def crop(
        self,
        image: PILImage.Image,
        left: int,
        top: int,
        width: int,
        height: int
    ) -> PILImage.Image:
        """Crop image to specified region."""
        if left < 0 or top < 0:
            raise ValueError("Crop coordinates must be non-negative")
        if left + width > image.width:
            raise ValueError(f"Crop region exceeds image width ({left + width} > {image.width})")
        if top + height > image.height:
            raise ValueError(f"Crop region exceeds image height ({top + height} > {image.height})")

        return image.crop((left, top, left + width, top + height))

    def auto_orient(self, image: PILImage.Image) -> PILImage.Image:
        """Auto-orient image based on EXIF data."""
        from PIL import ImageOps
        try:
            return ImageOps.exif_transpose(image)
        except Exception:
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