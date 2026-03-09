"""Image Optimization API - Main Application."""
import time
import hashlib
import logging
import os
from typing import Optional
from io import BytesIO
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Response, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import config
from app.processor import ImageProcessor, ProcessResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting configuration
# Default: 100 requests per minute per IP for API endpoints
RATE_LIMIT_PER_MINUTE = os.getenv("RATE_LIMIT_PER_MINUTE", "100")

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Image Optimization API",
    description="Self-hosted image optimization with excellent performance",
    version="0.1.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Prometheus metrics
IMAGES_PROCESSED = Counter(
    "image_api_images_processed_total",
    "Total number of images processed",
    ["operation", "format"]
)
PROCESSING_TIME = Histogram(
    "image_api_processing_time_seconds",
    "Time spent processing images",
    ["operation"]
)
COMPRESSION_RATIO = Histogram(
    "image_api_compression_ratio",
    "Compression ratio achieved",
    ["format"]
)
ERRORS = Counter(
    "image_api_errors_total",
    "Total number of errors",
    ["operation", "error_type"]
)

# CORS for browser usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = ImageProcessor()


def validate_file(file: UploadFile) -> bytes:
    """Validate and read uploaded file."""
    # Check content type
    allowed_types = ("image/jpeg", "image/png", "image/webp", "image/gif")
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported content type: {file.content_type}"
        )
    
    # Read content
    content = file.file.read()
    
    # Check size
    max_bytes = config.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size is {config.max_file_size_mb}MB"
        )
    
    # Validate magic bytes
    if len(content) < 8:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # Check magic bytes for supported formats
    magic = content[:16]
    if magic[:8] == b'\x89PNG\r\n\x1a\n':
        pass  # PNG
    elif magic[:2] == b'\xff\xd8':
        pass  # JPEG
    elif magic[:4] == b'RIFF' and magic[8:12] == b'WEBP':
        pass  # WebP
    elif magic[:6] in (b'GIF87a', b'GIF89a'):
        pass  # GIF
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format. Supported: JPEG, PNG, WebP, GIF"
        )
    
    return content


