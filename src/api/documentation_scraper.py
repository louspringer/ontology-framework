"""
Documentation scraper for Boldo API.

This module provides functionality to scrape and analyze API documentation.
"""

import logging
from typing import Dict, Any, Optional, List
import requests
import json
from pathlib import Path
import traceback
from http import HTTPStatus
from bs4 import BeautifulSoup
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
import re

from .boldo_explorer import BoldoAPIExplorer

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentationScraper:
    """A class to scrape and analyze API documentation from various endpoints."""
    
    def __init__(self, base_url: str = "https://app.boldo.io", api_key: Optional[str] = None):
        """Initialize the documentation scraper.
        
        Args:
            base_url: Base URL for the API documentation
            api_key: Boldo API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api = BoldoAPIExplorer(api_key=api_key)
        self.logger = logging.getLogger(__name__)
        self.graph = self._setup_graph()
        
    def _setup_graph(self) -> Graph:
        """Initialize and setup the RDF graph with necessary namespaces."""
        g = Graph()
        # Bind common namespaces
        g.bind('rdf', RDF)
        g.bind('rdfs', RDFS)
        g.bind('owl', OWL)
        g.bind('xsd', XSD)
        # Custom namespace for documentation
        DOC = Namespace(self.base_url + '/documentation#')
        g.bind('doc', DOC)
        return g

    def fetch_documentation(self, endpoint: str) -> Optional[str]:
        """Fetch documentation content from a specific endpoint."""
        url = f"{self.base_url}{endpoint}"
        try:
            logger.info(f"Attempting to fetch documentation from: {url}")
            response = requests.get(url)
            
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
            logger.error(f"Request failed for {url}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Stack trace:\n{traceback.format_exc()}")
            return None

    def analyze_content(self, content):
        if not content:
            return {
                "title": None,
                "description": None,
                "endpoint_count": 0,
                "auth_methods": [],
                "sections": {}
            }

        analysis = {
            "title": None,
            "description": None,
            "endpoint_count": 0,
            "auth_methods": [],
            "sections": {}
        }

        soup = BeautifulSoup(content, 'html.parser')

        # Define regex patterns for API-related content
        api_endpoint_pattern = re.compile(r'/api/[a-zA-Z0-9/-]+')
        api_key_pattern = re.compile(r'api[-_]key', re.IGNORECASE)
        auth_pattern = re.compile(r'(authenticate|authorization|bearer|token)', re.IGNORECASE)
        http_status_pattern = re.compile(r'([1-5][0-9]{2})\s+[A-Z][a-z\s]+')

        # Extract title and description
        title_tag = soup.find('title')
        if title_tag:
            analysis['title'] = title_tag.text.strip()

        # Count common documentation sections
        common_sections = [
            'authentication', 'endpoints', 'models', 'errors',
            'metamodel', 'assets', 'relations', 'properties',
            'users', 'roles', 'domains'
        ]
        
        for section in common_sections:
            matches = len(re.findall(rf'\b{section}\b', content, re.IGNORECASE))
            if matches > 0:
                analysis['sections'][section] = matches

        # Extract embedded JSON from script tags
        script_tags = soup.find_all('script')
        for script in script_tags:
            script_text = script.string
            if script_text:
                # Look for API-related keys in the script content
                api_keys = re.findall(r'"(api[^"]*)":', script_text)
                if api_keys:
                    analysis['sections']['api_config'] = api_keys

        return analysis

    def save_results(self, analysis, endpoint):
        """Save the analysis results to a file."""
        filename = f'api_documentation_{endpoint.replace("/", "_")}.json'
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        self.logger.info(f"Analysis results saved to {filename}")

    def update_ontology(self, analysis: Dict[str, Any]):
        """Update the RDF graph with analysis results."""
        DOC = Namespace(self.base_url + '/documentation#')
        
        # Create documentation source
        source = URIRef(DOC['APIDocumentation'])
        self.graph.add((source, RDF.type, DOC['DocumentationSource']))
        self.graph.add((source, RDFS.label, Literal(analysis.get('title', 'Unknown'))))
        
        # Add analysis results
        if analysis.get('format') == 'json':
            for endpoint in analysis.get('endpoints', []):
                endpoint_node = URIRef(DOC[f"Endpoint_{endpoint['path']}"])
                self.graph.add((endpoint_node, RDF.type, DOC['APIEndpoint']))
                self.graph.add((endpoint_node, DOC['path'], Literal(endpoint['path'])))
                for method in endpoint.get('methods', []):
                    self.graph.add((endpoint_node, DOC['supportsMethod'], Literal(method)))
        
        elif analysis.get('format') == 'html':
            for ref in analysis.get('api_references', []):
                ref_node = URIRef(DOC[f"Reference_{hash(ref['url'])}"])
                self.graph.add((ref_node, RDF.type, DOC['APIReference']))
                self.graph.add((ref_node, DOC['url'], Literal(ref['url'])))
                self.graph.add((ref_node, RDFS.label, Literal(ref['text'])))

    def save_ontology(self, output_file: str = 'documentation_scraping.ttl'):
        """Save the ontology to a Turtle file."""
        try:
            self.graph.serialize(destination=output_file, format='turtle')
            logger.info(f"Ontology saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save ontology: {str(e)}")
            logger.error(traceback.format_exc())

    def scrape_documentation(self, endpoint: str = "/api-doc") -> Dict[str, Any]:
        """Scrape documentation from the specified endpoint.
        
        Args:
            endpoint: API documentation endpoint to scrape
            
        Returns:
            Dictionary containing scraping results and metadata
        """
        url = f"{self.base_url}{endpoint}"
        logger.info(f"Scraping documentation from {url}")
        
        try:
            response = self.api._make_request("GET", endpoint)
            
            if isinstance(response, str):
                # Handle HTML response
                soup = BeautifulSoup(response, 'html.parser')
                content = soup.get_text(separator=' ', strip=True)
                
                # Log the result in our ontology
                result_uri = URIRef("http://example.org/documentation#ScrapingResult")
                self.graph.add((result_uri, RDF.type, OWL.NamedIndividual))
                self.graph.add((result_uri, RDFS.label, Literal("Documentation Scraping Result")))
                self.graph.add((result_uri, URIRef("http://example.org/documentation#resultStatus"), 
                              Literal("SUCCESS", datatype=XSD.string)))
                self.graph.add((result_uri, URIRef("http://example.org/documentation#resultContent"), 
                              Literal(content, datatype=XSD.string)))
                
                return {
                    "status": "success",
                    "content": content,
                    "metadata": {
                        "url": url,
                        "content_type": "text/html",
                        "length": len(content)
                    }
                }
            else:
                # Handle JSON response
                return {
                    "status": "success",
                    "content": response,
                    "metadata": {
                        "url": url,
                        "content_type": "application/json",
                        "length": len(str(response))
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to scrape documentation: {str(e)}")
            
            # Log the failure in our ontology
            result_uri = URIRef("http://example.org/documentation#ScrapingResult")
            self.graph.add((result_uri, RDF.type, OWL.NamedIndividual))
            self.graph.add((result_uri, RDFS.label, Literal("Documentation Scraping Result")))
            self.graph.add((result_uri, URIRef("http://example.org/documentation#resultStatus"), 
                          Literal("FAILURE", datatype=XSD.string)))
            self.graph.add((result_uri, URIRef("http://example.org/documentation#resultContent"), 
                          Literal(str(e), datatype=XSD.string)))
            
            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "url": url,
                    "error_type": type(e).__name__
                }
            }
            
    def save_results(self, filename: str = "documentation_scraping.ttl") -> None:
        """Save scraping results to a Turtle file.
        
        Args:
            filename: Name of the file to save results to
        """
        try:
            self.graph.serialize(destination=filename, format="turtle")
            logger.info(f"Saved scraping results to {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")
            
    def _extract_api_info_from_html(self, html_content: str) -> Dict[str, str]:
        """Extract API information from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract API title and version
        title = soup.find('h1')
        version = soup.find('p', class_='rounded-full')
        description = soup.find('p', class_='text-sm')
        
        info = {
            'title': title.text if title else 'Unknown',
            'version': version.text if version else 'Unknown',
            'description': description.text if description else 'No description available'
        }
        
        # Extract endpoints if available
        endpoints = []
        endpoint_sections = soup.find_all('div', class_='endpoint-section')
        for section in endpoint_sections:
            if section:
                method = section.find('span', class_='method')
                path = section.find('span', class_='path')
                if method and path:
                    endpoints.append(f"{method.text} {path.text}")
        
        info['endpoints'] = endpoints
        return info

    def _add_to_graph(self, info: Dict[str, str]) -> None:
        """Add scraped information to the RDF graph."""
        doc = Namespace('http://boldo.io/documentation#')
        
        api_doc = URIRef(doc['BoldoAPI'])
        self.graph.add((api_doc, RDF.type, doc.APIDocumentation))
        self.graph.add((api_doc, RDFS.label, Literal(info['title'])))
        self.graph.add((api_doc, doc.version, Literal(info['version'])))
        self.graph.add((api_doc, RDFS.comment, Literal(info['description'])))
        
        for i, endpoint in enumerate(info.get('endpoints', [])):
            endpoint_node = URIRef(doc[f'endpoint_{i}'])
            self.graph.add((endpoint_node, RDF.type, doc.Endpoint))
            self.graph.add((endpoint_node, RDFS.label, Literal(endpoint)))
            self.graph.add((api_doc, doc.hasEndpoint, endpoint_node))

    def save_results(self, output_file: str = "documentation_scraping.ttl") -> None:
        """Save the scraped results to a Turtle file."""
        self.graph.serialize(destination=output_file, format="turtle")
        logger.info(f"Results saved to {output_file}")

    def analyze_content(self, info: Dict[str, str]) -> Dict[str, int]:
        """Analyze the scraped content."""
        analysis = {
            'title_length': len(info.get('title', '')),
            'version': info.get('version', 'Unknown'),
            'description_length': len(info.get('description', '')),
            'endpoint_count': len(info.get('endpoints', []))
        }
        
        logger.info(f"Content analysis: {analysis}")
        return analysis

    def _extract_html_content(self, html_content: str) -> Dict:
        """Extract useful information from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract metadata
        metadata = {
            'title': soup.title.string if soup.title else 'Unknown',
            'meta_description': soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else '',
            'headers': [h.text for h in soup.find_all(['h1', 'h2', 'h3'])],
            'links': [a['href'] for a in soup.find_all('a', href=True)],
            'scripts': [s['src'] for s in soup.find_all('script', src=True)],
            'is_404': '404' in html_content or 'not found' in html_content.lower()
        }
        
        # Look for API-related content
        api_related = {
            'swagger_references': bool(soup.find_all(string=lambda text: 'swagger' in str(text).lower())),
            'openapi_references': bool(soup.find_all(string=lambda text: 'openapi' in str(text).lower())),
            'api_endpoints': [a['href'] for a in soup.find_all('a', href=True) if '/api/' in a['href']],
            'api_related_text': [p.text for p in soup.find_all(['p', 'div', 'span']) if 'api' in p.text.lower()]
        }
        
        return {'metadata': metadata, 'api_content': api_related}

    def _add_to_graph(self, content: Dict, endpoint: str, status_code: int):
        """Add scraped content to the RDF graph."""
        doc = Namespace('http://example.org/documentation#')
        
        # Create a node for this scraping attempt
        attempt_uri = URIRef(f"{doc}attempt_{endpoint.replace('/', '_')}")
        self.graph.add((attempt_uri, RDF.type, doc.ScrapingAttempt))
        self.graph.add((attempt_uri, doc.endpoint, Literal(endpoint)))
        self.graph.add((attempt_uri, doc.statusCode, Literal(status_code)))
        
        if 'metadata' in content:
            metadata = content['metadata']
            self.graph.add((attempt_uri, doc.pageTitle, Literal(metadata['title'])))
            self.graph.add((attempt_uri, doc.metaDescription, Literal(metadata['meta_description'])))
            self.graph.add((attempt_uri, doc.is404, Literal(metadata['is_404'])))
            
            # Add headers as a collection
            for header in metadata['headers']:
                self.graph.add((attempt_uri, doc.hasHeader, Literal(header)))
                
        if 'api_content' in content:
            api_content = content['api_content']
            self.graph.add((attempt_uri, doc.hasSwaggerReferences, Literal(api_content['swagger_references'])))
            self.graph.add((attempt_uri, doc.hasOpenAPIReferences, Literal(api_content['openapi_references'])))
            
            for endpoint in api_content['api_endpoints']:
                self.graph.add((attempt_uri, doc.containsAPIEndpoint, Literal(endpoint)))
            
            for text in api_content['api_related_text']:
                self.graph.add((attempt_uri, doc.containsAPIRelatedText, Literal(text)))

    def save_results(self, output_file: str = 'documentation_scraping.ttl'):
        """Save the RDF graph to a Turtle file."""
        try:
            self.graph.serialize(destination=output_file, format='turtle')
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}") 