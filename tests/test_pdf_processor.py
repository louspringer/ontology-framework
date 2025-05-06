"""Test script for PDF processor functionality."""

import unittest
from pathlib import Path
import logging
import numpy as np
from unittest.mock import patch, MagicMock
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
        
        # Create a small test PDF
        self.pdf_path = self.test_dir / "test.pdf"
        c = canvas.Canvas(str(self.pdf_path))
        c.drawString(100, 750, "Test document for PDF processor.")
        c.save()
        
    @patch('ontology_framework.pdf_processor.spacy.load')
    @patch('ontology_framework.pdf_processor.faiss.IndexFlatL2')
    def test_pdf_processing(self, mock_faiss, mock_spacy):
        # Mock spaCy model
        mock_nlp = MagicMock()
        mock_doc = MagicMock()
        mock_doc.vector = np.array([0.1, 0.2, 0.3])  # Simple mock vector
        mock_nlp.return_value = mock_doc
        mock_spacy.return_value = mock_nlp
        
        # Mock FAISS index
        mock_index = MagicMock()
        mock_index.search.return_value = (np.array([[1.0]]), np.array([[0]]))  # Mock search results
        mock_faiss.return_value = mock_index
        
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
        if (self.test_dir / "temp_embeddings").exists():
            for file in (self.test_dir / "temp_embeddings").iterdir():
                file.unlink()
            (self.test_dir / "temp_embeddings").rmdir()
        if self.test_dir.exists():
            for file in self.test_dir.iterdir():
                if file.name not in ["fuseki", "graphdb"]:  # Skip Fuseki and GraphDB directories
                    try:
                        file.unlink()
                    except (PermissionError, OSError):
                        pass  # Skip files that can't be deleted
            try:
                self.test_dir.rmdir()  # Try to remove directory if empty
            except OSError:
                pass  # Skip if directory is not empty

if __name__ == '__main__':
    unittest.main() 