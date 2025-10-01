"""Enhanced ReflectiveModule with ServiceRegistry integration for ontology framework."""

import os
import logging
from typing import Dict, Any, Optional, List
from .unified_reflective_module import ReflectiveModule, ModuleStatus, ModuleCapability
from .service_registry import ServiceRegistry, get_service_registry


class OntologyReflectiveModule(ReflectiveModule):
    """Enhanced ReflectiveModule with ServiceRegistry integration for ontology framework."""
    
    def __init__(self, environment: str = None):
        # Initialize service registry first
        self.service_registry = get_service_registry(environment)
        self.environment = self.service_registry.environment
        
        # Initialize base ReflectiveModule
        super().__init__()
        
        # Override logger to include environment context
        self._logger = logging.getLogger(f"ontology_framework.{self.__class__.__name__}.{self.environment}")
        
        # Initialize service clients with environment-specific configuration
        self._initialize_service_clients()
    
    def _initialize_service_clients(self):
        """Initialize service clients using ServiceRegistry configuration."""
        try:
            # CMS client initialization
            cms_config = self.service_registry.get_cms_config()
            self._cms_config = cms_config
            
            # Prometheus configuration
            prometheus_config = self.service_registry.get_prometheus_config()
            self._prometheus_config = prometheus_config
            
            # Observatory configuration
            observatory_config = self.service_registry.get_observatory_config()
            self._observatory_config = observatory_config
            
            self._logger.info(f"Initialized service clients for environment: {self.environment}")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize service clients: {e}")
            # Graceful degradation - continue without external services
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information including environment context."""
        base_info = {
            "module_id": getattr(self, "module_id", self.__class__.__name__),
            "module_name": self.__class__.__name__,
            "version": "1.0.0",
            "environment": self.environment,
            "service_registry_status": "active"
        }
        
        # Add service health information
        try:
            service_health = self.service_registry.health_check_all_services()
            base_info["service_health"] = service_health
        except Exception as e:
            self._logger.warning(f"Could not get service health: {e}")
            base_info["service_health"] = {}
        
        return base_info
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING,
            ModuleCapability.API_INTEGRATION
        ]
    
    def get_health_status(self) -> 'ModuleHealth':
        """Get module health status including service dependencies."""
        from .unified_reflective_module import ModuleHealth
        
        # Base health metrics
        uptime = (self._last_activity - self._start_time).total_seconds()
        
        # Check service dependencies
        issues = []
        health_score = 1.0
        
        try:
            service_health = self.service_registry.health_check_all_services()
            unhealthy_services = [service for service, healthy in service_health.items() if not healthy]
            
            if unhealthy_services:
                issues.extend([f"Service {service} unavailable" for service in unhealthy_services])
                health_score -= 0.1 * len(unhealthy_services)  # Reduce score for each unhealthy service
        except Exception as e:
            issues.append(f"Service health check failed: {e}")
            health_score -= 0.2
        
        # Determine overall status
        if health_score >= 0.9:
            status = ModuleStatus.HEALTHY
        elif health_score >= 0.7:
            status = ModuleStatus.WARNING
        else:
            status = ModuleStatus.DEGRADED
        
        return ModuleHealth(
            module_id=getattr(self, "module_id", self.__class__.__name__),
            status=status,
            health_score=max(0.0, health_score),
            issues=issues,
            last_check=self._last_activity,
            uptime_seconds=uptime,
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> 'GracefulDegradationResult':
        """Perform graceful degradation when services are unavailable."""
        from .unified_reflective_module import GracefulDegradationResult
        
        try:
            # Check which services are available
            service_health = self.service_registry.health_check_all_services()
            
            degraded_capabilities = []
            remaining_capabilities = list(self.get_capabilities())
            
            # If CMS is unavailable, degrade API integration capability
            if not service_health.get("cms", False):
                if ModuleCapability.API_INTEGRATION in remaining_capabilities:
                    remaining_capabilities.remove(ModuleCapability.API_INTEGRATION)
                    degraded_capabilities.append(ModuleCapability.API_INTEGRATION)
            
            # If Prometheus is unavailable, degrade monitoring capability
            if not service_health.get("prometheus", False):
                if ModuleCapability.MONITORING in remaining_capabilities:
                    remaining_capabilities.remove(ModuleCapability.MONITORING)
                    degraded_capabilities.append(ModuleCapability.MONITORING)
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
            
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def store_content(self, content_id: str, collection: str, data: Dict[str, Any]) -> bool:
        """Store content using environment-appropriate CMS."""
        try:
            # Use CMS configuration from ServiceRegistry
            cms_config = self._cms_config
            
            # Add environment and module context to data
            enhanced_data = {
                **data,
                "environment": self.environment,
                "module_id": getattr(self, "module_id", self.__class__.__name__),
                "created_by": self.__class__.__name__
            }
            
            # Try to store in CMS (implementation would use actual CMS client)
            self._logger.info(f"Storing content {content_id} in collection {collection} (environment: {self.environment})")
            
            # For now, use the base implementation with enhanced data
            return super().store_content(content_id, collection, enhanced_data)
            
        except Exception as e:
            self._logger.error(f"Failed to store content {content_id}: {e}")
            return False
    
    def get_content(self, content_id: str, collection: str = "content") -> Optional[Dict[str, Any]]:
        """Retrieve content from environment-appropriate CMS."""
        try:
            # Use CMS configuration from ServiceRegistry
            cms_config = self._cms_config
            
            self._logger.debug(f"Retrieving content {content_id} from collection {collection} (environment: {self.environment})")
            
            # Use base implementation for now
            return super().get_content(content_id, collection)
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve content {content_id}: {e}")
            return None
    
    def emit_observation(self, message: str, event_type: str = "info", context: Optional[Dict[str, Any]] = None, emoji: Optional[str] = None):
        """Emit observation with environment context."""
        # Add environment context to observation
        enhanced_context = {
            "environment": self.environment,
            "module": self.__class__.__name__,
            **(context or {})
        }
        
        # Use base implementation with enhanced context
        super().emit_observation(message, event_type, enhanced_context, emoji)
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get configuration for a specific service."""
        return self.service_registry.get_service_config(service_name)
    
    def is_service_available(self, service_name: str) -> bool:
        """Check if a specific service is available."""
        try:
            health_status = self.service_registry.health_check_all_services()
            return health_status.get(service_name, False)
        except Exception:
            return False