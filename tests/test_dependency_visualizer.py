"""Test, suite for dependency visualizer."""

import unittest
import pytest
import networkx as nx
from pathlib import Path
from ontology_framework.modules.dependency_visualizer import DependencyVisualizer

@pytest.fixture
def sample_graph():
    """Create a sample directed graph for testing."""
    G = nx.DiGraph()
    G.add_edge('A', 'B', type='import')
    G.add_edge('B', 'C', type='call')
    G.add_edge('C', 'D', type='assert')
    return G

@pytest.fixture
def output_dir(tmp_path):
    """Create a temporary output directory."""
    return tmp_path / "visualizations"

@pytest.fixture
def visualizer(output_dir):
    """Create a visualizer instance."""
    return DependencyVisualizer(output_dir)

def test_visualizer_initialization(visualizer, output_dir):
    """Test visualizer initialization."""
    assert visualizer.output_dir == output_dir
    assert output_dir.exists()
    
def test_visualize_graph(visualizer, sample_graph):
    """Test basic graph visualization."""
    output_path = visualizer.visualize_graph(sample_graph, "Test Graph")
    assert output_path.exists()
    assert output_path.suffix == '.png'
    
def test_visualize_dependency_types(visualizer, sample_graph):
    """Test visualization with different dependency types."""
    output_path = visualizer.visualize_dependency_types(sample_graph, "Test Types")
    assert output_path.exists()
    assert output_path.suffix == '.png'
    
def test_visualize_subgraph(visualizer, sample_graph):
    """Test subgraph visualization."""
    nodes = ['A', 'B', 'C']
    output_path = visualizer.visualize_subgraph(sample_graph, nodes, "Test Subgraph")
    assert output_path.exists()
    assert output_path.suffix == '.png'
    
def test_generate_report(visualizer, sample_graph, tmp_path):
    """Test report generation with multiple graphs."""
    graphs = {
        "Graph1": sample_graph,
        "Graph2": nx.DiGraph([('X', 'Y', {'type': 'import'})])
    }
    report_path = tmp_path / "report.md"
    visualizer.generate_report(graphs, report_path)
    
    assert report_path.exists()
    content = report_path.read_text()
    assert "# Dependency Analysis Report" in content
    assert "# # Graph1" in content
    assert "## Graph2" in content
    assert "Nodes: 4" in content  # Graph1 has 4 nodes
    assert "Nodes: 2" in content  # Graph2 has 2 nodes
    
def test_visualize_graph_layouts(visualizer, sample_graph):
    """Test different graph layouts."""
    layouts = ['spring', 'circular', 'random']
    for layout in layouts:
        output_path = visualizer.visualize_graph(sample_graph, f"Test {layout}", layout=layout)
        assert output_path.exists()
        
def test_visualize_graph_styles(visualizer, sample_graph):
    """Test different graph styles."""
    styles = [
        {'node_color': 'red', 'edge_color': 'blue'},
        {'node_size': 1000, 'font_size': 12}
    ]
    for style in styles:
        output_path = visualizer.visualize_graph(sample_graph, "Test Style", **style)
        assert output_path.exists() 