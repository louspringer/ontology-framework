from typing import Dict, Any, Optional, List, cast, Tuple
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal, Node
from rdflib.namespace import RDF, RDFS, DC, SH
from rdflib.query import ResultRow
import json
from datetime import datetime
import semver
import re
from typing import NamedTuple
from enum import Enum

# Define validation patterns namespace
VP = Namespace('http://example.org/validation-patterns#')

class PatternType(Enum):
    """Type of validation pattern"""
    REGEX = "regex"
    SHACL = "shacl"

class PatternValidationError(NamedTuple):
    """Represents a pattern validation error"""
    is_valid: bool
    error_message: Optional[str]
    suggested_shacl: Optional[str] = None

class PatternManager:
    # SHACL patterns take precedence over regex where possible
    DEFAULT_PATTERNS = {
        "email": {
            "type": PatternType.SHACL,
            "pattern": """
                sh:property [
                    sh:path ex:email ;
                    sh:nodeKind sh:Literal ;
                    sh:pattern "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$" ;
                    sh:maxCount 1 ;
                ]
            """,
            "category": "common",
            "label": "Email Pattern",
            "comment": "Validates email addresses using SHACL constraints"
        },
        "url": {
            "type": PatternType.SHACL,
            "pattern": """
                sh:property [
                    sh:path ex:url ;
                    sh:nodeKind sh:IRI ;
                    sh:minCount 1 ;
                ]
            """,
            "category": "common",
            "label": "URL Pattern",
            "comment": "Validates URLs using SHACL IRI constraint"
        },
        "required_string": {
            "type": PatternType.SHACL,
            "pattern": """
                sh:property [
                    sh:path ex:value ;
                    sh:datatype xsd:string ;
                    sh:minCount 1 ;
                    sh:maxCount 1 ;
                ]
            """,
            "category": "common",
            "label": "Required String",
            "comment": "Validates required string fields using SHACL"
        }
    }

    REGEX_COMPLEXITY_THRESHOLD = 50  # Threshold for suggesting SHACL alternative

    def __init__(self, patterns_file: Optional[str] = None):
        """Initialize the pattern manager.
        
        Args:
            patterns_file: Optional path to patterns.ttl file. If not provided,
                         will look in default location.
        """
        self.patterns_file = patterns_file or str(
            Path(__file__).parent / "patterns.ttl"
        )
        self.graph = Graph()
        self._pattern_cache: Dict[str, Dict[str, Any]] = {}
        self._last_load: Optional[datetime] = None
        self._ensure_patterns_file()
        self.load_patterns()

    def _ensure_patterns_file(self) -> None:
        """Ensure patterns file exists with default patterns."""
        if not Path(self.patterns_file).exists():
            self.graph = Graph()
            # Add default patterns
            for pattern_id, details in self.DEFAULT_PATTERNS.items():
                self.add_pattern(
                    pattern_id=pattern_id,
                    pattern=details["pattern"],
                    category=details["category"],
                    pattern_type=details["type"],
                    label=details["label"],
                    comment=details["comment"]
                )
            self.save_patterns()

    def load_patterns(self) -> None:
        """Load patterns from the TTL file into the graph."""
        try:
            self.graph = Graph()
            self.graph.parse(self.patterns_file, format="turtle")
            self._last_load = datetime.now()
            self._update_cache()
        except Exception as e:
            raise ValueError(f"Failed to load patterns from {self.patterns_file}: {e}")

    def _update_cache(self) -> None:
        """Update the pattern cache from the graph."""
        self._pattern_cache.clear()
        
        # Query for all patterns
        query = """
            SELECT ?pattern ?id ?value ?category ?version ?label ?comment
            WHERE {
                ?pattern a vp:ValidationPattern ;
                        vp:pattern ?value ;
                        vp:category ?category ;
                        vp:version ?version .
                BIND(STRAFTER(STR(?pattern), "#") AS ?id)
                OPTIONAL { ?pattern rdfs:label ?label }
                OPTIONAL { ?pattern rdfs:comment ?comment }
            }
        """
        
        results = self.graph.query(query, initNs={"vp": VP, "rdfs": RDFS})
        for row in results:
            if isinstance(row, ResultRow):
                pattern_id = str(row['id']) if 'id' in row.labels else ''
                self._pattern_cache[pattern_id] = {
                    "pattern": str(row['value']) if 'value' in row.labels else '',
                    "category": str(row['category']) if 'category' in row.labels else '',
                    "version": str(row['version']) if 'version' in row.labels else '',
                    "label": str(row['label']) if ('label' in row.labels and row['label']) else None,
                    "comment": str(row['comment']) if ('comment' in row.labels and row['comment']) else None
                }
            else:
                # Handle tuple results
                row_tuple = cast(Tuple[Node, ...], row)
                if len(row_tuple) >= 7:  # Ensure we have all required fields
                    pattern_id = str(row_tuple[1])  # id is second field
                    self._pattern_cache[pattern_id] = {
                        "pattern": str(row_tuple[2]),  # value
                        "category": str(row_tuple[3]),  # category
                        "version": str(row_tuple[4]),  # version
                        "label": str(row_tuple[5]) if row_tuple[5] else None,  # label
                        "comment": str(row_tuple[6]) if row_tuple[6] else None  # comment
                    }

    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get a pattern by its ID.
        
        Args:
            pattern_id: ID of the pattern to retrieve
            
        Returns:
            Pattern dictionary if found, None otherwise
        """
        return self._pattern_cache.get(pattern_id)

    def get_patterns_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all patterns in a specific category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of pattern dictionaries
        """
        category_uri = VP[category]
        return [
            {"id": pid, **p} 
            for pid, p in self._pattern_cache.items()
            if URIRef(VP[p["category"]]) == category_uri
        ]

    def _calculate_regex_complexity(self, pattern: str) -> int:
        """Calculate complexity score of a regex pattern.
        
        Args:
            pattern: Regex pattern string
            
        Returns:
            Complexity score (higher means more complex)
        """
        complexity = 0
        # Special characters that indicate complexity
        complex_features = [
            '+', '*', '?', '{', '}', '|', '(', ')',
            '[', ']', '\\d', '\\w', '\\s', '(?=', '(?!'
        ]
        
        for feature in complex_features:
            complexity += pattern.count(feature) * 10
            
        # Length also contributes to complexity
        complexity += len(pattern)
        
        return complexity

    def _suggest_shacl_alternative(self, pattern: str) -> Optional[str]:
        """Suggest SHACL alternative for complex regex patterns.
        
        Args:
            pattern: Regex pattern string
            
        Returns:
            SHACL pattern suggestion if applicable, None otherwise
        """
        # Common regex patterns that can be replaced with SHACL
        shacl_alternatives = {
            r"^\d+$": """
                sh:property [
                    sh:path ex:value ;
                    sh:datatype xsd:integer ;
                ]
            """,
            r"^[A-Za-z]+$": """
                sh:property [
                    sh:path ex:value ;
                    sh:datatype xsd:string ;
                    sh:pattern "^[A-Za-z]+$" ;
                ]
            """,
            r"^https?://": """
                sh:property [
                    sh:path ex:value ;
                    sh:nodeKind sh:IRI ;
                ]
            """
        }
        
        for regex_pattern, shacl_pattern in shacl_alternatives.items():
            if re.search(regex_pattern, pattern):
                return shacl_pattern
        return None

    def validate_pattern(self, pattern: str, pattern_type: PatternType = PatternType.REGEX) -> PatternValidationError:
        """Validate a pattern string.
        
        Args:
            pattern: Pattern string to validate
            pattern_type: Type of pattern (regex or SHACL)
            
        Returns:
            PatternValidationError with validation result and error message if invalid
        """
        if pattern_type == PatternType.REGEX:
            try:
                re.compile(pattern)
                complexity = self._calculate_regex_complexity(pattern)
                
                if complexity > self.REGEX_COMPLEXITY_THRESHOLD:
                    shacl_suggestion = self._suggest_shacl_alternative(pattern)
                    if shacl_suggestion:
                        return PatternValidationError(
                            is_valid=True,
                            error_message="Complex regex detected - consider using SHACL pattern",
                            suggested_shacl=shacl_suggestion
                        )
                return PatternValidationError(True, None, None)
            except re.error as e:
                return PatternValidationError(False, str(e), None)
        else:  # SHACL pattern
            try:
                # Create a temporary graph to validate SHACL syntax
                g = Graph()
                g.parse(data=f"""
                    @prefix sh: <http://www.w3.org/ns/shacl#> .
                    @prefix ex: <http://example.org/> .
                    
                    ex:TestShape a sh:NodeShape ;
                        {pattern} .
                """, format="turtle")
                return PatternValidationError(True, None, None)
            except Exception as e:
                return PatternValidationError(False, f"Invalid SHACL pattern: {str(e)}", None)

    def add_pattern(
        self,
        pattern_id: str,
        pattern: str,
        category: str,
        pattern_type: PatternType = PatternType.REGEX,
        version: str = "1.0.0",
        label: Optional[str] = None,
        comment: Optional[str] = None
    ) -> None:
        """Add a new pattern to the ontology.
        
        Args:
            pattern_id: Unique identifier for the pattern
            pattern: The pattern string
            category: Pattern category
            pattern_type: Type of pattern (regex or SHACL)
            version: Pattern version (semver format)
            label: Optional label for the pattern
            comment: Optional description of the pattern
        """
        # Validate pattern
        validation_result = self.validate_pattern(pattern, pattern_type)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid pattern: {validation_result.error_message}")
        elif validation_result.suggested_shacl:
            # Log suggestion but continue with addition
            print(f"Warning: Complex regex detected for pattern '{pattern_id}'. "
                  f"Consider using this SHACL alternative:\n{validation_result.suggested_shacl}")

        # Create pattern in graph
        pattern_uri = VP[pattern_id]
        self.graph.add((pattern_uri, RDF.type, VP.ValidationPattern))
        self.graph.add((pattern_uri, VP.pattern, Literal(pattern)))
        self.graph.add((pattern_uri, VP.patternType, Literal(pattern_type.value)))
        self.graph.add((pattern_uri, VP.category, VP[category]))
        self.graph.add((pattern_uri, VP.version, Literal(version)))
        self.graph.add((pattern_uri, DC.date, Literal(datetime.now().isoformat())))
        
        if label:
            self.graph.add((pattern_uri, RDFS.label, Literal(label, lang="en")))
        if comment:
            self.graph.add((pattern_uri, RDFS.comment, Literal(comment, lang="en")))

        # Save changes
        self.save_patterns()
        self._update_cache()

    def update_pattern(
        self,
        pattern_id: str,
        pattern: Optional[str] = None,
        category: Optional[str] = None,
        version: Optional[str] = None,
        label: Optional[str] = None,
        comment: Optional[str] = None
    ) -> None:
        """Update an existing pattern.
        
        Args:
            pattern_id: ID of pattern to update
            pattern: New pattern string (optional)
            category: New category (optional)
            version: New version (optional)
            label: New label (optional)
            comment: New comment (optional)
        """
        pattern_uri = VP[pattern_id]
        
        # Check if pattern exists
        if (pattern_uri, RDF.type, VP.ValidationPattern) not in self.graph:
            raise ValueError(f"Pattern {pattern_id} not found")

        # Validate and update version if provided
        if version:
            try:
                new_version = semver.VersionInfo.parse(version)
                old_version = semver.VersionInfo.parse(
                    str(self.graph.value(pattern_uri, VP.version))
                )
                if new_version <= old_version:
                    raise ValueError(
                        f"New version {version} must be greater than {old_version}"
                    )
            except ValueError as e:
                raise ValueError(f"Invalid version format: {e}")
            self.graph.set((pattern_uri, VP.version, Literal(version)))

        # Update other properties if provided
        if pattern:
            self.graph.set((pattern_uri, VP.pattern, Literal(pattern)))
        if category:
            self.graph.set((pattern_uri, VP.category, VP[category]))
        if label:
            self.graph.set(
                (pattern_uri, RDFS.label, Literal(label, lang="en"))
            )
        if comment:
            self.graph.set(
                (pattern_uri, RDFS.comment, Literal(comment, lang="en"))
            )

        # Save changes
        self.save_patterns()
        self._update_cache()

    def save_patterns(self) -> None:
        """Save patterns back to the TTL file."""
        self.graph.serialize(destination=self.patterns_file, format="turtle")

    def get_pattern_history(self, pattern_id: str) -> List[Dict[str, str]]:
        """Get version history of a pattern.
        
        Args:
            pattern_id: ID of the pattern
            
        Returns:
            List of version dictionaries with date and version
        """
        pattern_uri = VP[pattern_id]
        history = []
        
        # Query for all versions of this pattern
        query = """
            SELECT ?version ?date
            WHERE {
                ?pattern vp:version ?version ;
                        dc:date ?date .
            }
            ORDER BY DESC(?date)
        """
        
        results = self.graph.query(query, initBindings={"pattern": pattern_uri})
        for row in results:
            if isinstance(row, ResultRow):
                history.append({
                    "version": str(row['version']) if 'version' in row.labels else '',
                    "date": str(row['date']) if 'date' in row.labels else ''
                })
            else:
                # Handle tuple results
                row_tuple = cast(Tuple[Node, ...], row)
                if len(row_tuple) >= 2:
                    history.append({
                        "version": str(row_tuple[0]),
                        "date": str(row_tuple[1])
                    })
            
        return history 