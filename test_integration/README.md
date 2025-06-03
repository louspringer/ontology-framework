# SPORE Integration Files

This zip contains:
1. guidance.ttl - Updated main ontology with SPORE integration
2. guidance/modules/validation/spores.ttl - New SPORE module

## Integration Steps:
1. Backup existing guidance.ttl
2. Replace guidance.ttl with the updated version
3. Create directory structure: guidance/modules/validation/
4. Add spores.ttl to the validation directory
5. Test with: rapper -i turtle guidance.ttl
6. Validate SHACL constraints if available

## SPORE Message Format:
See the SPORE Integration Message artifact for the complete workflow instructions.
