"""Module for managing the guidance ontology."""

from typing import List, Dict, Any, Optional, Union, cast, Sequence, TypedDict, TypeGuard, Tuple, Iterator, Set, TypeVar, NamedTuple
from dataclasses import dataclass, field
from enum import Enum, auto
from rdflib import Graph, URIRef, Literal as RDFLiteral, BNode, Namespace, XSD, Node
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH
from rdflib.query import ResultRow, Result
from pathlib import Path
import math
from datetime import datetime, timedelta
from collections import defaultdict
from ontology_framework.modules.ontology import Ontology
from ontology_framework.modules.constants import CONFORMANCE_LEVELS
from ontology_framework.modules.template_ontology import TemplateOntology

class Stakeholder(Enum):
    """Different stakeholder perspectives for relationship evaluation."""
    FINANCE = "finance"           # Financial/cost implications
    OPERATIONS = "operations"     # Operational efficiency/maintainability
    PRODUCT = "product"          # Product functionality/features
    SECURITY = "security"        # Security/risk management
    COMPLIANCE = "compliance"    # Regulatory/policy compliance
    ENGINEERING = "engineering"  # Technical implementation
    BUSINESS = "business"        # Business value/strategy
    USER = "user"               # End-user experience
    
    @property
    def priority_dimensions(self) -> Dict[str, float]:
        """Get priority weights for different knowledge dimensions per stakeholder."""
        return {
            Stakeholder.FINANCE: {
                "structural": 0.3,
                "semantic": 0.4,
                "functional": 0.6,
                "temporal": 0.8,    # Historical stability is key for financial planning
                "social": 0.3,
                "security": 0.7,    # Financial risk management
                "compliance": 0.9    # Regulatory compliance is critical
            },
            Stakeholder.OPERATIONS: {
                "structural": 0.8,   # System structure is crucial
                "semantic": 0.6,
                "functional": 0.9,   # How things work is key
                "temporal": 0.7,
                "social": 0.4,
                "security": 0.6,
                "compliance": 0.5
            },
            Stakeholder.PRODUCT: {
                "structural": 0.5,
                "semantic": 0.8,     # Meaning and intent are crucial
                "functional": 0.9,   # Features and capabilities
                "temporal": 0.4,
                "social": 0.7,       # User community feedback
                "security": 0.6,
                "compliance": 0.5
            },
            Stakeholder.SECURITY: {
                "structural": 0.7,
                "semantic": 0.6,
                "functional": 0.5,
                "temporal": 0.4,
                "social": 0.3,
                "security": 1.0,     # Security is paramount
                "compliance": 0.8
            },
            # Add other stakeholder priorities...
        }.get(self, {})

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
    """Stakeholder-specific view of a relationship."""
    stakeholder: Stakeholder
    satisfaction_score: float = 0.0  # 0.0 to 1.0
    concerns: List[str] = field(default_factory=list)
    requirements_met: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

    def update_satisfaction(self, score: float, requirement: str, is_met: bool) -> None:
        """Update stakeholder satisfaction with new information."""
        self.satisfaction_score = min(1.0, max(0.0, (self.satisfaction_score + score) / 2))
        if is_met:
            self.requirements_met.append(requirement)
        else:
            self.concerns.append(requirement)
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
        """Update score with new evidence and stakeholder perspective."""
        self.score = min(1.0, max(0.0, (self.score + new_score) / 2))
        self.evidence.append(f"{datetime.now()}: {evidence}")
        self.last_updated = datetime.now()
        self.confidence = min(1.0, len(self.evidence) * 0.1)
        
        if stakeholder:
            if stakeholder not in self.stakeholder_views:
                self.stakeholder_views[stakeholder] = StakeholderView(stakeholder)
            view = self.stakeholder_views[stakeholder]
            view.update_satisfaction(
                new_score,
                evidence,
                new_score >= 0.7  # Consider requirement met if score is high enough
            )

    def get_stakeholder_satisfaction(self, stakeholder: Stakeholder) -> float:
        """Get satisfaction score for a specific stakeholder."""
        if stakeholder in self.stakeholder_views:
            return self.stakeholder_views[stakeholder].satisfaction_score
        return 0.0

