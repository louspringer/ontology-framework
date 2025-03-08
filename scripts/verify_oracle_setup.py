#!/usr/bin/env python3
"""Script to verify Oracle RDF store setup."""

import os
import sys
from typing import Dict, List, Optional, Tuple

import oracledb


def check_environment() -> Tuple[bool, List[str]]:
    """Check required environment variables.
    
    Returns:
        Tuple of (is_valid, missing_vars)
    """
    required_vars = ["ORACLE_USER", "ORACLE_PASSWORD", "ORACLE_DSN"]
    missing = [var for var in required_vars if not os.getenv(var)]
    return len(missing) == 0, missing


def get_oracle_connection() -> Optional[oracledb.Connection]:
    """Get Oracle database connection.
    
    Returns:
        Oracle connection if successful, None otherwise
    """
    try:
        connection = oracledb.connect(
            user=os.getenv("ORACLE_USER", "ADMIN"),
            password=os.getenv("ORACLE_PASSWORD", "your_password"),
            dsn=os.getenv("ORACLE_DSN", "tfm_medium")
        )
        return connection
    except Exception as e:
        print(f"Error connecting to Oracle: {e}")
        return None


def check_java_installation(connection: oracledb.Connection) -> bool:
    """Check if Java is installed in Oracle.
    
    Args:
        connection: Oracle database connection
        
    Returns:
        True if Java is available, False otherwise
    """
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT 1 FROM DUAL 
            WHERE EXISTS (
                SELECT * FROM ALL_OBJECTS 
                WHERE OBJECT_NAME = 'JAVA_INFO'
            )
        """)
        return bool(cursor.fetchone())
    except Exception as e:
        print(f"Error checking Java installation: {e}")
        return False


def check_rdf_support(connection: oracledb.Connection) -> Dict[str, bool]:
    """Check RDF-related features.
    
    Args:
        connection: Oracle database connection
        
    Returns:
        Dictionary of feature status
    """
    features = {
        "semantic_network": False,
        "rdf_views": False,
        "sem_apis": False,
        "user_permissions": False
    }
    
    try:
        cursor = connection.cursor()
        
        # Check semantic network
        cursor.execute("""
            SELECT COUNT(*) 
            FROM ALL_TABLES 
            WHERE TABLE_NAME = 'RDF_PARAMETER_TABLE' 
            AND OWNER = 'MDSYS'
        """)
        features["semantic_network"] = cursor.fetchone()[0] > 0
        
        # Check RDF views
        cursor.execute("""
            SELECT COUNT(*) 
            FROM ALL_VIEWS 
            WHERE VIEW_NAME LIKE 'SEM_%' 
            AND OWNER = 'MDSYS'
        """)
        features["rdf_views"] = cursor.fetchone()[0] > 0
        
        # Check SEM_APIS package
        cursor.execute("""
            SELECT COUNT(*) 
            FROM ALL_OBJECTS 
            WHERE OBJECT_NAME = 'SEM_APIS' 
            AND OWNER = 'MDSYS'
        """)
        features["sem_apis"] = cursor.fetchone()[0] > 0
        
        # Check user permissions
        cursor.execute("""
            SELECT COUNT(*) 
            FROM USER_SYS_PRIVS 
            WHERE PRIVILEGE IN ('CREATE ANY TABLE', 'CREATE PROCEDURE')
        """)
        features["user_permissions"] = cursor.fetchone()[0] >= 2
        
    except Exception as e:
        print(f"Error checking RDF support: {e}")
    
    return features


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("Verifying Oracle RDF store setup...")
    
    # Check environment variables
    env_valid, missing_vars = check_environment()
    if not env_valid:
        print("\nMissing environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        return 1
    
    # Get database connection
    connection = get_oracle_connection()
    if not connection:
        print("\nFailed to connect to Oracle database")
        return 1
    
    # Check Java installation
    print("\nChecking Java installation...")
    if not check_java_installation(connection):
        print("❌ Java is not installed in Oracle database")
        print("Please install Java using:")
        print("  1. Log in as SYSDBA")
        print("  2. Run: @$ORACLE_HOME/javavm/install/initjvm.sql")
        return 1
    print("✅ Java is installed")
    
    # Check RDF features
    print("\nChecking RDF features...")
    features = check_rdf_support(connection)
    
    all_features_available = all(features.values())
    
    for feature, available in features.items():
        status = "✅" if available else "❌"
        print(f"{status} {feature.replace('_', ' ').title()}")
    
    if not all_features_available:
        print("\nSome RDF features are not available.")
        print("Please ensure:")
        print("1. Semantic network is created")
        print("2. RDF views are installed")
        print("3. SEM_APIS package is available")
        print("4. User has required permissions")
        return 1
    
    print("\n✅ Oracle RDF store is properly configured")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 