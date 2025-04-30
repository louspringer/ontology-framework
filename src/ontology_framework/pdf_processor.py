"""PDF Processor for creating semantic searchable RAG from PDF documents.

This module provides functionality to parse PDF documents and create a Retrieval-Augmented Generation (RAG)
system that can be used for semantic search and knowledge extraction.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from PyPDF2 import PdfReader
import spacy
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, DCTERMS
import faiss

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """Processes PDF documents into semantic searchable RAG."""
    
    def __init__(self, model_name: str = "en_core_web_md"):
        """Initialize the PDF processor.
        
        Args:
            model_name: Name of the spaCy model to use
        """
        self.rdf_graph = Graph()
        self._bind_namespaces()
        self.nlp = spacy.load(model_name)
        self.index = None
        self.text_chunks = []
        self.metadata = []
        
    def _bind_namespaces(self) -> None:
        """Bind required namespaces to the RDF graph."""
        self.DOC = Namespace("http://example.org/document#")
        self.rdf_graph.bind("doc", self.DOC)
        self.rdf_graph.bind("rdf", RDF)
        self.rdf_graph.bind("rdfs", RDFS)
        self.rdf_graph.bind("dcterms", DCTERMS)
        
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks.
        
        Args:
            text: Text to split
            chunk_size: Size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - overlap
        return chunks
        
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a text using spaCy.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        doc = self.nlp(text)
        return doc.vector
        
    def process_pdf(self, pdf_path: Union[str, Path]) -> None:
        """Process a PDF file and create embeddings for semantic search.
        
        Args:
            pdf_path: Path to the PDF file
            
        Example:
            >>> processor = PDFProcessor()
            >>> processor.process_pdf("document.pdf")
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        try:
            # Read PDF
            reader = PdfReader(str(pdf_path))
            
            # Create document node
            doc_node = URIRef(f"{self.DOC}{pdf_path.stem}")
            self.rdf_graph.add((doc_node, RDF.type, self.DOC.Document))
            self.rdf_graph.add((doc_node, DCTERMS.title, Literal(pdf_path.stem)))
            
            # Process each page
            for page_num, page in enumerate(reader.pages, 1):
                page_node = URIRef(f"{self.DOC}{pdf_path.stem}/page/{page_num}")
                self.rdf_graph.add((page_node, RDF.type, self.DOC.Page))
                self.rdf_graph.add((page_node, DCTERMS.isPartOf, doc_node))
                
                # Extract text
                text = page.extract_text()
                if text:
                    # Create text node
                    text_node = BNode()
                    self.rdf_graph.add((text_node, RDF.type, self.DOC.TextContent))
                    self.rdf_graph.add((text_node, RDFS.label, Literal(text)))
                    self.rdf_graph.add((page_node, self.DOC.hasContent, text_node))
                    
                    # Split text into chunks
                    chunks = self._chunk_text(text)
                    for chunk_num, chunk in enumerate(chunks):
                        self.text_chunks.append(chunk)
                        self.metadata.append({
                            'page': page_num,
                            'chunk': chunk_num,
                            'document': pdf_path.stem
                        })
            
            # Create embeddings
            embeddings = np.array([self._get_embedding(chunk) for chunk in self.text_chunks])
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype('float32'))
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise
            
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search the PDF content using semantic similarity.
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of search results with page numbers and text snippets
            
        Example:
            >>> results = processor.search("ontology framework")
            >>> for result in results:
            ...     print(f"Page {result['page']}: {result['snippet']}")
        """
        if self.index is None:
            raise ValueError("No PDF has been processed yet")
            
        # Encode query
        query_embedding = self._get_embedding(query)
        
        # Search index
        distances, indices = self.index.search(np.array([query_embedding]).astype('float32'), k)
        
        # Format results
        results = []
        for i, idx in enumerate(indices[0]):
            metadata = self.metadata[idx]
            results.append({
                'page': metadata['page'],
                'document': metadata['document'],
                'snippet': self.text_chunks[idx],
                'score': float(distances[0][i])
            })
            
        return results
        
    def export_rdf(self, output_path: Union[str, Path]) -> None:
        """Export the RDF graph to a Turtle file.
        
        Args:
            output_path: Path to save the RDF graph
            
        Example:
            >>> processor.export_rdf("document.ttl")
        """
        self.rdf_graph.serialize(destination=str(output_path), format='turtle')
        
    def save_index(self, output_path: Union[str, Path]) -> None:
        """Save the FAISS index and associated data.
        
        Args:
            output_path: Path to save the index
            
        Example:
            >>> processor.save_index("document.index")
        """
        if self.index is None:
            raise ValueError("No index to save")
            
        output_path = Path(output_path)
        faiss.write_index(self.index, str(output_path))
        
        # Save metadata
        import json
        with open(output_path.with_suffix('.json'), 'w') as f:
            json.dump({
                'text_chunks': self.text_chunks,
                'metadata': self.metadata
            }, f)
            
    def load_index(self, input_path: Union[str, Path]) -> None:
        """Load a saved FAISS index and associated data.
        
        Args:
            input_path: Path to load the index from
            
        Example:
            >>> processor.load_index("document.index")
        """
        input_path = Path(input_path)
        self.index = faiss.read_index(str(input_path))
        
        # Load metadata
        import json
        with open(input_path.with_suffix('.json'), 'r') as f:
            data = json.load(f)
            self.text_chunks = data['text_chunks']
            self.metadata = data['metadata'] 