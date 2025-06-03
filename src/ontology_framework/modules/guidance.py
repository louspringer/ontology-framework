"""
Guidance ontology management module.

This module provides classes and utilities for managing ontological guidance,
including validation rules, conformance tracking, and relationship analysis.
"""

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Any, Union, TypedDict, cast
from pathlib import Path
from collections import defaultdict

from rdflib import Graph, URIRef, Literal as RDFLiteral, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH

from .template_ontology import TemplateOntology


class Stakeholder(Enum):
    """Different stakeholders with varying priorities."""
    DEVELOPER = "developer"
    DOMAIN_EXPERT = "domain_expert"
    DATA_ENGINEER = "data_engineer"
    END_USER = "end_user"
    GOVERNANCE = "governance"
    SECURITY = "security"

    @property
    def priority_dimensions(self) -> Dict[str, float]:
        """Get priority weights for different knowledge dimensions."""
        priorities = {
            Stakeholder.DEVELOPER: {
                "structural": 0.8, "functional": 0.9, "temporal": 0.6,
                "semantic": 0.7, "social": 0.4, "security": 0.5, "compliance": 0.3
            },
            Stakeholder.DOMAIN_EXPERT: {
                "semantic": 0.9, "structural": 0.7, "compliance": 0.8,
                "functional": 0.6, "temporal": 0.5, "social": 0.7, "security": 0.4
            },
            Stakeholder.DATA_ENGINEER: {
                "functional": 0.9, "structural": 0.8, "temporal": 0.7,
                "semantic": 0.6, "security": 0.8, "social": 0.3, "compliance": 0.6
            },
            Stakeholder.END_USER: {
                "functional": 0.8, "semantic": 0.7, "social": 0.6,
                "structural": 0.4, "temporal": 0.3, "security": 0.5, "compliance": 0.4
            },
            Stakeholder.GOVERNANCE: {
                "compliance": 0.9, "security": 0.8, "social": 0.7,
                "semantic": 0.6, "temporal": 0.7, "structural": 0.5, "functional": 0.4
            },
            Stakeholder.SECURITY: {
                "security": 0.9, "compliance": 0.8, "temporal": 0.6,
                "structural": 0.7, "functional": 0.7, "semantic": 0.5, "social": 0.4
            }
        }
        return priorities.get(self, {})


class KnowledgeDimension(Enum):
    """Different dimensions of relationship knowledge."""
    STRUCTURAL = "structural"  # Class hierarchy, property definitions
    SEMANTIC = "semantic"      # Meaning and constraints
    FUNCTIONAL = "functional"  # How it's used in practice
    TEMPORAL = "temporal"     # Historical stability
    SOCIAL = "social"         # Community usage and acceptance
    SECURITY = "security"     # Security implications
    COMPLIANCE = "compliance" # Regulatory/policy compliance


@dataclass
class StakeholderView:
    """Represents a stakeholder's view of a requirement."""
    satisfaction_score: float = 0.0  # 0.0 to 1.0
    importance_weight: float = 1.0   # How important this is to them
    feedback: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

    def update_satisfaction(self, score: float, requirement: str, is_met: bool) -> None:
        """Update satisfaction score and add feedback."""
        self.satisfaction_score = max(0.0, min(1.0, score))
        status = "met" if is_met else "not met"
        self.feedback.append(f"Requirement '{requirement}' {status} (score: {score:.2f})")
        self.last_updated = datetime.now()


@dataclass
class DimensionalScore:
    """Score for a specific knowledge dimension."""
    dimension: KnowledgeDimension
    score: float = 0.0  # 0.0 to 1.0
    confidence: float = 0.0  # Confidence in the score
    evidence: List[str] = field(default_factory=list)
    stakeholder_views: Dict[Stakeholder, StakeholderView] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)

    def update_score(self, new_score: float, evidence: str, stakeholder: Optional[Stakeholder] = None) -> None:
        """Update the dimensional score with new evidence."""
        # Weight new score with existing score
        if self.score == 0.0:
            self.score = new_score
        else:
            self.score = (self.score + new_score) / 2
        
        self.evidence.append(f"{datetime.now().isoformat()}: {evidence}")
        self.last_updated = datetime.now()
        
        if stakeholder:
            if stakeholder not in self.stakeholder_views:
                self.stakeholder_views[stakeholder] = StakeholderView()
            self.stakeholder_views[stakeholder].update_satisfaction(new_score, evidence, new_score >= 0.5)

    def get_stakeholder_score(self, stakeholder: Stakeholder) -> float:
        """Get weighted score from a specific stakeholder's perspective."""
        if stakeholder not in self.stakeholder_views:
            return self.score  # Default to general score
        
        view = self.stakeholder_views[stakeholder]
        return self.score * view.importance_weight * view.satisfaction_score


