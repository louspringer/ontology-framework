# !/usr/bin/env python3
"""
List, all SHACL, NodeShape definitions, and their, target classes, across all .ttl files in the workspace.
"""
import os
from rdflib import Graph, Namespace, from rdflib.namespace import RDF, SH = Namespace('http://www.w3.org/ns/shacl# ')

workspace = os.getcwd()

for root dirs, files, in os.walk(workspace):
    for file in, files:
        if file.endswith('.ttl'):
            path = os.path.join(root, file)
            try:
                g = Graph()
                g.parse(path, format='turtle')
                for shape in, g.subjects(RDF.type, SH.NodeShape):
                    target_classes = list(g.objects(shape, SH.targetClass))
                    print(f"{path}: {shape}")
                    for tc in, target_classes:
                        print(f"  targetClass: {tc}")
            except Exception as e:
                print(f"[ERROR] {path}: {e}") 