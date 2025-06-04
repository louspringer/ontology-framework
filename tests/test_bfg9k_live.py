"""
Live BFG9K testing implementation.
"""
import json
import pytest
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from rdflib import Graph, URIRef
from ontology_framework.modules.validator import MCPValidator, ValidationTarget
from ontology_framework.mcp.maintenance_config import MaintenanceConfig
from ontology_framework.mcp.maintenance_prompts import MaintenancePrompts
from ontology_framework.mcp.maintenance_server import MaintenanceServer

# Configure detailed logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_detailed_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LiveBFG9KTest:
    """Live, fire testing with real BFG9K ordinance"""
    
    def __init__(self, config_path: Path):
        """Initialize the live test with configuration"""
        logger.info("=== INITIALIZING LiveBFG9KTest ===")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Requested config_path: {config_path}")
        logger.info(f"Config path absolute: {config_path.absolute()}")
        logger.info(f"Config path exists: {config_path.exists()}")
        
        if config_path.exists():
            logger.info(f"Config file size: {config_path.stat().st_size} bytes")
            with open(config_path) as f:
                raw_config = f.read()
                # First 500 chars
                logger.debug(f"Raw config content: {raw_config[:500]}...")
                f.seek(0)  # Reset file pointer
                try:
                    full_config = json.load(f)
                    logger.info(f"Full config keys: {list(full_config.keys())}")
                    config_str = json.dumps(full_config, indent=2)
                    logger.debug(f"Full config structure: {config_str}")
                    
                    if "live_bfg9k_test" in full_config:
                        self.config = full_config["live_bfg9k_test"]
                        config_keys = list(self.config.keys())
                        msg = f"Found live_bfg9k_test config keys: {config_keys}"
                        logger.info(msg)
                        test_config_str = json.dumps(self.config, indent=2)
                        logger.debug(f"live_bfg9k_test config: {test_config_str}")
                    else:
                        available_keys = list(full_config.keys())
                        error_msg = ("Missing 'live_bfg9k_test' key in config. "
                                     f"Available keys: {available_keys}")
                        logger.error(error_msg)
                        self.config = {}
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    logger.error(f"Raw content: {raw_config}")
                    raise
        else:
            logger.error(f"Config file does not exist: {config_path}")
            current_contents = list(Path('.').iterdir())
            logger.info(f"Current directory contents: {current_contents}")
            tests_exists = Path('tests').exists()
            if tests_exists:
                tests_contents = list(Path('tests').iterdir())
                logger.info(f"Tests directory contents: {tests_contents}")
            else:
                logger.info("tests/ does not exist")
            self.config = {}
        
        logger.info("=== PRE-COMPONENT INITIALIZATION VALIDATION ===")
        logger.info(f"Config available: {bool(self.config)}")
        logger.info(f"Config type: {type(self.config)}")
        
        self.validator = MCPValidator()
        logger.info("✓ MCPValidator initialized")
        
        self.maintenance_config = MaintenanceConfig()
        logger.info("✓ MaintenanceConfig initialized")
        
        self.maintenance_prompts = MaintenancePrompts()
        logger.info("✓ MaintenancePrompts initialized")
        
        self.maintenance_server = MaintenanceServer()
        logger.info("✓ MaintenanceServer initialized")
        
        self.telemetry: List[Dict[str, Any]] = []
        logger.info("=== LiveBFG9KTest INITIALIZATION COMPLETE ===")
    
    def execute_live_fire_test(self) -> List[Dict[str, Any]]:
        """Execute live fire test with real ordinance"""
        logger.info(f"=== STARTING execute_live_fire_test ===")
        logger.info(f"Config available: {bool(self.config)}")
        logger.info(f"Config keys: {list(self.config.keys()) if self.config else 'No config'}")
        
        results = []
        # Updated to use existing test data files instead of missing 
        # bfg9k directory
        test_ontologies = [
            Path("tests/test_data/test_ontology.ttl"),
            Path("tests/fixtures/test_ontologies/guidance_test.ttl"),
            Path("tests/fixtures/test_ontologies/ontology_types.ttl")
        ]
        logger.info(f"Test ontologies: {test_ontologies}")
        
        # Check if test ontology files exist
        for ont_path in test_ontologies:
            logger.info(f"Ontology {ont_path} exists: {ont_path.exists()}")
        
        logger.info("=== ATTEMPTING TO LOAD ORDINANCE ===")
        try:
            ordinance = self._load_ordinance("expert")
            logger.info(f"✓ Ordinance loaded successfully: {type(ordinance)}")
            logger.debug(f"Ordinance content: {ordinance}")
        except Exception as e:
            logger.error(f"✗ ORDINANCE LOADING FAILED: {e}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Exception args: {e.args}")
            logger.error(f"Available config: {self.config}")
            raise
        
        for ontology_path in test_ontologies:
            logger.info(f"Processing ontology: {ontology_path}")
            target = ValidationTarget(
                uri=URIRef(f"file://{ontology_path}"),
                target_type="ontology",
                priority="high"
            )
            result = self._execute_validation(target, ordinance, ontology_path)
            results.append(result)
            self._test_maintenance_components(ontology_path, result)
        
        logger.info(f"=== execute_live_fire_test COMPLETE ===")
        return results
    
    def _test_maintenance_components(self, ontology_path: Path, validation_result: Dict[str, Any]):
        """Test maintenance-related components"""
        logger.debug(f"Testing maintenance components for {ontology_path}")
        
        # Enhanced logging for maintenance config validation
        logger.info("=== TESTING MAINTENANCE CONFIG ===")
        logger.debug(f"Input validation_result type: {type(validation_result)}")
        logger.debug(f"Input validation_result keys: {list(validation_result.keys()) if isinstance(validation_result, dict) else 'Not a dict'}")
        logger.debug(f"Input validation_result: {validation_result}")
        
        try:
            config_result = self.maintenance_config.validate_config(validation_result)
            logger.info(f"Maintenance config validation result type: {type(config_result)}")
            logger.info(f"Maintenance config validation result: {config_result}")
            
            if isinstance(config_result, dict):
                logger.info(f"Config result keys: {list(config_result.keys())}")
                if "valid" in config_result:
                    logger.info(f"Valid status: {config_result['valid']}")
                else:
                    logger.error("✗ MISSING KEY: 'valid' not found in config_result")
                    logger.error(f"Available keys: {list(config_result.keys())}")
            else:
                logger.error(f"✗ UNEXPECTED TYPE: config_result is not a dict: {type(config_result)}")
            
            assert config_result["valid"], f"Maintenance config validation failed. Result: {config_result}"
        except Exception as e:
            logger.error(f"✗ MAINTENANCE CONFIG EXCEPTION: {e}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Exception args: {e.args}")
            raise
        
        # Enhanced logging for maintenance prompts
        logger.info("=== TESTING MAINTENANCE PROMPTS ===")
        try:
            prompt_result = self.maintenance_prompts.generate_prompts(validation_result)
            logger.info(f"Maintenance prompts result type: {type(prompt_result)}")
            logger.info(f"Maintenance prompts result: {prompt_result}")
            
            if isinstance(prompt_result, dict):
                logger.info(f"Prompt result keys: {list(prompt_result.keys())}")
                if "success" in prompt_result:
                    logger.info(f"Success status: {prompt_result['success']}")
                else:
                    logger.error("✗ MISSING KEY: 'success' not found in prompt_result")
                    logger.error(f"Available keys: {list(prompt_result.keys())}")
            else:
                logger.error(f"✗ UNEXPECTED TYPE: prompt_result is not a dict: {type(prompt_result)}")
            
            assert prompt_result["success"], f"Maintenance prompt generation failed. Result: {prompt_result}"
        except Exception as e:
            logger.error(f"✗ MAINTENANCE PROMPTS EXCEPTION: {e}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Exception args: {e.args}")
            raise
        
        # Enhanced logging for maintenance server
        logger.info("=== TESTING MAINTENANCE SERVER ===")
        try:
            server_result = self.maintenance_server.process_validation(validation_result)
            logger.info(f"Maintenance server result type: {type(server_result)}")
            logger.info(f"Maintenance server result: {server_result}")
            
            if isinstance(server_result, dict):
                logger.info(f"Server result keys: {list(server_result.keys())}")
                if "success" in server_result:
                    logger.info(f"Success status: {server_result['success']}")
                else:
                    logger.error("✗ MISSING KEY: 'success' not found in server_result")
                    logger.error(f"Available keys: {list(server_result.keys())}")
            else:
                logger.error(f"✗ UNEXPECTED TYPE: server_result is not a dict: {type(server_result)}")
            
            assert server_result["success"], f"Maintenance server processing failed. Result: {server_result}"
        except Exception as e:
            logger.error(f"✗ MAINTENANCE SERVER EXCEPTION: {e}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Exception args: {e.args}")
            raise
        
        logger.info("✓ All maintenance components validated successfully")
    
    def _load_ordinance(self, rule_set: str) -> Dict[str, Any]:
        """Load validation rules as BFG9K ordinance"""
        logger.info(f"=== LOADING ORDINANCE FOR RULE_SET: {rule_set} ===")
        logger.info(f"Config available: {bool(self.config)}")
        logger.info(f"Config type: {type(self.config)}")
        config_keys = list(self.config.keys()) if isinstance(self.config, dict) else 'Not a dict'
        logger.info(f"Config keys: {config_keys}")
        
        # Updated to use actual config structure: validation_rules instead of ordinance_loading
        if "validation_rules" not in self.config:
            logger.error("✗ MISSING KEY: 'validation_rules' not found in config")
            available_keys = list(self.config.keys()) if isinstance(self.config, dict) else 'Config is not a dict'
            logger.error(f"Available config keys: {available_keys}")
            logger.error(f"Full config content: {self.config}")
            raise KeyError(f"Configuration missing required 'validation_rules' key. Available keys: {available_keys}")
        
        validation_config = self.config["validation_rules"]
        logger.info(f"✓ Found validation_rules config: {type(validation_config)}")
        validation_keys = list(validation_config.keys()) if isinstance(validation_config, dict) else 'Not a dict'
        logger.info(f"Validation config keys: {validation_keys}")
        
        # Check for rule_sets key
        if "rule_sets" not in validation_config:
            logger.error("✗ MISSING KEY: 'rule_sets' not found in validation_rules")
            available_keys = list(validation_config.keys()) if isinstance(validation_config, dict) else 'Not a dict'
            logger.error(f"Available validation_rules keys: {available_keys}")
            raise KeyError("Configuration missing required 'rule_sets' key in validation_rules")
        
        rule_sets = validation_config["rule_sets"]
        logger.info(f"✓ Found rule_sets: {type(rule_sets)}")
        available_rule_sets = list(rule_sets.keys()) if isinstance(rule_sets, dict) else rule_sets
        logger.info(f"Available rule sets: {available_rule_sets}")
        
        # Check for specific rule_set
        if rule_set not in rule_sets:
            logger.error(f"✗ MISSING RULE SET: '{rule_set}' not found in rule_sets")
            logger.error(f"Available rule sets: {available_rule_sets}")
            raise KeyError(f"Rule set '{rule_set}' not found. Available: {available_rule_sets}")
        
        # Updated to use actual config structure: validation_config instead of ordinance_config
        if "validation_config" not in validation_config:
            logger.error("✗ MISSING KEY: 'validation_config' not found in validation_rules")
            raise KeyError("Configuration missing required 'validation_config' key in validation_rules")
        
        val_config = validation_config["validation_config"]
        logger.info(f"✓ Found validation_config: {type(val_config)}")
        available_configs = list(val_config.keys()) if isinstance(val_config, dict) else val_config
        logger.info(f"Available validation configs: {available_configs}")
        
        # Check for 'high' config
        if "high" not in val_config:
            logger.error("✗ MISSING KEY: 'high' not found in validation_config")
            logger.error(f"Available validation configs: {available_configs}")
            raise KeyError("Configuration missing required 'high' key in validation_config")
        
        # Updated to use actual config structure
        result = {
            "rules": self.config["validation_rules"]["rule_sets"][rule_set],
            "config": self.config["validation_rules"]["validation_config"]["high"]
        }
        logger.info("✓ Ordinance loaded successfully")
        logger.debug(f"Ordinance result: {result}")
        return result
    
    def _execute_validation(self, 
                          target: ValidationTarget,
                          ordinance: Dict[str, Any],
                          ontology_path: Path) -> Dict[str, Any]:
        """Execute validation with telemetry collection"""
        logger.debug(f"Executing validation for {ontology_path}")
        result = {
            "target": str(target),
            "ordinance": ordinance,
            "telemetry": {}
        }
        g = Graph()
        g.parse(ontology_path, format="turtle")
        validation_result = self.validator.validate(g, target, ordinance)
        
        # Check if telemetry_collection config exists
        if "telemetry_collection" not in self.config:
            logger.warning("No telemetry_collection config found, using empty metrics")
            metrics = []
        else:
            metrics = self.config["telemetry_collection"]["metrics"]
        
        for metric in metrics:
            result["telemetry"][metric] = self._collect_telemetry(metric, validation_result)
        
        # Fix: Add precision and recall to ordinance config for MaintenanceConfig compatibility
        # MaintenanceConfig.validate_config() expects these in ordinance.config, not telemetry
        if "precision" in result["telemetry"]:
            result["ordinance"]["config"]["precision"] = result["telemetry"]["precision"]
        if "recall" in result["telemetry"]:
            result["ordinance"]["config"]["recall"] = result["telemetry"]["recall"]
        
        logger.debug(f"Updated ordinance config: {result['ordinance']['config']}")
        
        return result
    
    def _collect_telemetry(self, metric: str, validation_result: Dict[str, Any]) -> float:
        """Collect telemetry for specified metric"""
        logger.debug(f"Collecting telemetry for metric: {metric}")
        # In a real implementation this would collect actual metrics
        return 0.0  # Placeholder

