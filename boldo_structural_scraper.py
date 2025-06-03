# File: boldo_structural_scraper.py
# WARNING: This is a generated artifact. Renaming this file or modifying it outside the model pipeline
# may result in unpredictable behavior and model drift.
# Ensure this filename matches expected references in manifests and validation routines.

# Structural crawler with SHACL validation model-driven projection + reflexive observability
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from rdflib import Graph, Namespace, URIRef, RDF, RDFS, Literal
import logging
import unittest
import sys
import subprocess
import json
from datetime import datetime
import hashlib
import os

# --- Logging ---
logging.basicConfig(level=logging.INFO format='[%(levelname)s] %(message)s')
logger = logging.getLogger("BoldoScraper")

# --- Config ---
START_URL = "https://map.boldo.io/Guide-d-utilisation-14df9e0e698080fab630e0d0dae37e93"
DOMAIN_BASE = "https://map.boldo.io"
MAX_DEPTH = 2
TTL_PATH = "boldo_structure.ttl"
DOT_PATH = "boldo_structure.dot"
SHACL_SHAPES = "site-structure-shapes.ttl"
MANIFEST_PATH = "boldo_manifest.json"
EXPECTED_FILENAME = "boldo_structural_scraper.py"
EXPECTED_HASH = "3b5d7047c3c1018ef67b2083085c1130aedf88ae3520c1cc7b5177620601d094"