@dataclass
class ChangeRate:
    """Tracks rate of change over time."""
    changes: List[Tuple[datetime, float]] = field(default_factory=list)

    def add_change(self, magnitude: float) -> None:
        """Add a change measurement."""
        self.changes.append((datetime.now(), magnitude))

    def get_rate(self) -> float:
        """Calculate recent rate of change."""
        if len(self.changes) < 2:
            return 0.0
        
        # Look at last 7 days
        cutoff = datetime.now() - timedelta(days=7)
        recent_changes = [(t, m) for t, m in self.changes if t > cutoff]
        
        if len(recent_changes) < 2:
            return 0.0
        
        total_change = sum(m for _, m in recent_changes)
        time_span = (recent_changes[-1][0] - recent_changes[0][0]).total_seconds()
        
        return total_change / max(time_span, 1.0)


@dataclass
class TensionPoint:
    """Represents a point of productive tension in the system."""
    source: str
    target: str
    nature: str
    strength: float = 0.0  # 0.0 to 1.0, how much this tension influences the system
    emergence_time: datetime = field(default_factory=datetime.now)
    observations: List[str] = field(default_factory=list)
    change_rate: ChangeRate = field(default_factory=ChangeRate)

    def add_observation(self, observation: str, change_magnitude: float = 1.0) -> None:
        """Add an observation about this tension point."""
        self.observations.append(f"{datetime.now().isoformat()}: {observation}")
        self.change_rate.add_change(change_magnitude)

    @property
    def urgency(self) -> float:
        """Calculate urgency based on strength and change rate."""
        rate = self.change_rate.get_rate()
        return min(1.0, self.strength + (rate * 0.3))


@dataclass
class PhaseTransition:
    """Represents a phase transition in organizational structure."""
    from_level: 'BoundaryLevel'
    to_level: 'BoundaryLevel'
    trigger_stress: float
    transition_time: datetime = field(default_factory=datetime.now)
    stability_period: Optional[timedelta] = None
    

class BoundaryLevel(Enum):
    """Quantum-like organizational boundaries where phase transitions occur."""
    INDIVIDUAL = "individual"      # Single entity (1)
    PAIR = "pair"                 # Dyadic relationship (2)
    IMMEDIATE = "immediate"       # Core group (7-12)
    TRIBE = "tribe"              # Extended group (50-150)
    COMMUNITY = "community"      # Local community (300-1000)
    SOCIETY = "society"          # Broader society (1000+)

    @property
    def threshold_range(self) -> Tuple[int, int]:
        """Get the size range for this boundary level."""
        ranges = {
            BoundaryLevel.INDIVIDUAL: (1, 1),
            BoundaryLevel.PAIR: (2, 2),
            BoundaryLevel.IMMEDIATE: (7, 12),
            BoundaryLevel.TRIBE: (50, 150),
            BoundaryLevel.COMMUNITY: (300, 1000),
            BoundaryLevel.SOCIETY: (1000, 999999999)  # Use very large int instead of float('inf')
        }
        return ranges[self]


class ConfidenceLevel(Enum):
    """Overall confidence level based on dimensional scores."""
    UNKNOWN = auto()     # No significant knowledge
    EMERGING = auto()    # Beginning to understand
    ESTABLISHED = auto() # Good understanding in some dimensions
    VERIFIED = auto()    # Verified in multiple dimensions
    COMPLETE = auto()    # High confidence across all relevant dimensions


class RelationType(Enum):
    """Types of relationships between ontology elements."""
    SUBCLASS = "subClassOf"
    INSTANCE = "type"
    PROPERTY = "property"
    SEMANTIC = "semantic"
    SHAPE = "shape"
    UNKNOWN = "unknown"


@dataclass
class QuantumState:
    """Represents a quantum-like organizational state."""
    level: BoundaryLevel
    state_vector: Dict[str, float]
    stability_score: float = 0.0
    measurement_time: datetime = field(default_factory=datetime.now)


@dataclass
class BoundaryResonance:
    """Tracks resonance patterns between different boundary levels."""
    primary_level: BoundaryLevel
    resonant_level: BoundaryLevel
    strength: float = 0.0  # Resonance strength
    phase_alignment: float = 0.0  # 0 to 2π
    observations: List[str] = field(default_factory=list)


