"""Test script for PDF processor functionality."""

import logging
from pathlib import Path
from ontology_framework.pdf_processor import PDFProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

def test_pdf_processor():
    """Test the PDF processor with a sample PDF."""
    try:
        # Initialize processor
        processor = PDFProcessor()
        
        # Process PDF
        pdf_path = Path("GraphDB.pdf")
        logger.info(f"Processing PDF: {pdf_path}")
        processor.process_pdf(pdf_path)
        
        # Test search
        test_queries = [
            "repository configuration",
            "GraphDB setup",
            "RDF storage"
        ]
        
        for query in test_queries:
            logger.info(f"\nSearching for: {query}")
            results = processor.search(query)
            for result in results:
                logger.info(f"Page {result['page']} (score: {result['score']:.2f}):")
                logger.info(f"{result['snippet'][:200]}...")
        
        # Save index for future use
        processor.save_index("graphdb.index")
        logger.info("Index saved to graphdb.index")
        
        # Export RDF
        processor.export_rdf("graphdb.ttl")
        logger.info("RDF exported to graphdb.ttl")
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        raise

if __name__ == "__main__":
    test_pdf_processor() 