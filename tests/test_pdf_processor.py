"""Test script for PDF processor functionality."""

import unittest
from pathlib import Path
import logging
from reportlab.pdfgen import canvas
from ontology_framework.pdf_processor import PDFProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestPDFProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor()
        self.test_dir = Path("data")
        self.test_dir.mkdir(exist_ok=True)
        
        # Create a sample PDF with actual content
        self.pdf_path = self.test_dir / "test.pdf"
        c = canvas.Canvas(str(self.pdf_path))
        c.drawString(100, 750, "This is a test PDF document.")
        c.drawString(100, 700, "It contains multiple lines of text.")
        c.drawString(100, 650, "This text will be used for testing the PDF processor.")
        c.save()
        
    def test_pdf_processing(self):
        try:
            # Process the PDF
            logger.info("Processing PDF...")
            self.processor.process_pdf(self.pdf_path)
            
            # Test search functionality
            logger.info("Testing search...")
            results = self.processor.search("test document")
            self.assertGreater(len(results), 0)
            
            # Test RDF export
            logger.info("Testing RDF export...")
            rdf_path = self.test_dir / "test.ttl"
            self.processor.export_rdf(rdf_path)
            self.assertTrue(rdf_path.exists())
            
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            raise
            
    def tearDown(self):
        # Clean up test files
        if self.pdf_path.exists():
            self.pdf_path.unlink()
        if (self.test_dir / "test.ttl").exists():
            (self.test_dir / "test.ttl").unlink()

if __name__ == '__main__':
    unittest.main() 