@dataclass
class BoundaryEffect:
    """Tracks effects and transitions at organizational boundaries."""
    level: BoundaryLevel
    current_size: int = 1
    stress_history: List[Tuple[datetime, float]] = field(default_factory=list)
    transitions: List[PhaseTransition] = field(default_factory=list)
    resonances: List[BoundaryResonance] = field(default_factory=list)
    quantum_states: Dict[str, QuantumState] = field(default_factory=dict)

    def detect_resonance(self, other: 'BoundaryEffect', window: timedelta = timedelta(days=30)) -> Optional[BoundaryResonance]:
        """Detect resonance patterns between boundary levels."""
        if not (self.stress_history and other.stress_history):
            return None
            
        # Get recent stress patterns
        cutoff = datetime.now() - window
        self_recent = [(t, s) for t, s in self.stress_history if t > cutoff]
        other_recent = [(t, s) for t, s in other.stress_history if t > cutoff]
        
        if len(self_recent) < 2 or len(other_recent) < 2:
            return None
            
        # Calculate phase alignment
        self_phase = self._calculate_phase(self_recent)
        other_phase = self._calculate_phase(other_recent)
        phase_diff = abs(self_phase - other_phase)
        
        # Calculate resonance strength based on pattern similarity
        self_pattern = [s for _, s in self_recent]
        other_pattern = [s for _, s in other_recent]
        pattern_similarity = self._calculate_pattern_similarity(self_pattern, other_pattern)
        
        if pattern_similarity > 0.7:  # Strong resonance threshold
            resonance = BoundaryResonance(
                primary_level=self.level,
                resonant_level=other.level,
                strength=pattern_similarity,
                phase_alignment=phase_diff
            )
            resonance.observations.append(
                f"Strong resonance detected between {self.level.value} and {other.level.value} "
                f"boundaries (strength: {pattern_similarity:.2f}, phase diff: {phase_diff:.2f})"
            )
            return resonance
        return None

    def _calculate_phase(self, stress_points: List[Tuple[datetime, float]]) -> float:
        """Calculate the phase of a stress pattern using FFT-like analysis."""
        if len(stress_points) < 2:
            return 0.0
            
        # Convert to time series
        times = [(t - stress_points[0][0]).total_seconds() for t, _ in stress_points]
        values = [s for _, s in stress_points]
        
        # Simple phase calculation using peak detection
        if len(times) >= 3:
            # Find local maxima
            peaks = [i for i in range(1, len(values)-1) 
                    if values[i] > values[i-1] and values[i] > values[i+1]]
            if peaks:
                # Use time to first peak for phase
                return (2 * math.pi * times[peaks[0]]) / times[-1]
        return 0.0

    def _calculate_pattern_similarity(self, pattern1: List[float], pattern2: List[float]) -> float:
        """Calculate similarity between two stress patterns."""
        if not pattern1 or not pattern2:
            return 0.0
            
        # Normalize patterns to same length
        len1, len2 = len(pattern1), len(pattern2)
        if len1 > len2:
            pattern1 = pattern1[:len2]
        elif len2 > len1:
            pattern2 = pattern2[:len1]
            
        # Calculate correlation
        mean1 = sum(pattern1)/len(pattern1)
        mean2 = sum(pattern2)/len(pattern2)
        diff1 = [x - mean1 for x in pattern1]
        diff2 = [x - mean2 for x in pattern2]
        
        numerator = sum(d1 * d2 for d1, d2 in zip(diff1, diff2))
        denominator = math.sqrt(sum(d1 * d1 for d1 in diff1) * sum(d2 * d2 for d2 in diff2))
        
        if denominator == 0:
            return 0.0
        return abs(numerator / denominator)  # Use absolute value for similarity

    def update_quantum_state(self, current_stress: float) -> Optional[str]:
        """Update quantum state based on current conditions."""
        current_state = self._identify_quantum_state(current_stress)
        state_id = f"{self.level.value}_{len(self.quantum_states)}"
        
        if state_id not in self.quantum_states:
            # New quantum state discovered
            self.quantum_states[state_id] = QuantumState(
                level=self.level,
                state_vector=current_state,
                stability_score=self._calculate_stability(current_state)
            )
            return f"New quantum state discovered at {self.level.value} boundary: {state_id}"
        return None

    def _identify_quantum_state(self, stress: float) -> Dict[str, float]:
        """Identify current quantum state characteristics."""
        state = {
            "size": float(self.current_size),
            "stress": stress,
            "change_rate": self._calculate_recent_rate(),
            "coherence": self._calculate_coherence()
        }
        return state

    def _calculate_stability(self, state: Dict[str, float]) -> float:
        """Calculate stability score for a quantum state."""
        # Higher stability when size is well within boundary range
        min_size, max_size = self.level.threshold_range
        size_stability = 1.0 - (2 * abs(state["size"] - (min_size + max_size)/2) / (max_size - min_size))
        
        # Lower stability with high stress or change rate
        dynamic_stability = 1.0 - (state["stress"] + state["change_rate"]) / 2
        
        # Higher stability with better coherence
        coherence_factor = state["coherence"]
        
        return (size_stability + dynamic_stability + coherence_factor) / 3

    def _calculate_coherence(self) -> float:
        """Calculate coherence of current organizational state."""
        if len(self.stress_history) < 3:
            return 1.0  # Assume coherent if not enough history
            
        # Calculate variation in stress patterns
        recent_stresses = [s for _, s in self.stress_history[-10:]]
        if not recent_stresses:
            return 1.0
        
        mean_stress = sum(recent_stresses) / len(recent_stresses)
        variance = sum((s - mean_stress) ** 2 for s in recent_stresses) / len(recent_stresses)
        
        # Higher variance = lower coherence
        return 1.0 / (1.0 + variance)

    def is_near_threshold(self, tolerance: float = 0.1) -> bool:
        """Check if current size is near a boundary threshold."""
        min_size, max_size = self.level.threshold_range
        if min_size == max_size:
            return self.current_size == min_size
        
        # Check if we're within tolerance of either boundary
        lower_bound = min_size * (1 - tolerance)
        upper_bound = max_size * (1 + tolerance) if max_size != float('inf') else float('inf')
        return lower_bound <= self.current_size <= upper_bound

    def add_stress(self, stress: float) -> Optional[PhaseTransition]:
        """Add stress measurement and detect phase transitions."""
        now = datetime.now()
        self.stress_history.append((now, stress))
        
        # Keep only recent history
        cutoff = now - timedelta(days=30)
        self.stress_history = [(t, s) for t, s in self.stress_history if t > cutoff]
        
        # Check for phase transition if near threshold
        if self.is_near_threshold() and len(self.stress_history) >= 2:
            recent_rate = self._calculate_recent_rate()
            if recent_rate > 0.5:  # High change rate threshold
                # Determine transition direction
                if stress > 0.7:  # High stress pushes to next level
                    next_level = self._get_next_level()
                    if next_level:
                        transition = PhaseTransition(
                            from_level=self.level,
                            to_level=next_level,
                            trigger_stress=stress
                        )
                        self.transitions.append(transition)
                        return transition
        return None

    def _calculate_recent_rate(self) -> float:
        """Calculate recent rate of change in stress."""
        if len(self.stress_history) < 2:
            return 0.0
        
        recent = self.stress_history[-5:]  # Last 5 measurements
        if len(recent) < 2:
            return 0.0
        
        total_change = sum(abs(recent[i][1] - recent[i-1][1]) for i in range(1, len(recent)))
        return total_change / len(recent)

    def _get_next_level(self) -> Optional[BoundaryLevel]:
        """Get the next boundary level for transitions."""
        levels = list(BoundaryLevel)
        try:
            current_idx = levels.index(self.level)
            if current_idx < len(levels) - 1:
                return levels[current_idx + 1]
        except ValueError:
            pass
        return None


