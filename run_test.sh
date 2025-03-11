#!/bin/bash
export TNS_ADMIN=$WALLET_LOCATION

# Create a temporary SQL*Plus script with login
cat > login.sql << EOL
CONNECT ADMIN/op://Development/Oracle-RDF/password@tfm_high
@test_sparql.sql
EOL

# Run SQL*Plus with the temporary script
sqlplus /nolog @login.sql

# Clean up
rm login.sql 