from enum import Enum

class ConformanceLevel(Enum):
    """Validation conformance levels."""
    STRICT = "strict"  # Apply all validation rules
    BASIC = "basic"    # Apply only essential rules
    NONE = "none"      # Skip validation 