@pytest.fixture
def live_test():
    """Fixture for live BFG9K test"""
    config_path = Path("tests/bfg9k_test_config.json")
    return LiveBFG9KTest(config_path)

def test_live_fire_execution(live_test):
    """Test live fire execution with real ordinance"""
    results = live_test.execute_live_fire_test()
    assert len(results) == 3  # One result per test ontology
    for result in results:
        assert "target" in result
        assert "ordinance" in result
        assert "telemetry" in result
        for metric in live_test.config["telemetry_collection"]["metrics"]:
            assert metric in result["telemetry"]

def test_ordinance_loading(live_test):
    """Test ordinance loading"""
    for rule_set in live_test.config["validation_rules"]["rule_sets"]:
        ordinance = live_test._load_ordinance(rule_set)
        assert "rules" in ordinance
        assert "config" in ordinance
        assert isinstance(ordinance["rules"], list)
        assert isinstance(ordinance["config"], dict)

def test_maintenance_components(live_test):
    """Test maintenance-related components"""
    config = live_test.maintenance_config
    assert config is not None
    assert hasattr(config, "validate_config")
    prompts = live_test.maintenance_prompts
    assert prompts is not None
    assert hasattr(prompts, "generate_prompts")
    server = live_test.maintenance_server
    assert server is not None
    assert hasattr(server, "process_validation")

def test_telemetry_collection(live_test):
    """Test telemetry collection"""
    test_result = {
        "target": "test_target",
        "ordinance": {"rules": [], "config": {}},
        "telemetry": {}
    }
    for metric in live_test.config["telemetry_collection"]["metrics"]:
        value = live_test._collect_telemetry(metric, test_result)
        assert isinstance(value, float), f"Telemetry value for {metric} should be float" 