@dataclass
class ChangeRate:
    """Tracks the rate and acceleration of changes in a system component."""
    window_size: timedelta = field(default_factory=lambda: timedelta(days=30))
    changes: List[Tuple[datetime, float]] = field(default_factory=list)
    
    def add_change(self, magnitude: float) -> None:
        """Record a new change event with its magnitude."""
        self.changes.append((datetime.now(), magnitude))
        # Prune old changes outside the window
        cutoff = datetime.now() - self.window_size
        self.changes = [c for c in self.changes if c[0] > cutoff]
    
    def get_rate(self) -> float:
        """Calculate current rate of change (changes per day)."""
        if not self.changes:
            return 0.0
        
        window = (self.changes[-1][0] - self.changes[0][0]).total_seconds() / 86400  # days
        if window <= 0:
            return 0.0
        
        return len(self.changes) / window
    
    def get_acceleration(self) -> float:
        """Calculate change acceleration (rate of rate change)."""
        if len(self.changes) < 3:
            return 0.0
            
        # Calculate rates in two half-windows
        mid_idx = len(self.changes) // 2
        first_half = self.changes[:mid_idx]
        second_half = self.changes[mid_idx:]
        
        if not first_half or not second_half:
            return 0.0
            
        first_window = (first_half[-1][0] - first_half[0][0]).total_seconds() / 86400
        second_window = (second_half[-1][0] - second_half[0][0]).total_seconds() / 86400
        
        if first_window <= 0 or second_window <= 0:
            return 0.0
            
        first_rate = len(first_half) / first_window
        second_rate = len(second_half) / second_window
        
        return (second_rate - first_rate) / ((second_half[-1][0] - first_half[0][0]).total_seconds() / 86400)

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
        """Add a new observation and record its impact on change rate."""
        self.observations.append(f"{datetime.now()}: {observation}")
        self.change_rate.add_change(change_magnitude)
    
    @property
    def urgency(self) -> float:
        """Calculate urgency based on strength and rate of change."""
        rate = self.change_rate.get_rate()
        acceleration = self.change_rate.get_acceleration()
        
        # Urgency increases with:
        # 1. Higher tension strength
        # 2. Faster rate of change
        # 3. Positive acceleration (changes speeding up)
        base_urgency = self.strength * (1 + rate)
        if acceleration > 0:
            base_urgency *= (1 + acceleration)
        
        return min(1.0, base_urgency)

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
            BoundaryLevel.SOCIETY: (1000, 2147483647)  # Using max int instead of float('inf')
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
class PhaseTransition:
    """Represents a phase transition at a quantum boundary."""
    boundary: BoundaryLevel
    from_state: str
    to_state: str
    trigger_rate: float  # Rate of change that triggered transition
    transition_time: datetime = field(default_factory=datetime.now)
    cascade_effects: List[str] = field(default_factory=list)

@dataclass
class BoundaryResonance:
    """Tracks resonance patterns between different boundary levels."""
    primary_level: BoundaryLevel
    resonant_level: BoundaryLevel
    strength: float = 0.0  # Resonance strength
    phase_alignment: float = 0.0  # 0 to 2π
    observations: List[str] = field(default_factory=list)

