import logging
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from git import Union
from rdflib import Graph, URIRef
from rdflib.query import ResultRow

logger = logging.getLogger(__name__)

class ConfigChangeDetector:
    """Tracks and detects changes in configuration files."""
    
    def __init__(self, config_file: str = "bfg9k_config.ttl"):
        """Initialize the change detector.
        
        Args:
            config_file: Path to the configuration file to monitor
        """
        self.config_file = Path(config_file)
        self.history_file = Path("logs/config_changes.json")
        self.history_file.parent.mkdir(exist_ok=True)
        self._load_history()
    
    def _load_history(self):
        """Load change history from file."""
        try:
            if self.history_file.exists():
                self.history = json.loads(self.history_file.read_text())
            else:
                self.history = []
        except Exception as e:
            logger.error(f"Failed to load change history: {e}")
            self.history = []
    
    def _save_history(self):
        """Save change history to file."""
        try:
            self.history_file.write_text(json.dumps(self.history, indent=2))
        except Exception as e:
            logger.error(f"Failed to save change history: {e}")
    
    def _compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _extract_graphdb_config(self, content: str) -> Dict:
        """Extract GraphDB configuration from TTL content."""
        g = Graph()
        g.parse(data=content, format="turtle")
        
        config = {}
        ns1 = URIRef("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k# ")
        
        # Query for all configuration properties
        query = """
        PREFIX ns1: <https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k#>
        SELECT ?prop ?value WHERE {
            ?s a ns1:ServerConfiguration ;
               ?prop ?value .
        }
        """
        for row in g.query(query):
            if isinstance(row, ResultRow):
                prop = str(row[0]).split('#')[-1]
                value = str(row[1])
                config[prop] = value
        
        return config
    
    def detect_changes(self) -> Optional[Dict]:
        """Detect changes in configuration file.
        
        Returns:
            Dict containing change details if changes detected None otherwise
        """
        try:
            if not self.config_file.exists():
                logger.error(f"Configuration file not found: {self.config_file}")
                return None
            
            current_content = self.config_file.read_text()
            current_hash = self._compute_hash(current_content)
            
            # Get current configuration
            try:
                current_config = self._extract_graphdb_config(current_content)
            except Exception as e:
                logger.error(f"Failed to parse current configuration: {e}")
                return None
            
            # Check if we have previous changes
            if not self.history:
                change = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'initial',
                    'hash': current_hash,
                    'config': current_config
                }
                self.history.append(change)
                self._save_history()
                return change
            
            # Compare with last known configuration
            last_change = self.history[-1]
            if current_hash != last_change['hash']:
                # Detect specific changes
                changes: Dict[str, Dict[str, Union[str, Dict[str, str]]]] = {
                    'added': {},
                    'removed': {},
                    'modified': {}
                }
                
                last_config = last_change['config']
                
                # Find added and modified properties
                for key, value in current_config.items():
                    if key not in last_config:
                        changes['added'][key] = value
                    elif last_config[key] != value:
                        changes['modified'][key] = {
                            'old': last_config[key],
                            'new': value
                        }
                
                # Find removed properties
                for key in last_config:
                    if key not in current_config:
                        changes['removed'][key] = last_config[key]
                
                change = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'update',
                    'hash': current_hash,
                    'config': current_config,
                    'changes': changes
                }
                
                self.history.append(change)
                self._save_history()
                return change
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting changes: {e}")
            return None
    
    def get_history(self) -> List[Dict]:
        """Get configuration change history.
        
        Returns:
            List of change records
        """
        return self.history
    
    def get_last_change(self) -> Optional[Dict]:
        """Get most recent configuration change.
        
        Returns:
            Most recent change record or None if no history
        """
        return self.history[-1] if self.history else None
    
    def export_history_ttl(self) -> str:
        """Export change history as TTL.
        
        Returns:
            Change history in TTL format
        """
        g = Graph()
        ns1 = URIRef("https://raw.githubusercontent.com/louspringer/bfg9k/main/bfg9k# ")
        
        for change in self.history:
            change_uri = URIRef(f"urn:config:change:{change['timestamp']}")
            g.add((change_uri, URIRef(f"{ns1}changeType"), URIRef(f"{ns1}{change['type']}")))
            g.add((change_uri, URIRef(f"{ns1}timestamp"), URIRef(change['timestamp'])))
            g.add((change_uri, URIRef(f"{ns1}configHash"), URIRef(change['hash'])))
            
            if 'changes' in change:
                for change_type, props in change['changes'].items():
                    if isinstance(props, dict):
                        for prop, value in props.items():
                            if isinstance(value, dict):
                                # Modified property
                                g.add((change_uri, URIRef(f"{ns1}modified"), URIRef(f"{ns1}{prop}")))
                                g.add((URIRef(f"{ns1}{prop}"), URIRef(f"{ns1}oldValue"), URIRef(value['old'])))
                                g.add((URIRef(f"{ns1}{prop}"), URIRef(f"{ns1}newValue"), URIRef(value['new'])))
                            else:
                                # Added or removed property
                                g.add((change_uri, URIRef(f"{ns1}{change_type}"), URIRef(f"{ns1}{prop}")))
                                g.add((URIRef(f"{ns1}{prop}"), URIRef(f"{ns1}value"), URIRef(value)))
        
        return g.serialize(format='turtle') 