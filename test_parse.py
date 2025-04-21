from rdflib import Graph
from pathlib import Path

g = Graph()
guidance_path = Path("guidance.ttl")
print(f"Loading {guidance_path.absolute()}")
g.parse(str(guidance_path), format="turtle")
print("Successfully parsed guidance.ttl")
print(f"Graph contains {len(g)} triples") 