# FireCrawl Configuration Guide

This document explains the FireCrawl configuration and availability checking in the Enhanced Public Opinion Analysis Strategy V2.

## Overview

The strategy includes FireCrawl integration for web scraping capabilities. It has been updated to properly detect and work with custom FireCrawl deployments.

## Current Configuration

The strategy is configured to use FireCrawl at:
```
http://192.168.1.2:8080/v1
```

The current deployment returns:
```
SCRAPERS-JS: Hello, world! K8s!
```

This indicates it's a custom scraper deployment that actually does support standard FireCrawl API endpoints.

## Availability Checking Logic

The `_is_firecrawl_available` method performs the following checks:

1. **Base URL Extraction**: Extracts the base URL from the API URL (removing version paths like `/v1`)
2. **Base URL Accessibility**: Verifies the FireCrawl base URL is accessible
3. **Deployment Type Detection**: Checks for "SCRAPERS-JS" signature to identify custom deployments
4. **Endpoint Validation**: Actually tests the `/v1/scrape` endpoint to verify functionality

## Behavior When Not Available

When FireCrawl is not available or doesn't support required endpoints:
- The strategy logs a warning message
- FireCrawl data collection is skipped gracefully
- Other data sources continue to function normally
- The strategy execution continues without interruption

## Custom Deployment Handling

The current FireCrawl deployment at `192.168.1.2:8080` is identified as a custom scraper deployment (SCRAPERS-JS) that:
- Returns "SCRAPERS-JS: Hello, world! K8s!" at the root URL
- **Does** support standard FireCrawl API endpoints like `/v1/scrape`
- Is now properly detected and utilized by the updated availability checking logic

## Configuration Options

To use a different FireCrawl deployment:

1. **Update Database Configuration**: Modify the strategy parameters in MongoDB
2. **Change API URL**: Update the `firecrawl_config.api_url` parameter
3. **Adjust Settings**: Modify timeout, retry, and rate limit settings as needed

Example configuration:
```python
"firecrawl_config": {
    "api_url": "http://your-firecrawl-server:3002/v1",  # Standard FireCrawl endpoint with version
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 1,
    "rate_limit": 10,
    "concurrent_requests": 5,
}
```

## Testing FireCrawl Availability

To test FireCrawl availability, run:
```bash
python test/test_firecrawl_availability.py
```

This will show:
- Base URL accessibility
- Deployment type detection
- Endpoint validation results
- Strategy's availability check result

## Notes

1. The updated strategy properly detects that "SCRAPERS-JS" deployments can support standard FireCrawl APIs
2. The strategy now actually tests the scrape endpoint instead of assuming functionality based on deployment type
3. All data sources (AkShare, Guba, FireCrawl, professional sites) now function correctly
4. Performance has been improved by using the working FireCrawl deployment for web scraping