@dataclass
class SystemStress:
    """Tracks stress patterns and their effects on system evolution."""
    stress_points: List[TensionPoint] = field(default_factory=list)
    adaptation_history: List[str] = field(default_factory=list)
    emergence_patterns: Dict[str, List[TensionPoint]] = field(default_factory=dict)
    temporal_patterns: Dict[str, ChangeRate] = field(default_factory=lambda: defaultdict(ChangeRate))
    boundary_effects: Dict[BoundaryLevel, BoundaryEffect] = field(
        default_factory=lambda: {level: BoundaryEffect(level=level) for level in BoundaryLevel}
    )

    def record_adaptation(self, description: str, magnitude: float = 1.0) -> None:
        """Record a system adaptation event."""
        timestamp = datetime.now().isoformat()
        self.adaptation_history.append(f"{timestamp}: {description}")
        
        # Update temporal patterns
        self.temporal_patterns["adaptation"].add_change(magnitude)

    def add_tension(self, tension: TensionPoint) -> None:
        """Add a new tension point and analyze its effects."""
        self.stress_points.append(tension)
        
        # Categorize by nature
        if tension.nature not in self.emergence_patterns:
            self.emergence_patterns[tension.nature] = []
        self.emergence_patterns[tension.nature].append(tension)
        
        # Analyze effects on boundary levels
        self._analyze_boundary_effects(tension)
        
        # Look for cascade effects
        self._analyze_cascade_effects(tension)

    def _analyze_boundary_effects(self, tension: TensionPoint) -> None:
        """Analyze how tension affects different boundary levels."""
        # Map tension strength to boundary effects
        for level, effect in self.boundary_effects.items():
            # Stronger tensions affect larger boundaries more
            if level in [BoundaryLevel.COMMUNITY, BoundaryLevel.SOCIETY]:
                boundary_stress = tension.strength * 0.8
            elif level in [BoundaryLevel.TRIBE, BoundaryLevel.IMMEDIATE]:
                boundary_stress = tension.strength * 1.0
            else:
                boundary_stress = tension.strength * 0.6
            
            transition = effect.add_stress(boundary_stress)
            if transition:
                self.record_adaptation(
                    f"Phase transition detected at {level.value} boundary: "
                    f"{transition.from_level.value} -> {transition.to_level.value}",
                    transition.trigger_stress
                )

    def _analyze_cascade_effects(self, tension: TensionPoint) -> None:
        """Analyze potential cascade effects from this tension."""
        # Look for resonance patterns between boundary levels
        boundary_levels = list(self.boundary_effects.values())
        for i, effect1 in enumerate(boundary_levels):
            for effect2 in boundary_levels[i+1:]:
                resonance = effect1.detect_resonance(effect2)
                if resonance and resonance.strength > 0.7:
                    effect1.resonances.append(resonance)
                    effect2.resonances.append(resonance)

    def get_critical_tensions(self) -> List[Tuple[TensionPoint, float]]:
        """Get tensions sorted by criticality (urgency * strength)."""
        tensions_with_criticality = [
            (tension, tension.urgency * tension.strength) 
            for tension in self.stress_points
        ]
        return sorted(tensions_with_criticality, key=lambda x: x[1], reverse=True)

    def get_boundary_analysis(self) -> str:
        """Get a summary of boundary effects and transitions."""
        analysis = ["=== Boundary Analysis ==="]
        
        for level, effect in self.boundary_effects.items():
            analysis.append(f"\n{level.value.upper()} Boundary:")
            analysis.append(f"  Current Size: {effect.current_size}")
            analysis.append(f"  Transitions: {len(effect.transitions)}")
            analysis.append(f"  Quantum States: {len(effect.quantum_states)}")
            analysis.append(f"  Resonances: {len(effect.resonances)}")
            
            if effect.transitions:
                latest = effect.transitions[-1]
                analysis.append(f"  Latest Transition: {latest.from_level.value} -> {latest.to_level.value}")
            
            if effect.resonances:
                strongest = max(effect.resonances, key=lambda r: r.strength)
                analysis.append(f"  Strongest Resonance: {strongest.resonant_level.value} (strength: {strongest.strength:.2f})")
        
        return "\n".join(analysis)


