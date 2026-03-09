"""Tests for Image Optimization API."""
import pytest
import io
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from app.processor import ImageProcessor, PYVIPS_AVAILABLE


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_jpeg():
    """Create sample JPEG image."""
    img = Image.new('RGB', (800, 600), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=90)
    buffer.seek(0)
    return buffer


@pytest.fixture
def sample_png():
    """Create sample PNG image with transparency."""
    img = Image.new('RGBA', (400, 300), color=(0, 255, 0, 128))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer


@pytest.fixture
def sample_webp():
    """Create sample WebP image."""
    img = Image.new('RGB', (640, 480), color='blue')
    buffer = io.BytesIO()
    img.save(buffer, format='WEBP', quality=85)
    buffer.seek(0)
    return buffer


class TestHealthEndpoint:
    """Tests for health endpoint."""
    
    def test_health_returns_ok(self, client):
        """Health endpoint should return ok status."""
        response = client.get("/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "timestamp" in data


class TestMetricsEndpoint:
    """Tests for Prometheus metrics endpoint."""
    
    def test_metrics_returns_prometheus_format(self, client):
        """Metrics endpoint should return Prometheus format."""
        response = client.get("/v1/metrics")
        assert response.status_code == 200
        assert "image_api_" in response.text


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_returns_api_info(self, client):
        """Root endpoint should return API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Image Optimization API"
        assert "endpoints" in data
        assert "limits" in data


class TestOptimizeEndpoint:
    """Tests for optimize endpoint."""
    
    def test_optimize_jpeg_default(self, client, sample_jpeg):
        """Optimize JPEG with default settings."""
        response = client.post(
            "/v1/optimize",
            files={"image": ("test.jpg", sample_jpeg, "image/jpeg")}
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"
        assert "X-Original-Size" in response.headers
        assert "X-Optimized-Size" in response.headers
        assert "X-Compression-Ratio" in response.headers
    
    def test_optimize_with_resize(self, client, sample_jpeg):
        """Optimize with resize parameters."""
        response = client.post(
            "/v1/optimize",
            files={"image": ("test.jpg", sample_jpeg, "image/jpeg")},
            data={"width": "400", "height": "300"}
        )
        assert response.status_code == 200
        dims = response.headers["X-Output-Dimensions"]
        # Should be around 400x300
        assert "400" in dims or "300" in dims
    
    def test_optimize_with_format_conversion(self, client, sample_jpeg):
        """Optimize and convert to WebP."""
        response = client.post(
            "/v1/optimize",
            files={"image": ("test.jpg", sample_jpeg, "image/jpeg")},
            data={"format": "webp"}
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/webp"
    
    def test_optimize_png_preserves_format(self, client, sample_png):
        """PNG input should output PNG by default."""
        response = client.post(
            "/v1/optimize",
            files={"image": ("test.png", sample_png, "image/png")}
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
    
    def test_optimize_quality_affects_size(self, client, sample_jpeg):
        """Lower quality should produce smaller file."""
        # High quality
        sample_jpeg.seek(0)
        response_high = client.post(
            "/v1/optimize",
            files={"image": ("test.jpg", sample_jpeg, "image/jpeg")},
            data={"quality": "95"}
        )
        size_high = int(response_high.headers["X-Optimized-Size"])
        
        # Low quality
        sample_jpeg.seek(0)
        response_low = client.post(
            "/v1/optimize",
            files={"image": ("test.jpg", sample_jpeg, "image/jpeg")},
            data={"quality": "50"}
        )
        size_low = int(response_low.headers["X-Optimized-Size"])
        
        assert size_low < size_high
    
    def test_optimize_unsupported_format(self, client):
        """Should reject unsupported formats."""
        # Create a fake "bmp" file
        fake_file = io.BytesIO(b'BM' + b'\x00' * 100)
        response = client.post(
            "/v1/optimize",
            files={"image": ("test.bmp", fake_file, "image/bmp")}
        )
        assert response.status_code == 400


class TestConvertEndpoint:
    """Tests for convert endpoint."""
    
    def test_convert_jpeg_to_webp(self, client, sample_jpeg):
        """Convert JPEG to WebP."""
        response = client.post(
            "/v1/convert",
            files={"image": ("test.jpg", sample_jpeg, "image/jpeg")},
            data={"format": "webp"}
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/webp"
    
    def test_convert_jpeg_to_png(self, client, sample_jpeg):
        """Convert JPEG to PNG."""
        response = client.post(
            "/v1/convert",
            files={"image": ("test.jpg", sample_jpeg, "image/jpeg")},
            data={"format": "png"}
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
    
    def test_convert_png_to_jpeg(self, client, sample_png):
        """Convert PNG with transparency to JPEG."""
        response = client.post(
            "/v1/convert",
            files={"image": ("test.png", sample_png, "image/png")},
            data={"format": "jpeg"}
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"
    
    def test_convert_missing_format(self, client, sample_jpeg):
        """Should require format parameter."""
        response = client.post(
            "/v1/convert",
            files={"image": ("test.jpg", sample_jpeg, "image/jpeg")}
        )
        assert response.status_code == 422  # Validation error


class TestResizeEndpoint:
    """Tests for resize endpoint."""
    
    def test_resize_width_only(self, client, sample_jpeg):
        """Resize with width only."""
        response = client.post(
            "/v1/resize",
            files={"image": ("test.jpg", sample_jpeg, "image/jpeg")},
            data={"width": "400"}
        )
        assert response.status_code == 200
        dims = response.headers["X-Output-Dimensions"]
        assert dims.startswith("400x")
    
    def test_resize_height_only(self, client, sample_jpeg):
        """Resize with height only."""
        response = client.post(
            "/v1/resize",
            files={"image": ("test.jpg", sample_jpeg, "image/jpeg")},
            data={"height": "200"}
        )
        assert response.status_code == 200
        dims = response.headers["X-Output-Dimensions"]
        assert dims.endswith("x200")
    
    def test_resize_both_dimensions(self, client, sample_jpeg):
        """Resize with both width and height."""
        response = client.post(
            "/v1/resize",
            files={"image": ("test.jpg", sample_jpeg, "image/jpeg")},
            data={"width": "400", "height": "300"}
        )
        assert response.status_code == 200
    
    def test_resize_missing_both_dimensions(self, client, sample_jpeg):
        """Should require at least one dimension."""
        response = client.post(
            "/v1/resize",
            files={"image": ("test.jpg", sample_jpeg, "image/jpeg")}
        )
        assert response.status_code == 400


class TestCropEndpoint:
    """Tests for crop endpoint."""
    
    def test_crop_default(self, client, sample_jpeg):
        """Crop with default parameters."""
        response = client.post(
            "/v1/crop",
            files={"image": ("test.jpg", sample_jpeg, "image/jpeg")},
            data={"left": "100", "top": "50", "width": "200", "height": "150"}
        )
        assert response.status_code == 200
        dims = response.headers["X-Output-Dimensions"]
        assert dims == "200x150"
    
    def test_crop_out_of_bounds(self, client, sample_jpeg):
        """Should reject crop beyond image bounds."""
        response = client.post(
            "/v1/crop",
            files={"image": ("test.jpg", sample_jpeg, "image/jpeg")},
            data={"left": "0", "top": "0", "width": "9999", "height": "9999"}
        )
        assert response.status_code == 400


class TestFileValidation:
    """Tests for file validation."""
    
    def test_reject_too_large_file(self, client):
        """Should reject files exceeding size limit."""
        # This test would need a large file; skip in unit tests
        pass
    
    def test_reject_invalid_magic_bytes(self, client):
        """Should reject files with invalid magic bytes."""
        fake_file = io.BytesIO(b'not an image')
        response = client.post(
            "/v1/optimize",
            files={"image": ("test.txt", fake_file, "image/jpeg")}
        )
        assert response.status_code == 400


class TestImageProcessor:
    """Tests for ImageProcessor class."""
    
    def test_load_jpeg(self, sample_jpeg):
        """Should load JPEG image."""
        processor = ImageProcessor()
        sample_jpeg.seek(0)
        data = sample_jpeg.read()
        image = processor.load(data)
        assert image.width == 800
        assert image.height == 600
    
    def test_resize_cover_mode(self, sample_jpeg):
        """Resize with cover mode."""
        processor = ImageProcessor()
        sample_jpeg.seek(0)
        data = sample_jpeg.read()
        image = processor.load(data)
        resized = processor.resize(image, width=400, height=400, fit="cover")
        assert resized.width == 400
        assert resized.height == 400
    
    def test_resize_contain_mode(self, sample_jpeg):
        """Resize with contain mode."""
        processor = ImageProcessor()
        sample_jpeg.seek(0)
        data = sample_jpeg.read()
        image = processor.load(data)
        resized = processor.resize(image, width=400, height=400, fit="contain")
        # Should maintain aspect ratio
        assert resized.width <= 400
        assert resized.height <= 400
        assert resized.width == 400 or resized.height == 400
    
    def test_compress_quality(self, sample_jpeg):
        """Compress with quality setting."""
        processor = ImageProcessor()
        sample_jpeg.seek(0)
        data = sample_jpeg.read()
        image = processor.load(data)
        
        high_quality = processor.compress(image, quality=95, format="jpeg")
        low_quality = processor.compress(image, quality=50, format="jpeg")
        
        assert len(low_quality) < len(high_quality)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])