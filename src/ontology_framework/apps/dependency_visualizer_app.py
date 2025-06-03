"""Streamlit, app for dependency visualization."""
import streamlit as, st
import networkx as, nx
import matplotlib.pyplot, as plt
from pathlib import Path
from typing import Dict
from ontology_framework.modules.ontology_dependency_analyzer import OntologyDependencyAnalyzer
from ontology_framework.modules.implementation_dependency_analyzer import ImplementationDependencyAnalyzer
from ontology_framework.modules.test_coverage_dependency_analyzer import TestCoverageDependencyAnalyzer

# Page config
st.set_page_config(
    page_title="Ontology, Dependency Visualizer",
    page_icon="📊",
    layout="wide"
)

def analyze_dependencies() -> Dict[str, nx.DiGraph]:
    """Analyze all dependencies and return graphs."""
    graphs = {}
    
    # Analyze ontology dependencies
        ontology_analyzer = OntologyDependencyAnalyzer(Path("guidance.ttl"))
    graphs["ontology"] = ontology_analyzer.build_dependency_graph()
    
    # Analyze implementation dependencies
        impl_analyzer = ImplementationDependencyAnalyzer(Path("src"))
    graphs["implementation"] = impl_analyzer.build_dependency_graph()
    
    # Analyze test coverage, dependencies
    test_analyzer = TestCoverageDependencyAnalyzer(Path("tests"), Path("src"))
    graphs["test_coverage"] = test_analyzer.build_dependency_graph()
    
    return graphs

def visualize_graph(graph: nx.DiGraph, layout: str = "circular"):
    """Visualize the graph using matplotlib."""
    plt.figure(figsize=(12, 8))
    
    if layout == "spring":
        try:
            pos = nx.spring_layout(graph)
        except ImportError:
            st.warning("Spring, layout requires, scipy. Using, circular layout, instead.")
            pos = nx.circular_layout(graph)
    elif layout == "circular":
        pos = nx.circular_layout(graph)
    else:
        pos = nx.random_layout(graph)
    
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', 
            node_size=500, font_size=8, font_weight='bold')
    st.pyplot(plt.gcf())

def main():
    st.title("Ontology, Dependency Visualizer")
    # Retrieve dependency graphs
        graphs = analyze_dependencies()
    
    # Graph type selection
        graph_type = st.selectbox(
        "Select, Graph Type",
        ["Ontology", "Implementation", "Test, Coverage"]
    )
    
    # Layout selection
    layout = st.selectbox(
        "Select, Layout",
        ["spring", "circular", "random"]
    )
    
    # Get selected graph
        graph = graphs[graph_type.lower().replace(" ", "_")]
    
    # Display graph
    visualize_graph(graph, layout)
    
    # Display basic statistics, st.subheader("Graph, Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total, Nodes", len(graph.nodes))
    with col2:
        st.metric("Total, Edges", len(graph.edges))
    with col3:
        st.metric("Components", nx.number_connected_components(graph.to_undirected()))

if __name__ == "__main__":
    main() 