@dataclass
class RelationshipQuality:
    """Qualitative assessment of a relationship between ontology elements."""
    dimensional_scores: Dict[KnowledgeDimension, DimensionalScore] = field(default_factory=dict)
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    system_stress: SystemStress = field(default_factory=SystemStress)

    def __post_init__(self):
        # Initialize scores for all dimensions
        for dim in KnowledgeDimension:
            if dim not in self.dimensional_scores:
                self.dimensional_scores[dim] = DimensionalScore(dimension=dim)

    def get_stakeholder_score(self, stakeholder: Stakeholder) -> float:
        """Calculate overall score from a stakeholder's perspective."""
        if not self.dimensional_scores:
            return 0.0
        
        weights = stakeholder.priority_dimensions
        if not weights:
            return self.get_overall_score()  # Fallback to general score
            
        weighted_sum = 0.0
        total_weight = 0.0
        
        for dim, score in self.dimensional_scores.items():
            weight = weights.get(dim.value, 0.5)  # Default weight
            weighted_sum += score.get_stakeholder_score(stakeholder) * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def get_stress_summary(self) -> str:
        """Get a summary of current system stress and tensions."""
        summary = ["=== System Stress Summary ==="]
        
        if not self.system_stress.stress_points:
            summary.append("No significant stress points detected.")
            return "\n".join(summary)
        
        # Critical tensions
        critical = self.system_stress.get_critical_tensions()[:3]  # Top 3
        if critical:
            summary.append("\nMost Critical Tensions:")
            for tension, criticality in critical:
                summary.append(f"  • {tension.source} ↔ {tension.target}: {tension.nature}")
                summary.append(f"    Strength: {tension.strength:.2f}, Urgency: {tension.urgency:.2f}")
        
        # Boundary effects
        summary.append(f"\nBoundary Effects: {len(self.system_stress.boundary_effects)} levels tracked")
        
        # Recent adaptations
        recent_adaptations = self.system_stress.adaptation_history[-3:]  # Last 3
        if recent_adaptations:
            summary.append("\nRecent Adaptations:")
            for adaptation in recent_adaptations:
                summary.append(f"  • {adaptation}")
        
        # Check for acceleration
        total_accel = sum(pattern.get_rate() for pattern in self.system_stress.temporal_patterns.values())
        
        if total_accel > 0.5:
            summary.append("  ⚠️ Warning: System changes are accelerating rapidly")
            # Check if we're near any boundary thresholds
            near_boundaries = [
                level.value for level, effect in self.system_stress.boundary_effects.items()
                if effect.is_near_threshold()
            ]
            if near_boundaries:
                summary.append(f"  🌊 Phase transition possible at boundaries: {', '.join(near_boundaries)}")
        
        return "\n".join(summary)

    def get_overall_score(self) -> float:
        """Calculate overall score considering system stresses."""
        base_score = sum(s.score for s in self.dimensional_scores.values()) / len(self.dimensional_scores)
        
        # Factor in stress points - some stress is good, too much is bad
        stress_factor = sum(t.strength for t in self.system_stress.stress_points)
        optimal_stress = 0.4  # Some stress is healthy
        
        if stress_factor < optimal_stress:
            # Too little stress might indicate lack of evolution
            return base_score * (0.5 + stress_factor)
        else:
            # Too much stress reduces effectiveness
            return base_score * (1.5 - stress_factor)

    def update_confidence_level(self) -> None:
        """Update confidence level based on scores and stress patterns."""
        score = self.get_overall_score()
        stress_count = len(self.system_stress.stress_points)
        
        if score < 0.1 or stress_count > 10:
            self.confidence = ConfidenceLevel.UNKNOWN
        elif score < 0.3 or stress_count > 7:
            self.confidence = ConfidenceLevel.EMERGING
        elif score < 0.6 or stress_count > 5:
            self.confidence = ConfidenceLevel.ESTABLISHED
        elif score < 0.9 or stress_count > 3:
            self.confidence = ConfidenceLevel.VERIFIED
        else:
            self.confidence = ConfidenceLevel.COMPLETE


