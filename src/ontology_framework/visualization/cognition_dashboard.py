"""Interactive dashboard for visualizing AI cognition patterns and validation chains."""

from typing import Dict, List, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
import numpy as np
from datetime import datetime
import logging
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CognitionPattern:
    """Represents a detected cognition pattern."""
    pattern_type: str
    confidence: float
    timestamp: datetime
    context: Dict[str, Any]
    validation_chain: List[str]

@dataclass
class ValidationStep:
    """Represents a step in the validation chain."""
    step_id: str
    reasoning: str
    confidence: float
    dependencies: List[str]
    result: str

class CognitionDashboard:
    """Interactive dashboard for visualizing AI cognition and validation patterns."""
    
    def __init__(self):
        self.patterns: List[CognitionPattern] = []
        self.validation_chains: Dict[str, List[ValidationStep]] = {}
        
    def add_pattern(self, pattern: CognitionPattern) -> None:
        """Add a new cognition pattern to the dashboard."""
        self.patterns.append(pattern)
        self.validation_chains[pattern.pattern_type] = [
            ValidationStep(
                step_id=f"step_{i}",
                reasoning=step,
                confidence=pattern.confidence,
                dependencies=[],
                result="success"
            ) for i, step in enumerate(pattern.validation_chain)
        ]
        
    def create_dashboard(self, output_path: Path) -> None:
        """Generate the interactive dashboard."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Cognition Pattern Network",
                "Validation Chain Flow",
                "Confidence Timeline",
                "Pattern Context"
            ),
            specs=[
                [{"type": "scatter3d"}, {"type": "sankey"}],
                [{"type": "scatter"}, {"type": "heatmap"}]
            ]
        )
        
        # 1. Cognition Pattern Network (3D Scatter)
        self._add_pattern_network(fig, row=1, col=1)
        
        # 2. Validation Chain Flow (Sankey)
        self._add_validation_flow(fig, row=1, col=2)
        
        # 3. Confidence Timeline (Scatter)
        self._add_confidence_timeline(fig, row=2, col=1)
        
        # 4. Pattern Context (Heatmap)
        self._add_pattern_context(fig, row=2, col=2)
        
        # Update layout
        fig.update_layout(
            title="AI Cognition and Validation Dashboard",
            showlegend=True,
            height=1200,
            width=1600
        )
        
        # Save the dashboard
        fig.write_html(str(output_path))
        logger.info(f"Dashboard saved to {output_path}")
        
    def _add_pattern_network(self, fig: go.Figure, row: int, col: int) -> None:
        """Add 3D network visualization of cognition patterns."""
        G = nx.DiGraph()
        
        # Create a mapping of pattern types to confidences
        pattern_confidences = {
            pattern.pattern_type: pattern.confidence
            for pattern in self.patterns
        }
        
        # Add nodes and edges
        for pattern in self.patterns:
            G.add_node(pattern.pattern_type)
            for step in pattern.validation_chain:
                G.add_node(step)
                G.add_edge(pattern.pattern_type, step)
        
        # Get positions for 3D layout
        pos = nx.spring_layout(G, dim=3)
        
        # Create 3D scatter plot
        x, y, z = zip(*[pos[node] for node in G.nodes()])
        
        # Calculate node sizes based on confidence (if available)
        node_sizes = [
            pattern_confidences.get(node, 0.5) * 20
            for node in G.nodes()
        ]
        
        # Calculate node colors based on confidence
        node_colors = [
            pattern_confidences.get(node, 0.5)
            for node in G.nodes()
        ]
        
        fig.add_trace(
            go.Scatter3d(
                x=x, y=y, z=z,
                mode='markers+text',
                text=list(G.nodes()),
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    colorscale='Viridis',
                    opacity=0.8
                ),
                textposition="top center"
            ),
            row=row, col=col
        )
        
    def _add_validation_flow(self, fig: go.Figure, row: int, col: int) -> None:
        """Add Sankey diagram for validation flow."""
        # Collect all unique nodes and links
        nodes = set()
        links = []
        
        for pattern_type, chain in self.validation_chains.items():
            nodes.add(pattern_type)
            for i, step in enumerate(chain[:-1]):
                nodes.add(step.step_id)
                links.append({
                    'source': pattern_type if i == 0 else chain[i-1].step_id,
                    'target': step.step_id,
                    'value': step.confidence
                })
        
        # Convert nodes to list to maintain order
        node_list = list(nodes)
        
        fig.add_trace(
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=node_list,
                    color="lightblue"
                ),
                link=dict(
                    source=[node_list.index(l['source']) for l in links],
                    target=[node_list.index(l['target']) for l in links],
                    value=[l['value'] for l in links]
                )
            ),
            row=row, col=col
        )
        
    def _add_confidence_timeline(self, fig: go.Figure, row: int, col: int) -> None:
        """Add timeline of confidence levels."""
        timestamps = [p.timestamp for p in self.patterns]
        confidences = [p.confidence for p in self.patterns]
        pattern_types = [p.pattern_type for p in self.patterns]
        
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=confidences,
                mode='markers+lines',
                text=pattern_types,
                marker=dict(
                    size=10,
                    color=confidences,
                    colorscale='Viridis',
                    showscale=True
                )
            ),
            row=row, col=col
        )
        
    def _add_pattern_context(self, fig: go.Figure, row: int, col: int) -> None:
        """Add heatmap of pattern context relationships."""
        # Extract context features
        context_features = set()
        for pattern in self.patterns:
            context_features.update(pattern.context.keys())
        
        # Create context matrix
        context_matrix = np.zeros((len(self.patterns), len(context_features)))
        for i, pattern in enumerate(self.patterns):
            for j, feature in enumerate(sorted(context_features)):
                context_matrix[i, j] = pattern.context.get(feature, 0)
        
        fig.add_trace(
            go.Heatmap(
                z=context_matrix,
                x=list(sorted(context_features)),
                y=[p.pattern_type for p in self.patterns],
                colorscale='Viridis'
            ),
            row=row, col=col
        ) 