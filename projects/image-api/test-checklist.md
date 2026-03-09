# Test Checklist - Image API

**Version**: 0.1.0
**Test Date**: 2026-03-09
**Tester**: qa-bach

## Core Functionality

### API Endpoints
- [x] GET /v1/health returns ok status
- [x] GET /v1/metrics returns Prometheus format
- [x] GET / returns API info
- [x] POST /v1/optimize processes images
- [x] POST /v1/convert converts formats
- [x] POST /v1/resize resizes images
- [x] POST /v1/crop crops images

### Image Operations
- [x] JPEG optimization works
- [x] PNG optimization works
- [x] WebP optimization works
- [x] Resize with width only
- [x] Resize with height only
- [x] Resize with both dimensions
- [x] Resize fit modes (cover, contain, fill)
- [x] Format conversion (JPEG↔PNG↔WebP)
- [x] Quality affects file size
- [x] Crop with coordinates

## Edge Cases

### Input Validation
- [x] Reject unsupported formats (BMP, TIFF)
- [x] Reject invalid magic bytes
- [x] Require format parameter for /convert
- [x] Require dimensions for /resize
- [x] Reject crop out of bounds

### Error Handling
- [x] 400 for invalid input
- [x] 422 for missing required params
- [x] Proper error messages returned

## Performance

### Response Times (Pillow backend)
- [x] Optimize < 100ms for 800x600
- [x] Resize < 50ms for 800x600
- [x] Convert < 100ms for 800x600
- [x] Crop < 50ms for 800x600

## Security

### Input Validation
- [x] File size limit enforced (20MB)
- [x] Magic byte validation
- [x] Content-type validation
- [x] Dimension limits (10000x10000)

## Test Results Summary

| Category | Tests | Passed | Failed |
|----------|-------|--------|--------|
| API Endpoints | 3 | 3 | 0 |
| Optimize | 6 | 6 | 0 |
| Convert | 4 | 4 | 0 |
| Resize | 4 | 4 | 0 |
| Crop | 2 | 2 | 0 |
| Validation | 4 | 4 | 0 |
| Processor | 4 | 4 | 0 |
| **Total** | **27** | **27** | **0** |

**Overall Status**: ✅ PASS

## Notes

- All tests executed with Pillow backend (pyvips not available in test environment)
- pyvips import issue fixed in processor.py
- Test suite covers all documented API functionality