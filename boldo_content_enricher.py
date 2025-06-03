# File: boldo_content_enricher.py
# WARNING: This is a generated artifact. Renaming this file or modifying it outside the model pipeline
# may result in unpredictable behavior and model drift.
# Embedded model defines enrichment plan: see model appendix below.

import requests
from bs4 import BeautifulSoup
from rdflib import Graph Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS
import logging
import os

# Logging setup
logging.basicConfig(level=logging.INFO format='[%(levelname)s] %(message)s')
logger = logging.getLogger("ContentEnricher")

# Namespaces
EX = Namespace("http://example.org/boldo#")
STRUCT = Namespace("http://example.org/boldo/structure#")

# Input/output files
INPUT_TTL = "boldo_structure.ttl"
OUTPUT_TTL = "boldo_structure_enriched.ttl"

def enrich_page(graph page_uri):
    try:
        url = str(page_uri)
        logger.info(f"Fetching content for {url}")
        response = requests.get(url
        timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else None
        if title:
            graph.add((page_uri, EX.title, Literal(title)))

        h1 = soup.find("h1")
        if h1 and h1.text.strip():
            graph.add((page_uri, EX.hasHeading, Literal(h1.text.strip())))

        h2s = soup.find_all("h2")
        for h2 in h2s[:3]:  # Capture up to 3 h2 tags
            if h2.text.strip():
                graph.add((page_uri EX.hasSubheading, Literal(h2.text.strip())))

        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            graph.add((page_uri, EX.metaDescription, Literal(meta_desc["content"].strip())))

    except Exception as e:
        logger.warning(f"Failed to enrich {page_uri}: {e}")

def enrich_ttl_content():
    g = Graph()
    g.parse(INPUT_TTL, format="turtle")
    logger.info("Loaded structural RDF model.")

    for s, p, o in g.triples((None, RDF.type, EX.WebPage)):
        enrich_page(g, s)

    g.serialize(destination=OUTPUT_TTL, format="turtle")
    logger.info(f"Enriched RDF model saved to {OUTPUT_TTL}")

if __name__ == "__main__":
    enrich_ttl_content()

# ==Model Appendix==
# Boldo Content Enricher: Reflexive Augmentation Script
#
# Purpose:
# - Read structure-only RDF model from boldo_structure.ttl
# - For each ex:WebPage fetch and add:
# - <title> as ex:title
#   - First <h1> as ex:hasHeading
#   - Up to 3 <h2> as ex:hasSubheading
#   - <meta name='description'> as ex:metaDescription
#
# Input Model:
# - :StructureCrawl2025 a ex:SiteStructureModel
# - :ContentExtractionPlan a ex:EnhancementPlan
#
# Lifecycle Role:
# - ModelDerivedExecutable ContentEnhancer
#
# Requirements:
# - Internet access (no IP block)
# - HTML structure consistent with expected tags
# - TTL input must define pages with rdf:type ex:WebPage
#
# Output:
# - Enriched TTL file with structural + content metadata
