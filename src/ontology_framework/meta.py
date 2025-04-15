from rdflib import Namespace, URIRef

# Define namespaces
META = Namespace("http://example.org/meta#")

# Define classes
Patch = URIRef(str(META) + "Patch")
AddOperation = URIRef(str(META) + "AddOperation")
RemoveOperation = URIRef(str(META) + "RemoveOperation")

# Define properties
dependsOn = URIRef(str(META) + "dependsOn")
addTriple = URIRef(str(META) + "addTriple")
removeTriple = URIRef(str(META) + "removeTriple") 