@dataclass
class QuantumState:
    """Represents a discrete organizational state at a boundary."""
    level: BoundaryLevel
    state_vector: Dict[str, float]  # Key characteristics and their magnitudes
    stability_score: float = 0.0
    lifetime: timedelta = field(default_factory=lambda: timedelta())
    transitions_to: List[Tuple[str, float]] = field(default_factory=list)  # (state_id, probability)

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
        mean1, mean2 = sum(pattern1)/len(pattern1), sum(pattern2)/len(pattern2)
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
            if recent_rate > 0.7:  # High rate of change near boundary
                transition = PhaseTransition(
                    boundary=self.level,
                    from_state=f"size_{self.current_size}",
                    to_state=f"size_{self.current_size + 1}",
                    trigger_rate=recent_rate
                )
                self.transitions.append(transition)
                return transition
        return None

    def _calculate_recent_rate(self) -> float:
        """Calculate recent rate of change in stress."""
        if len(self.stress_history) < 2:
            return 0.0
        
        times, stresses = zip(*self.stress_history[-10:])  # Last 10 measurements
        time_delta = (times[-1] - times[0]).total_seconds() / 86400  # days
        if time_delta <= 0:
            return 0.0
            
        stress_delta = sum(abs(s2 - s1) for s1, s2 in zip(stresses[:-1], stresses[1:]))
        return stress_delta / time_delta

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
        """Record how the system adapted to stress."""
        self.adaptation_history.append(f"{datetime.now()}: {description}")
        
        # Update temporal patterns for the adaptation type
        pattern_type = description.split(":")[0] if ":" in description else "general"
        self.temporal_patterns[pattern_type].add_change(magnitude)
    
    def add_tension(self, tension: TensionPoint) -> None:
        """Add a new tension point and analyze emergence patterns."""
        self.stress_points.append(tension)
        
        if tension.nature not in self.emergence_patterns:
            self.emergence_patterns[tension.nature] = []
        self.emergence_patterns[tension.nature].append(tension)
        
        # Track temporal pattern for this type of tension
        self.temporal_patterns[tension.nature].add_change(tension.strength)
        
        # Check for boundary effects
        self._analyze_boundary_effects(tension)
        self._analyze_cascade_effects(tension)
    
    def _analyze_boundary_effects(self, tension: TensionPoint) -> None:
        """Analyze how tension affects different organizational boundaries."""
        # Count related tensions to determine affected boundary level
        related = len([t for t in self.stress_points 
                      if t.source == tension.source or t.target == tension.target])
        
        # Find most relevant boundary level
        for level in BoundaryLevel:
            min_size, max_size = level.threshold_range
            if min_size <= related <= max_size:
                effect = self.boundary_effects[level]
                effect.current_size = related
                
                # Check for phase transition
                transition = effect.add_stress(tension.strength)
                if transition:
                    transition.cascade_effects.append(
                        f"Tension {tension.source} ↔ {tension.target} triggered boundary transition"
                    )
                    self.record_adaptation(
                        f"Phase Transition: {level.value} boundary reorganization triggered by "
                        f"accelerating changes (rate: {transition.trigger_rate:.2f})",
                        magnitude=tension.strength
                    )

    def _analyze_cascade_effects(self, tension: TensionPoint) -> None:
        """Analyze how new tension might affect existing stress points."""
        related_tensions = [
            t for t in self.stress_points 
            if t.source == tension.target or t.target == tension.source
        ]
        
        if related_tensions:
            cascade_magnitude = sum(t.strength for t in related_tensions) / len(related_tensions)
            observation = f"Cascade effect: Connected to {len(related_tensions)} other tension points"
            tension.add_observation(observation, cascade_magnitude)
    
    def get_critical_tensions(self) -> List[Tuple[TensionPoint, float]]:
        """Identify tensions requiring urgent attention based on dynamics."""
        critical = []
        for tension in self.stress_points:
            urgency = tension.urgency
            if urgency > 0.7:  # High urgency threshold
                critical.append((tension, urgency))
        
        return sorted(critical, key=lambda x: x[1], reverse=True)

    def get_boundary_analysis(self) -> str:
        """Analyze stress patterns at different organizational boundaries."""
        summary = ["\nBoundary Analysis:"]
        
        for level, effect in self.boundary_effects.items():
            if effect.stress_history:  # Only show active boundaries
                summary.append(f"\n{level.value.title()} Boundary:")
                summary.append(f"  Current Size: {effect.current_size}")
                summary.append(f"  Recent Rate: {effect._calculate_recent_rate():.2f}")
                
                if effect.is_near_threshold():
                    summary.append("  ⚠️ Near threshold - potential phase transition")
                
                if effect.transitions:
                    summary.append("  Recent Transitions:")
                    for t in effect.transitions[-3:]:  # Show last 3 transitions
                        summary.append(f"    • {t.from_state} → {t.to_state}")
                        summary.append(f"      Triggered by rate: {t.trigger_rate:.2f}")
                        for cascade in t.cascade_effects:
                            summary.append(f"      ↪ {cascade}")
        
        return "\n".join(summary)

