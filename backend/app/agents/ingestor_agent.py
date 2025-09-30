"""
Ingestor Agent for Memory Graph

Extracts entities and relationships from text sources (deploy logs, READMEs, etc.)
and upserts them into the memory graph as structured nodes and edges.
"""

import re
from typing import List, Tuple, Dict, Any
import structlog

from .memory_graph import MemoryGraph, Node, Edge, EntityTypes, RelationTypes

logger = structlog.get_logger(__name__)


class IngestorAgent:
    """Agent that extracts entities/relations from text and populates the memory graph."""
    
    def __init__(self, memory_graph: MemoryGraph):
        self.graph = memory_graph
        
        # Simple patterns for entity extraction
        self.service_patterns = [
            r'\b([a-z0-9_-]+)\s+(?:service|app|application)',
            r'service\s+([a-z0-9_-]+)',
            r'\b([a-z0-9_-]+)\s+(?:on|deployed to|running on)\s+(?:vercel|railway|aws)',
            r'^([a-z0-9_-]+)(?:\s+requires?|\s+needs?)',
        ]
        
        self.envvar_patterns = [
            r'\b([A-Z_][A-Z0-9_]*)\b',  # Standard env var format
            r'(?:env|environment|config).*?([A-Z_][A-Z0-9_]*)',
            r'requires?\s+([A-Z_][A-Z0-9_]*)',
            r'missing\s+([A-Z_][A-Z0-9_]*)',
        ]
        
        self.incident_patterns = [
            r'(?:incident|issue|error|problem)\s+([A-Z]+-\d+)',
            r'(INC-\d+)',
            r'#(\d+)',  # Issue numbers
        ]
        
        # Relation patterns
        self.requires_patterns = [
            r'([a-z0-9_-]+).*?(?:requires?|needs?|depends on).*?([A-Z_][A-Z0-9_]*)',
            r'([a-z0-9_-]+).*?(?:missing|lacks).*?([A-Z_][A-Z0-9_]*)',
            r'([a-z0-9_-]+)\s+(?:on|deployed to).*?requires?\s+([A-Z_][A-Z0-9_]*)',
            r'([a-z0-9_-]+).*?requires?\s+([A-Z_][A-Z0-9_]*),?\s*([A-Z_][A-Z0-9_]*)',  # Multiple vars
        ]
        
        self.impacts_patterns = [
            r'(?:incident|issue|error)\s+([A-Z]+-\d+).*?(?:impacts?|affects?).*?([a-z0-9_-]+)',
            r'([A-Z]+-\d+).*?(?:blocks?|prevents?).*?([a-z0-9_-]+)',
            r'missing\s+([A-Z_][A-Z0-9_]*).*?(?:blocks?|prevents?).*?([a-z0-9_-]+)',
        ]
    
    def ingest(self, text: str, source_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract entities and relations from text and upsert into memory graph.
        
        Returns a summary of what was extracted.
        """
        if source_info is None:
            source_info = {}
        
        logger.info("Starting ingestion", text_length=len(text), source=source_info.get("source"))
        
        # Extract entities
        services = self._extract_services(text)
        envvars = self._extract_envvars(text)
        incidents = self._extract_incidents(text)
        
        # Create nodes
        nodes_created = []
        
        for service_name in services:
            node = Node(
                id=f"svc:{service_name}",
                type=EntityTypes.SERVICE,
                props={
                    "name": service_name,
                    "source": source_info.get("source"),
                    "extracted_from": text[:100] + "..." if len(text) > 100 else text
                }
            )
            self.graph.upsert_node(node)
            nodes_created.append(node)
        
        for var_name in envvars:
            node = Node(
                id=f"env:{var_name}",
                type=EntityTypes.ENVVAR,
                props={
                    "key": var_name,
                    "source": source_info.get("source"),
                    "extracted_from": text[:100] + "..." if len(text) > 100 else text
                }
            )
            self.graph.upsert_node(node)
            nodes_created.append(node)
        
        for incident_id in incidents:
            node = Node(
                id=f"inc:{incident_id}",
                type=EntityTypes.INCIDENT,
                props={
                    "id": incident_id,
                    "source": source_info.get("source"),
                    "extracted_from": text[:100] + "..." if len(text) > 100 else text
                }
            )
            self.graph.upsert_node(node)
            nodes_created.append(node)
        
        # Extract relationships
        edges_created = []
        
        # SERVICE_REQUIRES_ENVVAR relations
        requires_relations = self._extract_requires_relations(text)
        for service_name, var_name in requires_relations:
            service_id = f"svc:{service_name}"
            var_id = f"env:{var_name}"
            
            # Ensure nodes exist
            if service_id in self.graph.nodes and var_id in self.graph.nodes:
                edge = Edge(
                    type=RelationTypes.SERVICE_REQUIRES_ENVVAR,
                    from_id=service_id,
                    to_id=var_id,
                    props={"source": source_info.get("source")}
                )
                try:
                    self.graph.add_edge(edge)
                    edges_created.append(edge)
                except ValueError as e:
                    logger.debug("Skipped edge", error=str(e))
        
        # INCIDENT_IMPACTS_SERVICE relations
        impacts_relations = self._extract_impacts_relations(text)
        for incident_id, service_name in impacts_relations:
            inc_id = f"inc:{incident_id}"
            service_id = f"svc:{service_name}"
            
            if inc_id in self.graph.nodes and service_id in self.graph.nodes:
                edge = Edge(
                    type=RelationTypes.INCIDENT_IMPACTS_SERVICE,
                    from_id=inc_id,
                    to_id=service_id,
                    props={"source": source_info.get("source")}
                )
                try:
                    self.graph.add_edge(edge)
                    edges_created.append(edge)
                except ValueError as e:
                    logger.debug("Skipped edge", error=str(e))
        
        result = {
            "nodes_created": len(nodes_created),
            "edges_created": len(edges_created),
            "services": list(services),
            "envvars": list(envvars), 
            "incidents": list(incidents),
            "nodes": [{"id": n.id, "type": n.type, "props": n.props} for n in nodes_created],
            "edges": [{"type": e.type, "from": e.from_id, "to": e.to_id} for e in edges_created]
        }
        
        logger.info(
            "Completed ingestion",
            nodes_created=len(nodes_created),
            edges_created=len(edges_created),
            services=len(services),
            envvars=len(envvars),
            incidents=len(incidents)
        )
        
        return result
    
    def _extract_services(self, text: str) -> set:
        """Extract service names from text."""
        services = set()
        text_lower = text.lower()
        
        for pattern in self.service_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                service_name = match.group(1).strip()
                if len(service_name) >= 2 and service_name not in ['the', 'and', 'or', 'is', 'a']:
                    services.add(service_name)
        
        return services
    
    def _extract_envvars(self, text: str) -> set:
        """Extract environment variable names from text."""
        envvars = set()
        
        for pattern in self.envvar_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                var_name = match.group(1).strip()
                if len(var_name) >= 3 and '_' in var_name:  # Basic validation for env vars
                    envvars.add(var_name)
        
        return envvars
    
    def _extract_incidents(self, text: str) -> set:
        """Extract incident IDs from text.""" 
        incidents = set()
        
        for pattern in self.incident_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                incident_id = match.group(1).strip()
                if incident_id:
                    incidents.add(incident_id)
        
        return incidents
    
    def _extract_requires_relations(self, text: str) -> List[Tuple[str, str]]:
        """Extract service->envvar requirement relations."""
        relations = []
        text_lower = text.lower()
        
        # Extract services and envvars first 
        services = self._extract_services(text)
        envvars = self._extract_envvars(text)
        
        # Use patterns to find relations
        for pattern in self.requires_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                service_name = match.group(1).strip()
                var_name = match.group(2).strip()
                if service_name and var_name:
                    relations.append((service_name, var_name))
                
                # Handle multiple env vars in same match (group 3)
                if len(match.groups()) > 2 and match.group(3):
                    var_name2 = match.group(3).strip()
                    if var_name2:
                        relations.append((service_name, var_name2))
        
        # Also try a simpler approach: if text mentions service and envvars together
        for service in services:
            for envvar in envvars:
                service_lower = service.lower()
                
                # Check if service and envvar appear in same sentence/context
                sentences = text.split('.')
                for sentence in sentences:
                    sentence_lower = sentence.lower()
                    if (service_lower in sentence_lower and 
                        envvar in sentence and 
                        any(keyword in sentence_lower for keyword in ['require', 'need', 'depend', 'missing'])):
                        relations.append((service, envvar))
        
        return list(set(relations))  # Remove duplicates
    
    def _extract_impacts_relations(self, text: str) -> List[Tuple[str, str]]:
        """Extract incident->service impact relations."""
        relations = []
        
        # Get incidents and services first
        incidents = self._extract_incidents(text)
        services = self._extract_services(text)
        
        # Use patterns
        for pattern in self.impacts_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                incident_id = match.group(1).strip()
                service_name = match.group(2).strip()
                if incident_id and service_name:
                    relations.append((incident_id, service_name))
        
        # Simple co-occurrence approach
        for incident_id in incidents:
            for service in services:
                # Check if incident and service appear in same sentence
                sentences = text.split('.')
                for sentence in sentences:
                    sentence_lower = sentence.lower()
                    if (incident_id.lower() in sentence_lower and 
                        service.lower() in sentence_lower and
                        any(keyword in sentence_lower for keyword in ['affect', 'impact', 'block', 'prevent', 'cause'])):
                        relations.append((incident_id, service))
        
        return list(set(relations))  # Remove duplicates