# Assets Directory

This directory contains test resources for the DocumentVisionX API.

## Test Images

### Directory Structure

```
assets/test_images/
├── aadhar/          # Aadhaar card test images
├── pancard/         # PAN card test images
├── voter/           # Voter ID card test images
└── bank/            # Bank document test images
```

### Usage

Add sample document images to the respective subdirectories for testing:

- **Aadhaar**: Place Aadhaar card images in `test_images/aadhar/`
- **PAN Card**: Place PAN card images in `test_images/pancard/`
- **Voter ID**: Place Voter ID card images in `test_images/voter/`
- **Bank Documents**: Place bank statement/passbook/cheque images in `test_images/bank/`

### API Testing

You can test the API endpoints using curl with images from these directories:

```bash
# Test Aadhaar extraction
curl -X POST http://localhost:8000/aadhar/extract \
  -F "document_type=aadhar" \
  -F "file=@assets/test_images/aadhar/sample_aadhar.jpg"

# Test PAN extraction
curl -X POST http://localhost:8000/pancard/extract \
  -F "document_type=pancard" \
  -F "file=@assets/test_images/pancard/sample_pan.jpg"

# Test Voter ID extraction
curl -X POST http://localhost:8000/voter/extract \
  -F "document_type=voter" \
  -F "file=@assets/test_images/voter/sample_voter.jpg"

# Test Bank extraction
curl -X POST http://localhost:8000/bank/extract \
  -F "document_type=bank" \
  -F "file=@assets/test_images/bank/sample_bank.jpg"
```

### Python Testing

```python
import requests

# Test Aadhaar endpoint
with open('assets/test_images/aadhar/sample_aadhar.jpg', 'rb') as f:
    files = {'file': f}
    data = {'document_type': 'aadhar'}
    response = requests.post(
        'http://localhost:8000/aadhar/extract',
        files=files,
        data=data
    )
    print(response.json())
```

### Performance Metrics

After running tests, check the `/metrics` endpoint to view performance data:

```bash
curl http://localhost:8000/metrics | jq
```

This will show:
- Average extraction time per document type
- Min/max/percentile (p50, p95) latencies
- Total number of operations