@dataclass
class RelationshipQuality:
    """Qualitative and quantitative information about a relationship."""
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    dimensional_scores: Dict[KnowledgeDimension, DimensionalScore] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    validation_history: List[Tuple[float, str]] = field(default_factory=list)
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
            weight = weights.get(dim.value, 0.5)  # Default weight if not specified
            satisfaction = score.get_stakeholder_satisfaction(stakeholder)
            weighted_sum += satisfaction * weight
            total_weight += weight
            
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def get_stakeholder_summary(self, stakeholder: Stakeholder) -> str:
        """Get a summary of relationship quality from a stakeholder's perspective."""
        score = self.get_stakeholder_score(stakeholder)
        summary = [f"\n{stakeholder.value.title()} Perspective (Overall: {score:.2f}):"]
        
        for dim, dim_score in self.dimensional_scores.items():
            view = dim_score.stakeholder_views.get(stakeholder)
            if view:
                summary.append(f"  {dim.value}:")
                summary.append(f"    Satisfaction: {view.satisfaction_score:.2f}")
                if view.requirements_met:
                    summary.append(f"    ✓ Met: {', '.join(view.requirements_met)}")
                if view.concerns:
                    summary.append(f"    ⚠ Concerns: {', '.join(view.concerns)}")
                
        return "\n".join(summary)

    def record_tension(self, source: str, target: str, nature: str, strength: float, observation: str) -> None:
        """Record a new tension point in the relationship."""
        tension = TensionPoint(source=source, target=target, nature=nature, strength=strength)
        tension.add_observation(observation)
        self.system_stress.add_tension(tension)
    
    def get_stress_patterns(self) -> str:
        """Analyze and summarize stress patterns in the relationship."""
        if not self.system_stress.stress_points:
            return "No stress patterns observed"
            
        summary = ["Stress Pattern Analysis:"]
        
        # Get critical tensions first
        critical_tensions = self.system_stress.get_critical_tensions()
        if critical_tensions:
            summary.append("\n🚨 Critical Tensions (Requiring Urgent Attention):")
            for tension, urgency in critical_tensions:
                summary.append(f"  • {tension.source} ↔ {tension.target}")
                summary.append(f"    Urgency: {urgency:.2f}")
                summary.append(f"    Rate of Change: {tension.change_rate.get_rate():.2f} changes/day")
                summary.append(f"    Acceleration: {tension.change_rate.get_acceleration():.2f}")
        
        # Add boundary analysis
        summary.append(self.system_stress.get_boundary_analysis())
        
        # Analyze emergence patterns with temporal dynamics
        for nature, tensions in self.system_stress.emergence_patterns.items():
            pattern_rate = self.system_stress.temporal_patterns[nature]
            summary.append(f"\n{nature} Tensions:")
            summary.append(f"  Rate of Change: {pattern_rate.get_rate():.2f} changes/day")
            summary.append(f"  Acceleration: {pattern_rate.get_acceleration():.2f}")
            
            for tension in tensions:
                summary.append(f"  • {tension.source} ↔ {tension.target}")
                summary.append(f"    Strength: {tension.strength:.2f}")
                summary.append(f"    Urgency: {tension.urgency:.2f}")
                if tension.change_rate.get_rate() > 0:
                    summary.append(f"    Changes: {tension.change_rate.get_rate():.2f}/day")
        
        # System-wide dynamics
        total_rate = sum(p.get_rate() for p in self.system_stress.temporal_patterns.values())
        total_accel = sum(p.get_acceleration() for p in self.system_stress.temporal_patterns.values())
        
        summary.append("\nSystem-wide Dynamics:")
        summary.append(f"  Total Change Rate: {total_rate:.2f} changes/day")
        summary.append(f"  Overall Acceleration: {total_accel:.2f}")
        
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
            for next_uri in deps.depends_on.keys() | deps.depended_by.keys():
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
        """Initialize the guidance ontology with core classes, properties, and validation rules."""
        init_graph = Graph()
        base_uri_ref = URIRef(self.base_uri)
        init_graph.bind("", base_uri_ref)
        
        # Add metadata
        init_graph.add((base_uri_ref, RDF.type, OWL.Ontology))
        init_graph.add((base_uri_ref, RDFS.label, RDFLiteral("Guidance Ontology", lang="en")))
        init_graph.add((base_uri_ref, RDFS.comment, RDFLiteral("Ontology for managing guidance and validation rules", lang="en")))
        init_graph.add((base_uri_ref, OWL.versionInfo, RDFLiteral("1.0.0")))

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
        init_graph.add((consistency_example, has_validator, RDFLiteral("validate_consistency")))
        init_graph.add((consistency_example, has_priority, RDFLiteral("HIGH")))
        init_graph.add((consistency_example, has_target, URIRef(self.base_uri + "ClassHierarchy")))
        init_graph.add((consistency_example, has_message, RDFLiteral("Check for cycles in class hierarchy")))

        # Merge graphs with preservation of existing triples
        existing_triples: Dict[URIRef, List[Tuple[URIRef, Any]]] = {}
        for s, p, o in self.graph:
            if isinstance(s, URIRef) and isinstance(p, URIRef):
                if s not in existing_triples:
                    existing_triples[s] = []
                existing_triples[s].append((p, o))
            
        # First add all new triples
        for s, p, o in init_graph:
            self.graph.add((s, p, o))
            
        # Then selectively add existing triples that don't conflict
        for s, po_pairs in existing_triples.items():
            if not list(init_graph.triples((s, None, None))):
                for p, o in po_pairs:
                    if not list(init_graph.triples((s, p, None))):
                        self.graph.add((s, p, o))

    def get_relationship_summary(self, uri: URIRef) -> str:
        """Get a summary of relationship quality including stress patterns."""
        deps = self.get_dependencies(uri)
        
        summary = [f"\nRelationship Analysis for {uri}:"]
        
        for target, rel in deps['depends_on'].items():
            summary.append(f"\n→ {target} ({rel.rel_type.value}):")
            summary.append(f"  Score: {rel.quality.get_overall_score():.2f}")
            summary.append(f"  Confidence: {rel.quality.confidence.name}")
            
            # Add stress pattern analysis
            stress_patterns = rel.quality.get_stress_patterns()
            if stress_patterns != "No stress patterns observed":
                summary.append("\n  " + "\n  ".join(stress_patterns.split("\n")))
        
        return "\n".join(summary)

    def emit(self, output_path: Union[str, Path] = "guidance.ttl") -> None:
        """Emit the guidance ontology to a Turtle file."""
        self.save(output_path)

if __name__ == "__main__":
    # Generate guidance.ttl in the project root
    project_root = Path(__file__).parent.parent.parent
    output_path = project_root / "guidance.ttl"
    guidance = GuidanceOntology()
    
    # Analyze relationships with stress patterns
    validation_rule = guidance._create_uri("ValidationRule")
    print(guidance.get_relationship_summary(validation_rule))
    
    guidance.emit(output_path) 