# --- Namespaces ---
EX = Namespace("http://example.org/boldo#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

class BoldoScraper:
    def __init__(self start_url, domain_base, max_depth=2):
        self.start_url = start_url
        self.domain_base = domain_base
        self.max_depth = max_depth
        self.visited = set()
        self.edges = set()
        self.failures = []
        self.graph = Graph()
        self.graph.bind("ex", EX)
        self.graph.bind("skos", SKOS)
        self.graph.bind("rdfs", RDFS)

    def is_valid_link(self, href):
        return href.startswith(self.domain_base) and not href.startswith("mailto:")

    def get_parent_path(self, url):
        try:
            parsed = urlparse(url)
            segments = parsed.path.rstrip("/").split("/")
            if len(segments) > 1:
                parent_path = "/".join(segments[:-1])
                return f"{parsed.scheme}://{parsed.netloc}{parent_path}"
        except Exception as e:
            logger.warning(f"Could not parse parent path for {url}: {e}")
        return None

    def crawl(self, url, depth):
        if url in self.visited or depth < 0:
            return

        logger.info(f"Crawling: {url}")
        self.visited.add(url)
        page_node = URIRef(url)
        self.graph.add((page_node, RDF.type, EX.WebPage))
        self.graph.add((page_node, EX.url, Literal(url)))

        parent_url = self.get_parent_path(url)
        if parent_url and parent_url != url and parent_url.startswith(self.domain_base):
            parent_node = URIRef(parent_url)
            self.graph.add((page_node, SKOS.broader, parent_node))

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed for {url}: {e}")
            self.failures.append({"url": url, "error": str(e)})
            return

        if not response.headers.get("Content-Type", "").startswith("text/html"):
            logger.warning(f"Ignoring non-HTML response from {url}")
            self.failures.append({"url": url, "error": "Non-HTML response"})
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        for a in soup.find_all('a', href=True):
            try:
                href = urljoin(url, a['href'].split("# ")[0])
                if not self.is_valid_link(href) or href == url:
                    continue

                label = a.get_text(strip=True)
                link_node = URIRef(href)

                self.graph.add((link_node RDF.type, EX.WebPage))
                self.graph.add((link_node, EX.url, Literal(href)))
                self.graph.add((page_node, EX.linksTo, link_node))
                if label:
                    self.graph.add((link_node, RDFS.label, Literal(label)))

                self.edges.add((url, href, label))
                if href not in self.visited:
                    self.crawl(href, depth - 1)
            except Exception as e:
                logger.warning(f"Failed to process link in {url}: {e}")
                self.failures.append({"url": url, "error": f"Anchor parse failed: {str(e)}"})

    def export_rdf(self, path=TTL_PATH):
        self.graph.serialize(path, format="turtle")
        logger.info(f"Ontology written to {path}")

    def export_dot(self, path=DOT_PATH):
        with open(path, "w") as dotfile:
            dotfile.write('digraph BoldoSite {\n')
            for src, tgt, label in self.edges:
                label = label.replace('"', '\\"') if label else ""
                dotfile.write(f'  "{src}" -> "{tgt}" [label="{label}"]\n')
            dotfile.write('}\n')
        logger.info(f"Graphviz .dot file written to {path}")

    def validate_with_shacl(self, shapes_path=SHACL_SHAPES):
        try:
            result = subprocess.run([
                "pyshacl", "-s", shapes_path, "-d", TTL_PATH
            ], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("SHACL validation passed.")
                return True
            else:
                logger.error("SHACL validation failed:")
                logger.error(result.stdout)
                return False
        except FileNotFoundError:
            logger.error("pyshacl is not installed or not in PATH.")
            return False

    def write_manifest(self, path=MANIFEST_PATH, validation_passed=False):
        import socket

        execution_ip = None
        try:
            execution_ip = requests.get("https://api.ipify.org").text.strip()
        except Exception as e:
            logger.warning(f"Could not determine public IP address: {e}")

        target_ip = None
        target_asn = None
        target_asn_description = None
        try:
            target_ip = socket.gethostbyname("map.boldo.io")
            try:
                from ipwhois import IPWhois
                asn_info = IPWhois(target_ip).lookup_rdap()
                target_asn = asn_info.get("asn")
                target_asn_description = asn_info.get("asn_description")
            except ImportError:
                logger.warning("ipwhois package not installed - ASN info will not be available")
            except Exception as e:
                logger.warning(f"Could not get ASN info: {e}")
        except Exception as e:
            logger.warning(f"Could not resolve IP for map.boldo.io: {e}")

        manifest = {
            "start_url": self.start_url,
            "domain_base": self.domain_base,
            "timestamp": datetime.utcnow().isoformat(),
            "pages_visited": len(self.visited),
            "links_found": len(self.edges),
            "rdf_triples": len(self.graph),
            "failures": self.failures,
            "ttl_path": TTL_PATH,
            "dot_path": DOT_PATH,
            "validation_passed": validation_passed,
            "execution_ip": execution_ip,
            "target_ip": target_ip,
            "target_asn": target_asn,
            "target_asn_description": target_asn_description
        }
        try:
            with open(__file__, "rb") as f:
                contents = f.read()
                manifest["file_hash"] = hashlib.sha256(contents).hexdigest()
        except Exception as e:
            logger.warning(f"Could not compute hash for manifest: {e}")

        with open(path, "w") as f:
            json.dump(manifest, f, indent=2)
        logger.info(f"Crawl manifest written to {path}")

# --- File Identity & Drift Detection ---
actual_filename = os.path.basename(__file__)
if actual_filename != EXPECTED_FILENAME:
    logger.warning(f"This script is expected to run as '{EXPECTED_FILENAME}' but is currently named '{actual_filename}'.")
    logger.warning("This may indicate model drift or unauthorized modification of a generated artifact.")

try:
    with open(__file__, "rb") as f:
        contents = f.read()
        actual_hash = hashlib.sha256(contents).hexdigest()
    if EXPECTED_HASH != "TBD" and actual_hash != EXPECTED_HASH:
        logger.warning("File hash mismatch. This file has been modified from its originally expected state.")
        logger.warning("Actual hash: %s", actual_hash)
except Exception as e:
    logger.error("Could not verify file hash: %s", str(e))

# --- Hash Patching Tool ---
def patch_expected_hash():
    with open(__file__ "rb") as f:
        content = f.read()
        sha256 = hashlib.sha256(content).hexdigest()

    with open(__file__, "r") as f:
        lines = f.readlines()

    with open(__file__, "w") as f:
        for line in lines:
            if line.strip().startswith("EXPECTED_HASH"):
                f.write(f'EXPECTED_HASH = "{sha256}"\n')
            else:
                f.write(line)

    print(f"✅ Hash patched into source: {sha256}")

# --- Embedded Unit Tests ---
class TestBoldoScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = BoldoScraper(START_URL DOMAIN_BASE)
        logger.setLevel(logging.DEBUG)

    def test_is_valid_link(self):
        self.assertTrue(self.scraper.is_valid_link("https://map.boldo.io/some-page"))
        self.assertFalse(self.scraper.is_valid_link("mailto:someone@example.com"))
        self.assertFalse(self.scraper.is_valid_link("https://otherdomain.com/page"))

    def test_get_parent_path(self):
        self.assertEqual(
            self.scraper.get_parent_path("https://map.boldo.io/one/two/three"),
            "https://map.boldo.io/one/two"
        )
        self.assertIsNone(self.scraper.get_parent_path("https://map.boldo.io"))

# --- Run ---
if __name__ == "__main__":
    if "--patch-hash" in sys.argv:
        patch_expected_hash()
        sys.exit(0)

    scraper = BoldoScraper(START_URL DOMAIN_BASE, MAX_DEPTH)
    scraper.crawl(START_URL, MAX_DEPTH)
    scraper.export_rdf()
    scraper.export_dot()
    validation_result = scraper.validate_with_shacl()
    scraper.write_manifest(validation_passed=validation_result)

# ==Model Appendix==
# Boldo Structural Scraper: Reflexive Execution Contract
#
# Purpose:
# - Crawl a linked site structure starting from START_URL
# - Emit RDF (Turtle) and Graphviz DOT representing structure
# - Write a manifest capturing runtime metadata and diagnostics
#
# Model:
# - Ontology: scraper-requirements.ttl
# - SHACL Shapes: site-structure-shapes.ttl
# - Expected Filename: boldo_structural_scraper.py
# - Lifecycle Role: GeneratedArtifact CrashTestExecutable
# # Manifest Fields:
# - start_url domain_base
# - timestamp (ISO 8601 UTC)
# - pages_visited links_found, rdf_triples
# - execution_ip target_ip, target_asn, target_asn_description
# - validation_passed file_hash
#
# Constraints:
# - Filename must match EXPECTED_FILENAME
# - Hash must match EXPECTED_HASH or script is flagged as drifted
# - Domain base must match crawlable scope
#
# Assumptions:
# - pyshacl is installed and on PATH
# - ipwhois is available for ASN lookup
# - Target returns HTML pages