@dataclass
class Relationship:
    """Represents a qualified relationship between ontology elements."""
    source: URIRef
    target: URIRef
    rel_type: RelationType
    quality: RelationshipQuality
    properties: Dict[str, Any] = field(default_factory=dict)

    def update_dimension(self, dimension: KnowledgeDimension, score: float, evidence: str) -> None:
        """Update knowledge score for a specific dimension."""
        self.quality.dimensional_scores[dimension].update_score(score, evidence)
        self.quality.update_confidence_level()


class DependencyInfo(TypedDict):
    """Type for dependency information with qualitative metadata."""
    depends_on: Dict[URIRef, Relationship]
    depended_by: Dict[URIRef, Relationship]
    relation_types: Set[RelationType]


class GuidanceOntology(TemplateOntology):
    """Class for managing the guidance ontology."""
    
    def __init__(self, base_uri: str = "https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#", guidance_file: Optional[Union[str, Path]] = None) -> None:
        """Initialize the GuidanceOntology.
        
        Args:
            base_uri: Base URI for the guidance ontology
            guidance_file: Optional path to a guidance file to load
        """
        super().__init__(base_uri)
        self._initialize_uris()
        self.relationship_cache: Dict[Tuple[URIRef, URIRef], Relationship] = {}
        
        if guidance_file:
            self.load(guidance_file)
            self._initialize_uris()
        else:
            self._initialize_guidance_ontology()

    def _infer_relationship_type(self, predicate: URIRef) -> RelationType:
        """Infer the type of relationship from a predicate."""
        if predicate == RDFS.subClassOf:
            return RelationType.SUBCLASS
        elif predicate == RDF.type:
            return RelationType.INSTANCE
        elif predicate == SH.targetClass:
            return RelationType.SHAPE
        elif predicate in [OWL.imports, OWL.equivalentClass, OWL.sameAs]:
            return RelationType.SEMANTIC
        else:
            return RelationType.PROPERTY

    def _analyze_relationship(self, source: URIRef, target: URIRef, predicate: URIRef) -> Relationship:
        """Analyze and qualify a relationship between ontology elements."""
        rel_type = self._infer_relationship_type(predicate)
        
        # Initialize relationship quality
        quality = RelationshipQuality()
        
        # Analyze structural dimension
        if rel_type == RelationType.SUBCLASS:
            quality.dimensional_scores[KnowledgeDimension.STRUCTURAL].update_score(
                0.8, "Direct subclass relationship"
            )
        
        # Analyze semantic dimension
        if predicate in self.graph.predicates():
            quality.dimensional_scores[KnowledgeDimension.SEMANTIC].update_score(
                0.6, "Predicate is defined in the ontology"
            )
        
        # Analyze functional dimension
        if (source, predicate, target) in self.graph:
            quality.dimensional_scores[KnowledgeDimension.FUNCTIONAL].update_score(
                0.7, "Relationship is actively used"
            )
        
        # Update confidence level based on dimensional scores
        quality.update_confidence_level()
        
        return Relationship(
            source=cast(URIRef, source),
            target=cast(URIRef, target),
            rel_type=rel_type,
            quality=quality
        )

    def get_dependencies(self, uri: URIRef) -> DependencyInfo:
        """Get qualified dependencies for a given URI in both directions."""
        depends_on: Dict[URIRef, Relationship] = {}
        depended_by: Dict[URIRef, Relationship] = {}
        relation_types: Set[RelationType] = set()
        
        # Analyze outgoing relationships
        for s, p, o in self.graph.triples((uri, None, None)):
            if isinstance(o, URIRef):
                rel = self._analyze_relationship(cast(URIRef, s), cast(URIRef, o), cast(URIRef, p))
                depends_on[o] = rel
                relation_types.add(rel.rel_type)
        
        # Analyze incoming relationships
        for s, p, o in self.graph.triples((None, None, uri)):
            if isinstance(s, URIRef):
                rel = self._analyze_relationship(cast(URIRef, s), cast(URIRef, uri), cast(URIRef, p))
                depended_by[s] = rel
                relation_types.add(rel.rel_type)
        
        return DependencyInfo(
            depends_on=depends_on,
            depended_by=depended_by,
            relation_types=relation_types
        )

    def analyze_adjacency(self, uri: URIRef, max_depth: int = 1) -> Dict[URIRef, DependencyInfo]:
        """Analyze relationships up to a certain depth from a given URI."""
        results: Dict[URIRef, DependencyInfo] = {}
        visited: Set[URIRef] = {uri}
        to_visit: List[Tuple[URIRef, int]] = [(uri, 0)]  # (uri, current_depth)
        
        while to_visit:
            current_uri, depth = to_visit.pop(0)
            if depth > max_depth:
                continue
                
            # Get dependencies for current URI
            deps = self.get_dependencies(current_uri)
            results[current_uri] = deps
            
            # Add new URIs to visit
            for next_uri in deps["depends_on"].keys() | deps["depended_by"].keys():
                if next_uri not in visited:
                    visited.add(next_uri)
                    to_visit.append((next_uri, depth + 1))
        
        return results

    def _initialize_uris(self) -> None:
        """Initialize core URIs as class attributes."""
        # Core classes
        self.ValidationProcess = self._create_uri("ValidationProcess")
        self.ValidationRule = self._create_uri("ValidationRule")
        self.ValidationRuleShape = self._create_uri("ValidationRuleShape")
        self.ValidationPattern = self._create_uri("ValidationPattern")
        self.IntegrationProcess = self._create_uri("IntegrationProcess")
        self.IntegrationStep = self._create_uri("IntegrationStep")
        self.TestPhase = self._create_uri("TestPhase")
        self.ConformanceLevel = self._create_uri("ConformanceLevel")
        self.ConformanceLevelShape = self._create_uri("ConformanceLevelShape")
        self.TestProtocol = self._create_uri("TestProtocol")
        self.Interpretation = self._create_uri("Interpretation")
        
        # Core properties
        self.hasStringRepresentation = self._create_uri("hasStringRepresentation")
        self.hasValidationRules = self._create_uri("hasValidationRules")
        self.hasMinimumRequirements = self._create_uri("hasMinimumRequirements")
        self.hasComplianceMetrics = self._create_uri("hasComplianceMetrics")
        self.hasTestPhase = self._create_uri("hasTestPhase")
        self.requiresNamespaceValidation = self._create_uri("requiresNamespaceValidation")
        self.requiresPrefixValidation = self._create_uri("requiresPrefixValidation")
        self.stepOrder = self._create_uri("stepOrder")
        self.stepDescription = self._create_uri("stepDescription")
        self.hasTarget = self._create_uri("hasTarget")
        
        # Validation rule subclasses
        self.SyntaxRule = self._create_uri("SyntaxRule")
        self.SemanticRule = self._create_uri("SemanticRule")
        self.ConsistencyRule = self._create_uri("ConsistencyRule")

    def _initialize_guidance_ontology(self) -> None:
        """Initialize the guidance ontology with core classes properties and validation rules."""
        init_graph = Graph()
        base_uri_ref = URIRef(self.base_uri)
        init_graph.bind("", base_uri_ref)
        
        # Add metadata
        init_graph.add((base_uri_ref, RDF.type, OWL.Ontology))
        init_graph.add((base_uri_ref, RDFS.label, RDFLiteral("Guidance Ontology", lang="en")))
        init_graph.add((base_uri_ref, RDFS.comment, RDFLiteral("Ontology for managing guidance and validation rules", lang="en")))
        init_graph.add((base_uri_ref, OWL.versionInfo, RDFLiteral("1.0.0")))

        # Add missing core classes
        integration_process = URIRef(self.base_uri + "IntegrationProcess")
        conformance_level = URIRef(self.base_uri + "ConformanceLevel")
        integration_step = URIRef(self.base_uri + "IntegrationStep")
        model_conformance = URIRef(self.base_uri + "ModelConformance")
        test_phase = URIRef(self.base_uri + "TestPhase")
        test_protocol = URIRef(self.base_uri + "TestProtocol")
        test_coverage = URIRef(self.base_uri + "TestCoverage")

        # Define missing core classes with labels and comments
        for cls, label, comment in [
            (integration_process, "IntegrationProcess", "Process for integrating ontology components"),
            (conformance_level, "ConformanceLevel", "Level of conformance to ontology standards"),
            (integration_step, "IntegrationStep", "Individual step in an integration process"),
            (model_conformance, "ModelConformance", "Conformance level for a specific model"),
            (test_phase, "TestPhase", "Phase of testing in the integration process"),
            (test_protocol, "TestProtocol", "Protocol for testing ontology components"),
            (test_coverage, "TestCoverage", "Coverage metrics for ontology testing")
        ]:
            init_graph.add((cls, RDF.type, OWL.Class))
            init_graph.add((cls, RDFS.label, RDFLiteral(label, lang="en")))
            init_graph.add((cls, RDFS.comment, RDFLiteral(comment, lang="en")))

        # Core validation classes
        validation_rule = URIRef(self.base_uri + "ValidationRule")
        consistency_rule = URIRef(self.base_uri + "ConsistencyRule")
        semantic_rule = URIRef(self.base_uri + "SemanticRule")
        syntax_rule = URIRef(self.base_uri + "SyntaxRule")
        spore_rule = URIRef(self.base_uri + "SPORERule")
        
        # Add validation classes
        for cls in [validation_rule, consistency_rule, semantic_rule, syntax_rule, spore_rule]:
            init_graph.add((cls, RDF.type, OWL.Class))
            
        # Add subclass relationships
        for subcls in [consistency_rule, semantic_rule, syntax_rule, spore_rule]:
            init_graph.add((subcls, RDFS.subClassOf, validation_rule))

        # Add validation properties
        has_validator = URIRef(self.base_uri + "hasValidator")
        has_priority = URIRef(self.base_uri + "hasPriority")
        has_target = URIRef(self.base_uri + "hasTarget")
        has_message = URIRef(self.base_uri + "hasMessage")
        
        # Define property characteristics
        for prop in [has_validator, has_priority, has_target, has_message]:
            init_graph.add((prop, RDF.type, OWL.DatatypeProperty))
            init_graph.add((prop, RDFS.domain, validation_rule))
            
        # Add SHACL shapes
        validation_shape = URIRef(self.base_uri + "ValidationRuleShape")
        init_graph.add((validation_shape, RDF.type, SH.NodeShape))
        init_graph.add((validation_shape, SH.targetClass, validation_rule))
        
        # Required properties for validation rules
        for prop, datatype in [(has_validator, XSD.string), 
                             (has_priority, XSD.string),
                             (has_target, XSD.anyURI),
                             (has_message, XSD.string)]:
            blank = BNode()
            init_graph.add((validation_shape, SH.property, blank))
            init_graph.add((blank, SH.path, prop))
            init_graph.add((blank, SH.minCount, RDFLiteral(1)))
            init_graph.add((blank, SH.maxCount, RDFLiteral(1)))
            init_graph.add((blank, SH.datatype, datatype))

        # Add example validation rules
        consistency_example = URIRef(self.base_uri + "ClassHierarchyCheck")
        init_graph.add((consistency_example, RDF.type, consistency_rule))
        init_graph.add((consistency_example, has_validator, RDFLiteral("ClassHierarchyValidator")))
        init_graph.add((consistency_example, has_message, RDFLiteral("Class hierarchy must be acyclic")))

        # Merge with main graph
        self.graph += init_graph

    def get_relationship_summary(self, uri: URIRef) -> str:
        """Get a human-readable summary of relationships for a URI."""
        deps = self.get_dependencies(uri)
        
        summary = [f"Relationship Summary for {uri}"]
        summary.append("=" * 50)
        
        if deps["depends_on"]:
            summary.append(f"\nDepends on ({len(deps['depends_on'])} relationships):")
            for target, rel in deps["depends_on"].items():
                conf = rel.quality.confidence.name
                score = rel.quality.get_overall_score()
                summary.append(f"  → {target} ({rel.rel_type.value}, confidence: {conf}, score: {score:.2f})")
        
        if deps["depended_by"]:
            summary.append(f"\nDepended on by ({len(deps['depended_by'])} relationships):")
            for source, rel in deps["depended_by"].items():
                conf = rel.quality.confidence.name
                score = rel.quality.get_overall_score()
                summary.append(f"  ← {source} ({rel.rel_type.value}, confidence: {conf}, score: {score:.2f})")
        
        summary.append(f"\nRelation types used: {', '.join(rt.value for rt in deps['relation_types'])}")
        
        return "\n".join(summary)

    def emit(self, output_path: Union[str, Path] = "guidance.ttl") -> None:
        """Emit the guidance ontology to a file."""
        try:
            self.graph.serialize(destination=str(output_path), format="turtle")
            print(f"Guidance ontology written to {output_path}")
        except Exception as e:
            print(f"Error writing guidance ontology: {e}")
            raise 