"""PDF Processor for creating semantic searchable RAG from PDF documents.

This module provides functionality to parse PDF documents and create a Retrieval-Augmented Generation (RAG)
system that can be used for semantic search and knowledge extraction.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
from PyPDF2 import PdfReader
import spacy
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import RDF, RDFS, DCTERMS
import faiss
import gc
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """Processes PDF documents into semantic searchable RAG."""
    
    def __init__(self, model_name: str = "en_core_web_md", chunk_size: int = 200, overlap: int = 20):
        """Initialize the PDF processor.
        
        Args:
            model_name: Name of the spaCy model to use
            chunk_size: Size of text chunks in characters
            overlap: Overlap between chunks in characters
        """
        self.rdf_graph = Graph()
        self._bind_namespaces()
        self.nlp = spacy.load(model_name, disable=['parser', 'ner'])  # Disable unnecessary components
        self.nlp.add_pipe('sentencizer')  # Add sentencizer for sentence splitting
        self.index = None
        self.text_chunks = []
        self.metadata = []
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.temp_dir = Path("temp_embeddings")
        self.temp_dir.mkdir(exist_ok=True)
        
    def _bind_namespaces(self) -> None:
        """Bind required namespaces to the RDF graph."""
        self.DOC = Namespace("http://example.org/document#")
        self.rdf_graph.bind("doc", self.DOC)
        self.rdf_graph.bind("rdf", RDF)
        self.rdf_graph.bind("rdfs", RDFS)
        self.rdf_graph.bind("dcterms", DCTERMS)
        
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        # Split text into sentences first
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            if current_size + sentence_size <= self.chunk_size:
                current_chunk.append(sentence)
                current_size += sentence_size
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_size = sentence_size
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks
        
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a text using spaCy.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Process text in smaller chunks if it's too long
        if len(text) > 1000:
            docs = [self.nlp(t) for t in [text[i:i+1000] for i in range(0, len(text), 1000)]]
            vectors = [doc.vector for doc in docs]
            return np.mean(vectors, axis=0)
        return self.nlp(text).vector
        
    def _save_embeddings(self, embeddings: np.ndarray, page_num: int) -> None:
        """Save embeddings to disk.
        
        Args:
            embeddings: Embeddings to save
            page_num: Page number
        """
        np.save(self.temp_dir / f"embeddings_page_{page_num}.npy", embeddings)
        
    def _load_embeddings(self, page_num: int) -> np.ndarray:
        """Load embeddings from disk.
        
        Args:
            page_num: Page number
            
        Returns:
            Loaded embeddings
        """
        return np.load(self.temp_dir / f"embeddings_page_{page_num}.npy")
        
    def process_pdf(self, pdf_path: Union[str, Path]) -> None:
        """Process a PDF file and create embeddings for semantic search.
        
        Args:
            pdf_path: Path to the PDF file
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
            
            # Initialize FAISS index with first batch
            first_batch = True
            
            # Process each page
            for page_num, page in enumerate(reader.pages, 1):
                logger.info(f"Processing page {page_num}")
                page_node = URIRef(f"{self.DOC}{pdf_path.stem}/page/{page_num}")
                self.rdf_graph.add((page_node, RDF.type, self.DOC.Page))
                self.rdf_graph.add((page_node, DCTERMS.isPartOf, doc_node))
                
                # Extract text
                text = page.extract_text()
                if not text:
                    continue
                    
                # Create text node
                text_node = BNode()
                self.rdf_graph.add((text_node, RDF.type, self.DOC.TextContent))
                self.rdf_graph.add((text_node, RDFS.label, Literal(text)))
                self.rdf_graph.add((page_node, self.DOC.hasContent, text_node))
                
                # Split text into chunks
                chunks = self._chunk_text(text)
                
                # Process chunks in very small batches
                batch_size = 5
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i:i+batch_size]
                    batch_embeddings = np.array([self._get_embedding(chunk) for chunk in batch])
                    
                    # Initialize or update FAISS index
                    if first_batch:
                        dimension = batch_embeddings.shape[1]
                        self.index = faiss.IndexFlatL2(dimension)
                        first_batch = False
                    
                    self.index.add(batch_embeddings.astype('float32'))
                    
                    # Update metadata
                    for j, chunk in enumerate(batch):
                        self.text_chunks.append(chunk)
                        self.metadata.append({
                            'page': page_num,
                            'chunk': i + j,
                            'document': pdf_path.stem
                        })
                    
                    # Clean up
                    del batch
                    del batch_embeddings
                    gc.collect()
                
                # Clean up page data
                del text
                del chunks
                gc.collect()
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
            
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar text chunks.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of search results with metadata
        """
        if not self.index:
            raise ValueError("No index available. Process a PDF first.")
            
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        # Search index
        distances, indices = self.index.search(
            np.array([query_embedding]).astype('float32'), 
            min(k, len(self.text_chunks))
        )
        
        # Format results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.text_chunks):  # Ensure valid index
                results.append({
                    'score': 1 / (1 + dist),  # Convert distance to similarity score
                    'page': self.metadata[idx]['page'],
                    'chunk': self.metadata[idx]['chunk'],
                    'document': self.metadata[idx]['document'],
                    'snippet': self.text_chunks[idx]
                })
        
        return results
        
    def export_rdf(self, output_path: Union[str, Path]) -> None:
        """Export RDF graph to file.
        
        Args:
            output_path: Path to save the RDF file
        """
        self.rdf_graph.serialize(destination=str(output_path), format='turtle')
        
    def save_index(self, output_path: Union[str, Path]) -> None:
        """Save FAISS index to file.
        
        Args:
            output_path: Path to save the index
        """
        if self.index:
            faiss.write_index(self.index, str(output_path))
        
    def load_index(self, input_path: Union[str, Path]) -> None:
        """Load FAISS index from file.
        
        Args:
            input_path: Path to the index file
        """
        self.index = faiss.read_index(str(input_path)) 