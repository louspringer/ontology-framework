#!/bin/bash

# Oracle Database Configuration
export ORACLE_HOME=/opt/oracle/instantclient_19_8
export LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH

# Database Credentials
export ORACLE_USER=ontology_admin
export ORACLE_PASSWORD="op://Development/Oracle-RDF/password"
export ORACLE_DSN=localhost:1521/XEPDB1

# Optional: Set other environment variables as needed
# export ORACLE_SID=XE
# export NLS_LANG=AMERICAN_AMERICA.AL32UTF8

# Oracle Wallet and Connection Settings
export TNS_ADMIN=~/Oracle/wallet
export DYLD_LIBRARY_PATH=$ORACLE_HOME:$DYLD_LIBRARY_PATH
export PATH=$ORACLE_HOME:$PATH 