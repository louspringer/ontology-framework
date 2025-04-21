from typing import Final
from rdflib import Namespace

# Core namespaces
META: Final[Namespace] = Namespace("http://example.org/guidance#")
SEMANTIC_SPORE: Final[str] = "http://example.org/guidance#SemanticSpore"
VALIDATION_RULE: Final[str] = "http://example.org/guidance#ValidationRule"
CONCEPT_PATCH: Final[str] = "http://example.org/guidance#ConceptPatch"
TRANSFORMATION_PATTERN: Final[str] = "http://example.org/guidance#TransformationPattern"

# Properties
DISTRIBUTES_PATCH: Final[str] = "http://example.org/guidance#distributesPatch"
TARGET_MODEL: Final[str] = "http://example.org/guidance#targetModel"
HAS_INTEGRATION_STEP: Final[str] = "http://example.org/guidance#hasIntegrationStep"
STEP_ORDER: Final[str] = "http://example.org/guidance#stepOrder"
STEP_TYPE: Final[str] = "http://example.org/guidance#stepType"
STEP_TARGET: Final[str] = "http://example.org/guidance#stepTarget"

# Step types
VALIDATION_STEP: Final[str] = "http://example.org/guidance#ValidationStep"
TRANSFORMATION_STEP: Final[str] = "http://example.org/guidance#TransformationStep" 