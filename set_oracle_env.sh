#!/bin/bash

# Oracle Wallet and Connection Settings
export TNS_ADMIN=~/Oracle/wallet
export ORACLE_HOME=~/Oracle/instantclient_19_16
export DYLD_LIBRARY_PATH=$ORACLE_HOME:$DYLD_LIBRARY_PATH
export PATH=$ORACLE_HOME:$PATH

# Database Credentials
export ORACLE_USER=admin
export ORACLE_PASSWORD=op://Development/Oracle-RDF/password

# Connection String
export ORACLE_DSN=tfm_high 