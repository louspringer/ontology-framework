#!/usr/bin/env python3
"""
Visualize ontology dependencies and duplicates as a UML/static structure graph.
"""
import os
from rdflib import Graph, URIRef
from graphviz import Digraph
from collections import defaultdict
from rdflib.compare import isomorphic

MODULES_DIR = "guidance/modules"
OUTPUT_DOT = "ontology_dependency_graph.dot"
OUTPUT_PNG = "ontology_dependency_graph.png"
OUTPUT_SVG = "ontology_dependency_graph.svg"

# Step 1: Collect all ontology files
files = [os.path.join(MODULES_DIR, f) for f in os.listdir(MODULES_DIR) if f.endswith('.ttl') or f.endswith('.rdf')]

# Step 1.5: Detect isomorphic .ttl/.rdf pairs and exclude them
# Map base name to .ttl and .rdf
base_map = defaultdict(dict)
for f in files:
    base, ext = os.path.splitext(os.path.basename(f))
    base_map[base][ext] = f

isomorphic_pairs = set()
for base, exts in base_map.items():
    if '.ttl' in exts and '.rdf' in exts:
        g1 = Graph()
        g2 = Graph()
        try:
            g1.parse(exts['.ttl'])
            g2.parse(exts['.rdf'])
            if isomorphic(g1, g2):
                isomorphic_pairs.add(exts['.ttl'])
                isomorphic_pairs.add(exts['.rdf'])
        except Exception:
            continue

# Filter files to exclude isomorphic pairs
files = [f for f in files if f not in isomorphic_pairs]

# Step 2: Build dependency graph and IRI map
deps = defaultdict(set)  # file -> set of dependencies
iri_map = defaultdict(set)  # IRI -> set of files
for f in files:
    g = Graph()
    try:
        g.parse(f)
    except Exception:
        continue
    for s, p, o in g:
        if p.endswith("imports") and isinstance(o, URIRef):
            deps[f].add(str(o))
        if p.endswith("subClassOf") and isinstance(o, URIRef):
            deps[f].add(str(o))
        if p.endswith("domain") and isinstance(o, URIRef):
            deps[f].add(str(o))
        if p.endswith("range") and isinstance(o, URIRef):
            deps[f].add(str(o))
        if isinstance(s, URIRef):
            iri_map[str(s)].add(f)
        if isinstance(o, URIRef):
            iri_map[str(o)].add(f)

# Step 3: Find duplicates
duplicates = {iri: list(paths) for iri, paths in iri_map.items() if len(paths) > 1}

# Step 4: Build Graphviz graph
dot = Digraph(comment="Ontology Dependency Graph", format="png")
for f in files:
    label = os.path.basename(f)
    dot.node(f, label=label, shape="box", style="filled", fillcolor="#e0e0e0")
for f, targets in deps.items():
    for t in targets:
        # Try to resolve t to a file node
        t_file = next((ff for ff in files if t in ff or os.path.basename(t) in ff), None)
        if t_file:
            dot.edge(f, t_file, color="#8888ff")
        else:
            dot.node(t, label=os.path.basename(t), shape="ellipse", style="dashed", color="#ff8888")
            dot.edge(f, t, color="#ff8888", style="dashed")
# Highlight duplicate IRIs
for iri, paths in duplicates.items():
    for f in paths:
        dot.node(f, style="filled", fillcolor="#ffcccc")

# Step 5: Output DOT and render
with open(OUTPUT_DOT, "w") as f:
    f.write(dot.source)
dot.render(OUTPUT_PNG, view=False)
dot.render(OUTPUT_SVG, view=False)
print(f"Dependency graph written to {OUTPUT_DOT}, {OUTPUT_PNG}, {OUTPUT_SVG}")
print(f"Found {len(duplicates)} duplicate IRIs. See DOT for highlights.")

def is_project_iri(iri):
    return not (
        iri.startswith("http://www.w3.org/") or
        iri.startswith("http://example.org/") or
        iri.startswith("http://example.com/")
    )

# Filter duplicates to only project IRIs
project_duplicates = {iri: paths for iri, paths in duplicates.items() if is_project_iri(iri)}

# Step 6: Print top 60 project duplicates as Markdown
sorted_dupes = sorted(project_duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:60]
print("\nTop 60 Most Duplicated Project IRIs (Markdown Table):\n")
print("| IRI | # Files | Files |")
print("|---|---|---|")
for iri, files in sorted_dupes:
    file_list = ', '.join([os.path.basename(f) for f in files])
    print(f"| `{iri}` | {len(files)} | {file_list} |")

# Redefinitions: filter to project IRIs
def_types = {
    "http://www.w3.org/2002/07/owl#Class",
    "http://www.w3.org/2002/07/owl#ObjectProperty",
    "http://www.w3.org/2002/07/owl#DatatypeProperty",
    "http://www.w3.org/2002/07/owl#NamedIndividual"
}
def_map = defaultdict(set)  # IRI -> set of files where defined
for f in files:
    g = Graph()
    try:
        g.parse(f)
    except Exception:
        continue
    for s, p, o in g.triples((None, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), None)):
        if str(o) in def_types and isinstance(s, URIRef) and is_project_iri(str(s)):
            def_map[str(s)].add(f)

redefs = {iri: list(paths) for iri, paths in def_map.items() if len(paths) > 1}

# Print top 60 project redefinitions as Markdown
sorted_redefs = sorted(redefs.items(), key=lambda x: len(x[1]), reverse=True)[:60]
print("\nTop 60 Most Redefined Project IRIs (Markdown Table):\n")
print("| IRI | # Files | Files |")
print("|---|---|---|")
for iri, files in sorted_redefs:
    file_list = ', '.join([os.path.basename(f) for f in files])
    print(f"| `{iri}` | {len(files)} | {file_list} |") 