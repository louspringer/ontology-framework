# SPORE Integration Message

**From:** Human Developer  
**To:** Claude/Cursor Agent  
**Channel:** File System + Clipboard  
**Message Type:** workflow_coordination  
**Session ID:** spore_integration_2025_001  

## SPORE Payload (TTL):

```turtle
@prefix spore: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance/modules/validation/spores#> .
@prefix guidance: <https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#> .
@prefix workflow: <http://example.org/workflow#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

workflow:spore_integration_task a workflow:RepositoryIntegrationTask ;
    workflow:priority "HIGH" ;
    workflow:requires_files "guidance.ttl, guidance/modules/validation/spores.ttl" ;
    workflow:target_directory "~/ontology-framework" ;
    workflow:action_sequence "extract_zip, update_files, test_validation, commit_changes" ;
    workflow:validation_required true ;
    workflow:test_command "python -m pytest tests/test_spore_validation.py" ;
    workflow:git_branch "feature/spore-integration" .

workflow:file_locations a workflow:FileLocationSpec ;
    workflow:zip_source "~/Downloads/spore_integration_files.zip" ;
    workflow:target_guidance "guidance.ttl" ;
    workflow:target_spores "guidance/modules/validation/spores.ttl" ;
    workflow:backup_existing true .

workflow:validation_steps a workflow:ValidationSequence ;
    workflow:step_1 "Load updated guidance.ttl into GraphDB" ;
    workflow:step_2 "Validate SHACL constraints" ;
    workflow:step_3 "Run SPORE message validation tests" ;
    workflow:step_4 "Check module import resolution" ;
    workflow:step_5 "Verify backward compatibility" .

workflow:expected_outcomes a workflow:OutcomeSpec ;
    workflow:spore_classes_available true ;
    workflow:validation_rules_active true ;
    workflow:module_registry_updated true ;
    workflow:legacy_support_maintained true ;
    workflow:test_coverage_complete true .
```

## Instructions for Claude/Cursor:

1. **Extract the zip file** from ~/Downloads/spore_integration_files.zip
2. **Create backup** of existing guidance.ttl 
3. **Update guidance.ttl** with the enhanced version (includes SPORE imports and validation)
4. **Add new file** guidance/modules/validation/spores.ttl
5. **Test integration** by loading into GraphDB or running validation
6. **Commit changes** to git with message: "feat: Add SPORE inter-LLM communication module"

## Validation Commands:

```bash
# Test TTL syntax
rapper -i turtle guidance.ttl
rapper -i turtle guidance/modules/validation/spores.ttl

# Test in GraphDB (if available)
curl -X POST http://localhost:7200/repositories/guidance/statements \
  -H "Content-Type: application/x-turtle" \
  --data-binary @guidance.ttl

# Run SHACL validation (if pyshacl available)
pyshacl -s guidance.ttl -d guidance.ttl -f turtle
```

## Success Criteria:

- [ ] Both TTL files parse without syntax errors
- [ ] All imports resolve correctly  
- [ ] SPORE classes are available for instantiation
- [ ] Validation rules execute successfully
- [ ] Module registry includes spores module
- [ ] Backward compatibility maintained for existing SPORERule references

## Next Steps After Integration:

1. Create example SPORE messages for testing
2. Implement browser extension for SPORE communication
3. Add clipboard bridge functionality
4. Test multi-LLM workflow coordination

**End SPORE Message**