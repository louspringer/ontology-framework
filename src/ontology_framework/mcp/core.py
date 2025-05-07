"""
Core MCP implementation.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Callable, AsyncContextManager
from datetime import datetime
import logging
from pathlib import Path
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
import asyncio
from contextlib import asynccontextmanager

@dataclass
class ValidationContext:
    """Context for validation operations."""
    ontology_path: Path
    target_files: List[Path]
    phase: str
    metadata: Dict[str, Any]
    timestamp: datetime = datetime.now()

@dataclass
class ValidationResult:
    """Result of a validation operation."""
    success: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]

class MCPTypes:
    """MCP type definitions."""
    
    @dataclass
    class TextContent:
        type: str
        text: str

    @dataclass
    class PromptMessage:
        role: str
        content: 'MCPTypes.TextContent'

    @dataclass
    class PromptArgument:
        name: str
        description: str
        required: bool = True

    @dataclass
    class Prompt:
        name: str
        description: str
        arguments: List['MCPTypes.PromptArgument']

    @dataclass
    class GetPromptResult:
        description: str
        messages: List['MCPTypes.PromptMessage']

class MCPServer:
    """MCP server implementation."""
    
    def __init__(self, name: str, lifespan: Optional[AsyncContextManager] = None):
        self.name = name
        self.lifespan = lifespan
        self.request_context = None
        self._prompt_handlers: Dict[str, Callable] = {}
        self._tool_handlers: Dict[str, Callable] = {}

    def list_prompts(self) -> Callable:
        """Decorator for list_prompts handler."""
        def decorator(func: Callable) -> Callable:
            self._prompt_handlers['list_prompts'] = func
            return func
        return decorator

    def get_prompt(self) -> Callable:
        """Decorator for get_prompt handler."""
        def decorator(func: Callable) -> Callable:
            self._prompt_handlers['get_prompt'] = func
            return func
        return decorator

    def call_tool(self) -> Callable:
        """Decorator for call_tool handler."""
        def decorator(func: Callable) -> Callable:
            self._tool_handlers['call_tool'] = func
            return func
        return decorator

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming request."""
        method = request.get('method')
        if method == 'list_prompts':
            handler = self._prompt_handlers.get('list_prompts')
            if handler:
                return await handler()
        elif method == 'get_prompt':
            handler = self._prompt_handlers.get('get_prompt')
            if handler:
                name = request.get('name')
                arguments = request.get('arguments')
                return await handler(name, arguments)
        elif method == 'call_tool':
            handler = self._tool_handlers.get('call_tool')
            if handler:
                name = request.get('name')
                arguments = request.get('arguments')
                return await handler(name, arguments)
        raise ValueError(f"Unknown method: {method}")

class MCPCore:
    """Core MCP implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_config = self.config.get('logging', {})
        log_file = log_config.get('file')
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            filename=log_file
        )
    
    def _validate_phase_order(self, phase: str) -> bool:
        """Validate phase order."""
        phase_execution = self.config.get('validation', {}).get('phaseExecution', {}).get(phase, {})
        if not phase_execution:
            return False
        
        order = phase_execution.get('order', [])
        if not order:
            return False
            
        return phase in order
    
    def _validate_required_files(self, phase: str, context: ValidationContext) -> List[str]:
        """Validate required files for phase."""
        errors = []
        phase_execution = self.config.get('validation', {}).get('phaseExecution', {}).get(phase, {})
        if not phase_execution:
            return [f"No phase execution configuration found for {phase}"]
            
        required_files = phase_execution.get('requiredFiles', [])
        for file in required_files:
            file_path = Path(file)
            if not file_path.exists():
                errors.append(f"Required file not found: {file}")
                
        return errors
    
    def _execute_validation_rules(self, phase: str, context: ValidationContext) -> List[str]:
        """Execute validation rules for phase."""
        errors: List[str] = []
        warnings: List[str] = []
        phase_execution = self.config.get('validation', {}).get('phaseExecution', {}).get(phase, {})
        if not phase_execution:
            return [f"No phase execution configuration found for {phase}"]
            
        validation_rules = phase_execution.get('validationRules', [])
        rules_config = self.config.get('validationRules', {})
        
        self.logger.debug(f"Executing validation rules for phase {phase}: {validation_rules}")
        
        for rule_name in validation_rules:
            rule = rules_config.get(rule_name)
            if not rule:
                errors.append(f"Validation rule not found: {rule_name}")
                continue
                
            # Execute SPARQL query if provided
            if 'sparql' in rule:
                try:
                    g = Graph()
                    g.parse(str(context.ontology_path), format="turtle")
                    self.logger.debug(f"Executing SPARQL query for rule {rule_name}:\n{rule['sparql']}")
                    results = list(g.query(rule['sparql']))
                    self.logger.debug(f"Query results for rule {rule_name}: {len(results)} violations found")
                    if results:
                        # Format result details
                        details = [", ".join(str(x) for x in result) for result in results]
                        error_msg = f"{rule['message']}: {len(results)} violations found\n"
                        error_msg += "Details:\n" + "\n".join(f"- {detail}" for detail in details)
                        errors.append(error_msg)
                        self.logger.debug(f"Rule {rule_name} violations:\n{error_msg}")
                except Exception as e:
                    error_msg = f"Error executing rule {rule_name}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
                
        return errors
    
    def validate(self, context: ValidationContext) -> ValidationResult:
        """Execute validation based on context."""
        try:
            self.logger.info(f"Starting validation for phase: {context.phase}")
            
            errors = []
            warnings = []
            metadata = {
                'phase': context.phase,
                'timestamp': context.timestamp.isoformat(),
                'config_version': self.config.get('metadata', {}).get('version', 'unknown'),
                'errors': [],
                'warnings': []
            }
            
            # Validate phase order if required
            if self.config.get('validation', {}).get('rules', {}).get('phaseOrder', False):
                if not self._validate_phase_order(context.phase):
                    error = f"Invalid phase order for: {context.phase}"
                    errors.append(error)
                    metadata['errors'].append(error)
                    self.logger.debug(f"Phase order validation failed: {error}")
            
            # Validate required files
            file_errors = self._validate_required_files(context.phase, context)
            errors.extend(file_errors)
            metadata['errors'].extend(file_errors)
            if file_errors:
                self.logger.debug(f"File validation errors: {file_errors}")
            
            # Execute validation rules
            rule_errors = self._execute_validation_rules(context.phase, context)
            errors.extend(rule_errors)
            metadata['errors'].extend(rule_errors)
            if rule_errors:
                self.logger.debug(f"Rule validation errors: {rule_errors}")
            
            result = ValidationResult(
                success=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                metadata=metadata
            )
            self.logger.debug(f"Validation result: {result}")
            return result
            
        except Exception as e:
            error = f"Validation error: {str(e)}"
            self.logger.error(error)
            return ValidationResult(
                success=False,
                errors=[error],
                warnings=[],
                metadata={
                    'phase': context.phase,
                    'timestamp': context.timestamp.isoformat(),
                    'errors': [error]
                }
            )
    
    def execute_phase(self, phase: str, context: Optional[ValidationContext] = None) -> ValidationResult:
        """Execute a specific phase of the MCP process."""
        if context is None:
            context = ValidationContext(
                ontology_path=Path(self.config.get('ontologyPath', '')),
                target_files=[Path(f) for f in self.config.get('targetFiles', [])],
                phase=phase,
                metadata=self.config.get('metadata', {})
            )
            
        # Update context phase
        context.phase = phase
        
        return self.validate(context) 