@app.get("/v1/health")
@limiter.exempt
async def health(request: Request):
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/v1/metrics", response_class=PlainTextResponse)
@limiter.exempt
async def metrics(request: Request):
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.post("/v1/optimize")
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
async def optimize(
    request: Request,
    image: UploadFile = File(...),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None),
    quality: int = Form(85),
    format: Optional[str] = Form(None),
    fit: str = Form("cover"),
):
    """
    Optimize an image with multiple operations.
    
    - **image**: Image file to optimize
    - **width**: Target width in pixels
    - **height**: Target height in pixels
    - **quality**: Output quality (1-100, default: 85)
    - **format**: Output format (jpeg, png, webp)
    - **fit**: Resize fit mode (cover, contain, fill)
    """
    start_time = time.time()
    
    try:
        # Validate and read
        content = validate_file(image)
        
        # Build operations
        operations = {"quality": quality}
        
        if width or height:
            operations["resize"] = {
                "width": width,
                "height": height,
                "fit": fit
            }
        
        if format:
            format = format.lower()
            if format not in config.output_formats:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported output format: {format}. Supported: {config.output_formats}"
                )
            operations["format"] = format
        else:
            # Infer from input
            if image.content_type == "image/png":
                operations["format"] = "png"
            elif image.content_type == "image/webp":
                operations["format"] = "webp"
            else:
                operations["format"] = "jpeg"
        
        # Process
        output, original_info, output_info = processor.process(content, operations)
        
        # Calculate metrics
        processing_time = time.time() - start_time
        compression_ratio = output_info.size_bytes / original_info.size_bytes if original_info.size_bytes > 0 else 1.0
        
        # Record metrics
        IMAGES_PROCESSED.labels(operation="optimize", format=operations["format"]).inc()
        PROCESSING_TIME.labels(operation="optimize").observe(processing_time)
        COMPRESSION_RATIO.labels(format=operations["format"]).observe(compression_ratio)
        
        logger.info(
            f"Optimized image: {original_info.width}x{original_info.height} -> "
            f"{output_info.width}x{output_info.height}, "
            f"{original_info.size_bytes} -> {output_info.size_bytes} bytes, "
            f"ratio: {compression_ratio:.2%}, time: {processing_time*1000:.0f}ms"
        )
        
        # Build response
        media_type = f"image/{operations['format']}"
        headers = {
            "X-Original-Size": str(original_info.size_bytes),
            "X-Optimized-Size": str(output_info.size_bytes),
            "X-Original-Dimensions": f"{original_info.width}x{original_info.height}",
            "X-Output-Dimensions": f"{output_info.width}x{output_info.height}",
            "X-Compression-Ratio": f"{compression_ratio:.4f}",
            "X-Processing-Time-Ms": f"{processing_time * 1000:.0f}",
        }
        
        return Response(
            content=output,
            media_type=media_type,
            headers=headers
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        ERRORS.labels(operation="optimize", error_type="validation").inc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        ERRORS.labels(operation="optimize", error_type="processing").inc()
        logger.exception(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/v1/convert")
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
async def convert(
    request: Request,
    image: UploadFile = File(...),
    format: str = Form(...),
    quality: int = Form(85),
):
    """
    Convert image to another format.
    
    - **image**: Image file to convert
    - **format**: Target format (jpeg, png, webp)
    - **quality**: Output quality (1-100, default: 85)
    """
    start_time = time.time()
    
    try:
        # Validate format
        format = format.lower()
        if format not in config.output_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {format}. Supported: {config.output_formats}"
            )
        
        # Validate and read
        content = validate_file(image)
        
        # Process
        operations = {
            "quality": quality,
            "format": format
        }
        output, original_info, output_info = processor.process(content, operations)
        
        # Calculate metrics
        processing_time = time.time() - start_time
        
        # Record metrics
        IMAGES_PROCESSED.labels(operation="convert", format=format).inc()
        PROCESSING_TIME.labels(operation="convert").observe(processing_time)
        
        logger.info(
            f"Converted image: {original_info.format} -> {format}, "
            f"time: {processing_time*1000:.0f}ms"
        )
        
        return Response(
            content=output,
            media_type=f"image/{format}",
            headers={
                "X-Original-Size": str(original_info.size_bytes),
                "X-Converted-Size": str(output_info.size_bytes),
                "X-Processing-Time-Ms": f"{processing_time * 1000:.0f}",
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        ERRORS.labels(operation="convert", error_type="validation").inc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        ERRORS.labels(operation="convert", error_type="processing").inc()
        logger.exception(f"Error converting image: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


@app.post("/v1/resize")
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
async def resize(
    request: Request,
    image: UploadFile = File(...),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None),
    fit: str = Form("cover"),
    quality: int = Form(85),
):
    """
    Resize an image.
    
    - **image**: Image file to resize
    - **width**: Target width in pixels
    - **height**: Target height in pixels
    - **fit**: Fit mode (cover, contain, fill)
    - **quality**: Output quality (1-100, default: 85)
    """
    if not width and not height:
        raise HTTPException(
            status_code=400,
            detail="At least one of width or height must be specified"
        )
    
    start_time = time.time()
    
    try:
        content = validate_file(image)
        
        # Infer format
        if image.content_type == "image/png":
            output_format = "png"
        elif image.content_type == "image/webp":
            output_format = "webp"
        else:
            output_format = "jpeg"
        
        operations = {
            "resize": {
                "width": width,
                "height": height,
                "fit": fit
            },
            "quality": quality,
            "format": output_format
        }
        
        output, original_info, output_info = processor.process(content, operations)
        
        processing_time = time.time() - start_time
        
        IMAGES_PROCESSED.labels(operation="resize", format=output_format).inc()
        PROCESSING_TIME.labels(operation="resize").observe(processing_time)
        
        return Response(
            content=output,
            media_type=f"image/{output_format}",
            headers={
                "X-Original-Dimensions": f"{original_info.width}x{original_info.height}",
                "X-Output-Dimensions": f"{output_info.width}x{output_info.height}",
                "X-Processing-Time-Ms": f"{processing_time * 1000:.0f}",
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        ERRORS.labels(operation="resize", error_type="validation").inc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        ERRORS.labels(operation="resize", error_type="processing").inc()
        logger.exception(f"Error resizing image: {e}")
        raise HTTPException(status_code=500, detail=f"Resize error: {str(e)}")


@app.post("/v1/crop")
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
async def crop(
    request: Request,
    image: UploadFile = File(...),
    left: int = Form(0),
    top: int = Form(0),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None),
    quality: int = Form(85),
):
    """
    Crop an image.
    
    - **image**: Image file to crop
    - **left**: Left offset in pixels
    - **top**: Top offset in pixels
    - **width**: Crop width (defaults to remaining width)
    - **height**: Crop height (defaults to remaining height)
    - **quality**: Output quality (1-100, default: 85)
    """
    start_time = time.time()
    
    try:
        content = validate_file(image)
        
        # Infer format
        if image.content_type == "image/png":
            output_format = "png"
        elif image.content_type == "image/webp":
            output_format = "webp"
        else:
            output_format = "jpeg"
        
        operations = {
            "crop": {
                "left": left,
                "top": top,
                "width": width,
                "height": height
            },
            "quality": quality,
            "format": output_format
        }
        
        output, original_info, output_info = processor.process(content, operations)
        
        processing_time = time.time() - start_time
        
        IMAGES_PROCESSED.labels(operation="crop", format=output_format).inc()
        PROCESSING_TIME.labels(operation="crop").observe(processing_time)
        
        return Response(
            content=output,
            media_type=f"image/{output_format}",
            headers={
                "X-Original-Dimensions": f"{original_info.width}x{original_info.height}",
                "X-Output-Dimensions": f"{output_info.width}x{output_info.height}",
                "X-Processing-Time-Ms": f"{processing_time * 1000:.0f}",
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        ERRORS.labels(operation="crop", error_type="validation").inc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        ERRORS.labels(operation="crop", error_type="processing").inc()
        logger.exception(f"Error cropping image: {e}")
        raise HTTPException(status_code=500, detail=f"Crop error: {str(e)}")


# Root endpoint with API info
@app.get("/")
@limiter.exempt
async def root(request: Request):
    """API information."""
    return {
        "name": "Image Optimization API",
        "version": "0.1.0",
        "endpoints": {
            "optimize": "/v1/optimize",
            "convert": "/v1/convert",
            "resize": "/v1/resize",
            "crop": "/v1/crop",
            "health": "/v1/health",
            "metrics": "/v1/metrics"
        },
        "limits": {
            "max_file_size_mb": config.max_file_size_mb,
            "max_dimensions": f"{config.max_dimensions[0]}x{config.max_dimensions[1]}",
            "supported_formats": config.supported_formats
        }
    }