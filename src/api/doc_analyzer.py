import logging
from typing import Dict, Any, Optional
import requests
import json
from pathlib import Path
import traceback
from http import HTTPStatus

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIDocAnalyzer:
    def __init__(self, doc_url: str):
        self.doc_url = doc_url
        
    def fetch_documentation(self) -> Optional[str]:
        """Fetch the raw documentation content."""
        try:
            logger.info(f"Attempting to fetch documentation from: {self.doc_url}")
            response = requests.get(self.doc_url)
            
            # Log response details
            logger.debug(f"Response status code: {response.status_code} ({HTTPStatus(response.status_code).phrase})")
            logger.debug(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
            logger.debug(f"Response content type: {response.headers.get('content-type', 'Not specified')}")
            logger.debug(f"Response encoding: {response.encoding}")
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch documentation. Status: {response.status_code}")
                logger.error(f"Response text: {response.text[:1000]}...")
                response.raise_for_status()
                
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Stack trace:\n{traceback.format_exc()}")
            raise
        
    def analyze_documentation(self) -> Dict[str, Any]:
        """Analyze the API documentation and return its structure."""
        try:
            # First fetch the raw content
            raw_content = self.fetch_documentation()
            if not raw_content:
                logger.error("No content received from documentation endpoint")
                return {}
                
            logger.info("Received raw documentation content")
            logger.debug("Content preview (first 500 chars):")
            logger.debug(raw_content[:500] + "..." if len(raw_content) > 500 else raw_content)
            
            # Try to parse as JSON first
            try:
                logger.info("Attempting to parse content as JSON")
                spec = json.loads(raw_content)
                logger.info("Successfully parsed content as JSON")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse content as JSON: {str(e)}")
                logger.error(f"Error at position {e.pos}: {e.msg}")
                logger.error(f"Line number: {e.lineno}, Column: {e.colno}")
                logger.error(f"Document snippet around error:\n{raw_content[max(0, e.pos-50):e.pos+50]}")
                
                # Save problematic content for inspection
                error_file = "raw_api_doc_error.txt"
                with open(error_file, "w") as f:
                    f.write(raw_content)
                logger.info(f"Saved problematic content to {error_file}")
                return {}
            
            # Log API specification details
            if spec:
                logger.info("API Specification Details:")
                logger.info(f"Title: {spec.get('info', {}).get('title', 'Unknown')}")
                logger.info(f"Version: {spec.get('info', {}).get('version', 'Unknown')}")
                logger.info(f"Available fields: {list(spec.keys())}")
                
                # Log endpoints if present
                paths = spec.get('paths', {})
                if paths:
                    logger.info(f"Found {len(paths)} endpoints:")
                    for path, methods in paths.items():
                        logger.info(f"Path: {path}")
                        logger.info(f"Available methods: {list(methods.keys())}")
                        for method, details in methods.items():
                            logger.info(f"  Method: {method}")
                            logger.info(f"  Summary: {details.get('summary', 'No summary')}")
                            logger.info(f"  Operation ID: {details.get('operationId', 'Not specified')}")
                else:
                    logger.warning("No endpoints found in the specification")
            
            return spec
            
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Stack trace:\n{traceback.format_exc()}")
            raise

def main():
    doc_url = "https://app.boldo.io/api-doc"
    logger.info(f"Starting API documentation analysis for: {doc_url}")
    
    analyzer = APIDocAnalyzer(doc_url)
    try:
        spec = analyzer.analyze_documentation()
        if spec:
            output_path = Path("api_spec.json")
            with open(output_path, "w") as f:
                json.dump(spec, f, indent=2)
            logger.info(f"API specification saved to {output_path}")
        else:
            logger.warning("No valid API specification was obtained")
            
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        logger.error(f"Stack trace:\n{traceback.format_exc()}")
        raise

if __name__ == "__main__":
    main() 