#!/usr/bin/env python3
"""Script to load all transformed ontologies into Oracle RDF store."""

import glob
import logging
import sys
from pathlib import Path
import oracledb
from ontology_framework.load_to_oracle import (
    setup_semantic_network, 
    check_prerequisites,
    connect_to_oracle,
    load_ontology_to_oracle
)
import os
from typing import Optional, Union
from rdflib import Graph, URIRef, Namespace, BNode, Literal
import time
from datetime import datetime

# Set up logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('load_ontologies.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_tracking_table(cursor):
    """Create table to track ontology loading status if it doesn't exist."""
    try:
        cursor.execute("""
            CREATE TABLE ONTOLOGY_LOAD_TRACKING (
                model_name VARCHAR2(30) PRIMARY KEY,
                file_name VARCHAR2(200) NOT NULL,
                load_status VARCHAR2(20) DEFAULT 'PENDING',
                load_timestamp TIMESTAMP DEFAULT SYSTIMESTAMP,
                job_instance VARCHAR2(50),
                error_message VARCHAR2(4000)
            )
        """)
        cursor.execute("COMMIT")
        logger.info("Created ontology load tracking table")
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        if "ORA-00955" not in str(error_obj.message):  # Table already exists
            raise
        logger.info("Ontology load tracking table already exists")

def get_unloaded_ontologies(cursor):
    """Get list of ontologies that haven't been successfully loaded."""
    cursor.execute("""
        SELECT file_name 
        FROM ONTOLOGY_LOAD_TRACKING 
        WHERE load_status = 'PENDING' 
        OR load_status = 'FAILED'
        ORDER BY load_timestamp ASC
    """)
    return [row[0] for row in cursor.fetchall()]

def initialize_tracking(cursor, ontology_files):
    """Initialize tracking for ontologies not yet in tracking table."""
    for file_path in ontology_files:
        model_name = Path(file_path).stem.upper()
        if model_name.startswith('TRANSFORMED_'):
            model_name = model_name[12:]
            
        cursor.execute("""
            MERGE INTO ONTOLOGY_LOAD_TRACKING t
            USING (SELECT :1 as file_name, :2 as model_name FROM DUAL) s
            ON (t.file_name = s.file_name)
            WHEN NOT MATCHED THEN
                INSERT (file_name, model_name)
                VALUES (s.file_name, s.model_name)
        """, (file_path, model_name))
    cursor.execute("COMMIT")

def update_load_status(cursor, file_name, status, error_msg=None):
    """Update the load status for an ontology."""
    job_instance = f"load_{os.getpid()}_{int(time.time())}"
    cursor.execute("""
        UPDATE ONTOLOGY_LOAD_TRACKING
        SET load_status = :1,
            load_timestamp = SYSTIMESTAMP,
            job_instance = :2,
            error_message = :3
        WHERE file_name = :4
    """, (status, job_instance, error_msg, file_name))
    cursor.execute("COMMIT")

def main():
    """Main function to load transformed ontologies into Oracle."""
    logger.info("Starting ontology loading script...")
    
    # Get Oracle connection
    connection = connect_to_oracle()
    if not connection:
        logger.error("Failed to connect to Oracle database")
        return
    
    try:
        cursor = connection.cursor()
        
        # Check prerequisites and setup semantic network
        logger.info("Checking Oracle prerequisites...")
        check_prerequisites(connection)
        
        logger.info("Setting up semantic network...")
        setup_semantic_network(connection)
        
        # Create tracking table if it doesn't exist
        create_tracking_table(cursor)
        
        # Find all transformed ontology files
        ontology_files = glob.glob("transformed_*.ttl")
        logger.info(f"Found {len(ontology_files)} transformed ontology files")
        
        # Initialize tracking for new files
        initialize_tracking(cursor, ontology_files)
        
        # Get unloaded ontologies
        unloaded_files = get_unloaded_ontologies(cursor)
        files_to_process = unloaded_files[:3]  # Only process first 3 unloaded files
        
        logger.info(f"Processing {len(files_to_process)} out of {len(unloaded_files)} unloaded ontologies")
        
        for file_path in files_to_process:
            logger.info(f"Loading ontology file: {file_path}")
            try:
                # Load the ontology into Oracle
                load_ontology_to_oracle(connection, file_path)
                
                # Update status to SUCCESS
                update_load_status(cursor, file_path, 'SUCCESS')
                logger.info(f"Successfully loaded {file_path}")
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error processing {file_path}: {error_msg}")
                update_load_status(cursor, file_path, 'FAILED', error_msg)
                continue
        
        logger.info("Completed ontology loading process")
        
    except Exception as e:
        logger.error(f"Error during ontology loading: {e}")
    finally:
        connection.close()
        logger.info("Closed Oracle connection")

if __name__ == "__main__":
    main() 