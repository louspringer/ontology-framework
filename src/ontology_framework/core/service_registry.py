"""Centralized service registry for environment-aware configuration management."""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ServiceConfig:
    """Configuration for a specific service."""
    url: str
    timeout: int = 30
    retry_attempts: int = 3
    additional_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_config is None:
            self.additional_config = {}


class ServiceRegistry:
    """Centralized service registry implementing DRY configuration principle."""
    
    _instance = None
    _config_cache = None
    
    def __new__(cls, environment: str = None):
        """Singleton pattern ensures one config source for entire system."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, environment: str = None):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.environment = environment or os.getenv("DEPLOYMENT_ENV", "development")
        self.logger = logging.getLogger(f"service_registry.{self.environment}")
        self._load_centralized_config()
        self._initialized = True
    
    def _load_centralized_config(self):
        """Load configuration from centralized source."""
        if ServiceRegistry._config_cache is None:
            # Default configuration structure
            default_config = {
                "environments": {
                    "development": {
                        "cms": {
                            "url": "http://localhost:8055",
                            "token_env": "DEV_DIRECTUS_TOKEN",
                            "timeout": 10,
                            "retry_attempts": 3
                        },
                        "prometheus": {
                            "port": 8000,
                            "enable_http_server": True,
                            "metrics_path": "/metrics"
                        },
                        "observatory": {
                            "websocket_url": "ws://localhost:3001/ws",
                            "dashboard_url": "http://localhost:3001",
                            "reconnect_interval": 5
                        },
                        "dag_registry": {
                            "backend": "memory",
                            "persistence_enabled": False
                        }
                    },
                    "staging": {
                        "cms": {
                            "url": os.getenv("STAGING_CMS_URL", "https://staging-cms.example.com"),
                            "token_env": "STAGING_DIRECTUS_TOKEN",
                            "timeout": 30,
                            "retry_attempts": 5
                        },
                        "prometheus": {
                            "port": 8000,
                            "registry_url": os.getenv("STAGING_PROMETHEUS_URL", "https://staging-prometheus.example.com"),
                            "push_gateway": os.getenv("STAGING_PUSHGATEWAY_URL")
                        },
                        "observatory": {
                            "websocket_url": os.getenv("STAGING_OBSERVATORY_WS", "wss://staging-observatory.example.com/ws"),
                            "dashboard_url": os.getenv("STAGING_OBSERVATORY_URL", "https://staging-observatory.example.com"),
                            "api_key_env": "STAGING_OBSERVATORY_KEY"
                        },
                        "dag_registry": {
                            "backend": "redis",
                            "redis_url": os.getenv("STAGING_REDIS_URL", "redis://staging-redis.example.com:6379")
                        }
                    },
                    "production": {
                        "cms": {
                            "url": os.getenv("PROD_CMS_URL", "https://cms.example.com"),
                            "token_env": "PROD_DIRECTUS_TOKEN",
                            "timeout": 60,
                            "retry_attempts": 10,
                            "connection_pool_size": 20
                        },
                        "prometheus": {
                            "port": 8000,
                            "registry_url": os.getenv("PROD_PROMETHEUS_URL", "https://prometheus.example.com"),
                            "push_gateway": os.getenv("PROD_PUSHGATEWAY_URL"),
                            "high_availability": True
                        },
                        "observatory": {
                            "websocket_url": os.getenv("PROD_OBSERVATORY_WS", "wss://observatory.example.com/ws"),
                            "dashboard_url": os.getenv("PROD_OBSERVATORY_URL", "https://observatory.example.com"),
                            "api_key_env": "PROD_OBSERVATORY_KEY"
                        },
                        "dag_registry": {
                            "backend": "redis_cluster",
                            "redis_cluster_nodes": [
                                os.getenv("PROD_REDIS_1", "redis-1.example.com:6379"),
                                os.getenv("PROD_REDIS_2", "redis-2.example.com:6379"),
                                os.getenv("PROD_REDIS_3", "redis-3.example.com:6379")
                            ]
                        }
                    }
                },
                "defaults": {
                    "health_check_interval": 30,
                    "service_timeout": 10,
                    "max_retries": 3,
                    "circuit_breaker_threshold": 5,
                    "graceful_degradation_enabled": True
                }
            }
            
            # Try to load from config file, fall back to defaults
            config_file = Path("config") / f"{self.environment}.json"
            if config_file.exists():
                try:
                    with open(config_file) as f:
                        file_config = json.load(f)
                    # Merge with defaults
                    ServiceRegistry._config_cache = self._merge_configs([default_config, file_config])
                    self.logger.info(f"Loaded configuration from {config_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to load config file {config_file}: {e}, using defaults")
                    ServiceRegistry._config_cache = default_config
            else:
                ServiceRegistry._config_cache = default_config
                self.logger.info(f"Using default configuration for {self.environment}")
    
    def _merge_configs(self, configs: list) -> Dict[str, Any]:
        """Merge multiple configuration dictionaries."""
        result = {}
        for config in configs:
            if config:
                self._deep_merge(result, config)
        return result
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """Deep merge source into target dictionary."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get configuration for any service - used by ALL components."""
        try:
            env_config = self._config_cache["environments"][self.environment]
            service_config = env_config.get(service_name, {})
            
            # Merge with defaults
            defaults = self._config_cache.get("defaults", {})
            return {**defaults, **service_config}
        except KeyError as e:
            self.logger.error(f"Configuration not found for service '{service_name}' in environment '{self.environment}': {e}")
            return self._config_cache.get("defaults", {})
    
    def get_cms_config(self) -> ServiceConfig:
        """Get CMS configuration for current environment."""
        config = self.get_service_config("cms")
        return ServiceConfig(
            url=config.get("url", "http://localhost:8055"),
            timeout=config.get("timeout", 30),
            retry_attempts=config.get("retry_attempts", 3),
            additional_config={
                "token_env": config.get("token_env", "DIRECTUS_TOKEN"),
                "connection_pool_size": config.get("connection_pool_size", 10)
            }
        )
    
    def get_prometheus_config(self) -> ServiceConfig:
        """Get Prometheus configuration for current environment."""
        config = self.get_service_config("prometheus")
        return ServiceConfig(
            url=config.get("registry_url", ""),
            timeout=config.get("timeout", 30),
            additional_config={
                "port": config.get("port", 8000),
                "enable_http_server": config.get("enable_http_server", True),
                "metrics_path": config.get("metrics_path", "/metrics"),
                "push_gateway": config.get("push_gateway"),
                "high_availability": config.get("high_availability", False)
            }
        )
    
    def get_observatory_config(self) -> ServiceConfig:
        """Get Observatory configuration for current environment."""
        config = self.get_service_config("observatory")
        return ServiceConfig(
            url=config.get("dashboard_url", "http://localhost:3001"),
            timeout=config.get("timeout", 30),
            additional_config={
                "websocket_url": config.get("websocket_url", "ws://localhost:3001/ws"),
                "api_key_env": config.get("api_key_env"),
                "reconnect_interval": config.get("reconnect_interval", 5)
            }
        )
    
    def get_dag_registry_config(self) -> ServiceConfig:
        """Get DAG Registry configuration for current environment."""
        config = self.get_service_config("dag_registry")
        return ServiceConfig(
            url="",  # DAG registry doesn't have a single URL
            timeout=config.get("timeout", 30),
            additional_config={
                "backend": config.get("backend", "memory"),
                "persistence_enabled": config.get("persistence_enabled", False),
                "redis_url": config.get("redis_url"),
                "redis_cluster_nodes": config.get("redis_cluster_nodes", [])
            }
        )
    
    def health_check_all_services(self) -> Dict[str, bool]:
        """Check health of all configured services."""
        services = ["cms", "prometheus", "observatory", "dag_registry"]
        health_status = {}
        
        for service in services:
            try:
                config = self.get_service_config(service)
                # Basic connectivity check (can be enhanced with actual health endpoints)
                health_status[service] = bool(config)
            except Exception as e:
                self.logger.error(f"Health check failed for {service}: {e}")
                health_status[service] = False
        
        return health_status
    
    @classmethod
    def reset_instance(cls):
        """Reset singleton instance (useful for testing)."""
        cls._instance = None
        cls._config_cache = None


# Convenience function for getting the global service registry
def get_service_registry(environment: str = None) -> ServiceRegistry:
    """Get the global service registry instance."""
    return ServiceRegistry(environment)