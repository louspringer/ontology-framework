# AbemaTV Extractor Security Documentation

## Overview

The AbemaTV extractor is a component of yt-dlp that handles video extraction from AbemaTV, a Japanese streaming service. This document outlines the security requirements and implementation details for handling sensitive data.

## Security Requirements

1. **Environment Variables**
   - `ABEMA_HKEY`: The HMAC key for video key decryption
   - `ABEMA_SECRET_KEY`: The secret key for application authentication

2. **Default Values**
   - Default values are provided for testing purposes only
   - Production deployments MUST set proper environment variables
   - Warnings will be issued when falling back to defaults

## Implementation Details

### Secret Management

```python
def get_secret_from_env(key, default=None, encoding='utf-8'):
    """Safely retrieve secrets from environment variables with proper warnings."""
    value = os.environ.get(key)
    if not value and default:
        warnings.warn(
            f"{key} not found in environment variables, using default value. "
            "This is insecure and should only be used for testing.",
            RuntimeWarning
        )
        return default.encode(encoding) if isinstance(default, str) else default
    return value.encode(encoding) if value else None
```

### Usage

1. Set environment variables:
   ```bash
   export ABEMA_HKEY='your_hmac_key'
   export ABEMA_SECRET_KEY='your_secret_key'
   ```

2. The extractor will automatically use these values when instantiated

## Security Considerations

1. **Never commit actual secrets to version control**
2. **Use secure methods to set environment variables**
3. **Consider using a secrets management service in production**
4. **Rotate keys regularly**
5. **Monitor for security warnings in logs**

## Testing

Run the test suite to verify security implementation:

```bash
python -m pytest tests/test_abematv.py
```

## Compliance

This implementation follows:
1. Project security guidance from `guidance.ttl`
2. OWASP secure coding guidelines
3. Python security best practices

## TODO

1. Implement key rotation mechanism
2. Add audit logging for security events
3. Consider adding HMAC key versioning
4. Add integration with secrets management services 