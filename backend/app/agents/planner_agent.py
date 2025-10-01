"""
Planner Agent for Memory Graph

Answers tasks using only the graph structure (no raw text). 
Demonstrates multi-hop reasoning across entity relationships.
"""

from typing import List, Dict, Any, Optional
import structlog

from .memory_graph import MemoryGraph, Node, Edge, EntityTypes, RelationTypes

logger = structlog.get_logger(__name__)


class PlannerAgent:
    """Agent that answers questions using only memory graph queries."""
    
    def __init__(self, memory_graph: MemoryGraph):
        self.graph = memory_graph
    
    def answer_query(self, query: str, query_type: str = "auto") -> Dict[str, Any]:
        """
        Answer a query using only graph structure.
        
        Query types:
        - "blocking_analysis": What's blocking a service rollout?
        - "missing_envvars": What env vars are missing for a service?
        - "related_incidents": What incidents relate to rollout risks?
        - "service_dependencies": What does a service depend on?
        - "impact_analysis": What services are impacted by an incident?
        - "resource_impact": What services depend on a resource?
        - "all_dependencies": Show all service dependencies
        - "risk_analysis": Which services have the most dependencies?
        """
        logger.info("Processing query", query=query, query_type=query_type)
        
        # Auto-detect query type from keywords
        if query_type == "auto":
            query_type = self._detect_query_type(query)
        
        # Extract service name from query
        service_name = self._extract_service_from_query(query)
        
        result = {
            "query": query,
            "query_type": query_type,
            "service_name": service_name,
            "answer": "",
            "evidence": [],
            "graph_operations": []
        }
        
        try:
            if query_type == "blocking_analysis":
                result = self._analyze_blocking_factors(service_name, result)
            elif query_type == "missing_envvars":
                result = self._find_missing_envvars(service_name, result)
            elif query_type == "related_incidents":
                result = self._find_related_incidents(service_name, result)
            elif query_type == "service_dependencies":
                result = self._analyze_service_dependencies(service_name, result)
            elif query_type == "impact_analysis":
                result = self._analyze_incident_impact(query, result)
            elif query_type == "resource_impact":
                result = self._analyze_resource_impact(query, result)
            elif query_type == "all_dependencies":
                result = self._show_all_dependencies(result)
            elif query_type == "risk_analysis":
                result = self._analyze_service_risks(result)
            else:
                result["answer"] = f"Unknown query type: {query_type}"
        
        except Exception as e:
            logger.error("Error processing query", query=query, error=str(e))
            result["answer"] = f"Error processing query: {str(e)}"
        
        return result
    
    def _detect_query_type(self, query: str) -> str:
        """Auto-detect query type from keywords."""
        query_lower = query.lower()
        
        # Order matters - more specific patterns first
        if any(word in query_lower for word in ["blocking", "blocks", "prevent"]):
            return "blocking_analysis"
        elif any(word in query_lower for word in ["missing", "need", "require"]) and "all" not in query_lower:
            return "missing_envvars"
        elif "redis" in query_lower or ("down" in query_lower and "goes" in query_lower) or "affected if" in query_lower:
            return "resource_impact"
        elif any(word in query_lower for word in ["all", "show me", "dependencies across"]):
            return "all_dependencies"
        elif "most dependencies" in query_lower or "highest risk" in query_lower:
            return "risk_analysis"
        elif "incidents are related" in query_lower or ("incident" in query_lower and "related" in query_lower):
            return "related_incidents"
        elif "incidents have occurred" in query_lower or ("incident" in query_lower and "deployment" in query_lower):
            return "related_incidents"
        elif any(word in query_lower for word in ["depend", "requirement", "needs"]):
            return "service_dependencies"
        elif any(word in query_lower for word in ["affects", "impacts"]) and "INC-" in query.upper():
            return "impact_analysis"
        elif "incident" in query_lower:
            return "related_incidents"
        else:
            return "blocking_analysis"  # Default
    
    def _extract_service_from_query(self, query: str) -> Optional[str]:
        """Extract service name from query text."""
        # Look for known services in the graph
        services = self.graph.get_nodes_by_type(EntityTypes.SERVICE)
        
        for service in services:
            service_name = service.props.get("name", "")
            if service_name.lower() in query.lower():
                return service_name
        
        return None
    
    def _analyze_blocking_factors(self, service_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze what's blocking a service rollout."""
        if not service_name:
            result["answer"] = "No service specified in query"
            return result
        
        service_id = f"svc:{service_name}"
        service_node = self.graph.get_node(service_id)
        
        if not service_node:
            result["answer"] = f"Service '{service_name}' not found in memory graph"
            return result
        
        result["graph_operations"].append(f"Found service node: {service_id}")
        
        blocking_factors = []
        
        # Check for missing environment variables
        required_envvars = self.graph.get_neighbors(service_id, RelationTypes.SERVICE_REQUIRES_ENVVAR)
        result["graph_operations"].append(f"Found {len(required_envvars)} required env vars")
        
        for envvar in required_envvars:
            # In a real system, we'd check if the env var is actually set
            # For this demo, we'll assume missing if no "value" prop
            if not envvar.props.get("value"):
                blocking_factors.append({
                    "type": "missing_envvar",
                    "description": f"Missing environment variable: {envvar.props.get('key')}",
                    "node_id": envvar.id
                })
        
        # Check for related incidents - fix direction
        # Look for incidents that impact this service (incoming edges)
        incident_paths = []
        for edge in self.graph.edges:
            if (edge.type == RelationTypes.INCIDENT_IMPACTS_SERVICE and 
                edge.to_id == service_id):
                incident_node = self.graph.get_node(edge.from_id)
                if incident_node:
                    # Create a path-like structure for consistency
                    incident_paths.append([service_node, incident_node])
        
        result["graph_operations"].append(f"Found {len(incident_paths)} incident impacts")
        
        for path in incident_paths:
            if len(path) >= 2:
                incident = path[-1]  # Last node in path should be incident
                blocking_factors.append({
                    "type": "related_incident", 
                    "description": f"Related incident: {incident.props.get('id')} impacts service",
                    "node_id": incident.id,
                    "path_length": len(path)
                })
        
        if blocking_factors:
            result["answer"] = f"Found {len(blocking_factors)} blocking factors for {service_name} rollout"
            result["evidence"] = blocking_factors
        else:
            result["answer"] = f"No blocking factors found for {service_name} rollout"
        
        return result
    
    def _find_missing_envvars(self, service_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Find missing environment variables for a service."""
        if not service_name:
            result["answer"] = "No service specified in query"
            return result
        
        service_id = f"svc:{service_name}"
        service_node = self.graph.get_node(service_id)
        
        if not service_node:
            result["answer"] = f"Service '{service_name}' not found in memory graph"
            return result
        
        required_envvars = self.graph.get_neighbors(service_id, RelationTypes.SERVICE_REQUIRES_ENVVAR)
        result["graph_operations"].append(f"Query: get_neighbors({service_id}, {RelationTypes.SERVICE_REQUIRES_ENVVAR})")
        
        missing_vars = []
        present_vars = []
        
        for envvar in required_envvars:
            var_name = envvar.props.get("key")
            if envvar.props.get("value") or envvar.props.get("is_set"):
                present_vars.append(var_name)
            else:
                missing_vars.append({
                    "key": var_name,
                    "node_id": envvar.id,
                    "required_by": service_name
                })
        
        if missing_vars:
            result["answer"] = f"Service {service_name} is missing {len(missing_vars)} environment variables"
            result["evidence"] = missing_vars
        else:
            result["answer"] = f"All required environment variables are present for {service_name}"
            result["evidence"] = [{"present_vars": present_vars}]
        
        return result
    
    def _find_related_incidents(self, service_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Find incidents related to rollout risks."""
        related_incidents = []
        
        if service_name:
            service_id = f"svc:{service_name}"
            
            # Direct incident impacts (incoming edges to the service)
            for edge in self.graph.edges:
                if (edge.type == RelationTypes.INCIDENT_IMPACTS_SERVICE and 
                    edge.to_id == service_id):
                    incident_node = self.graph.get_node(edge.from_id)
                    if incident_node:
                        related_incidents.append({
                            "incident_id": incident_node.props.get("id"),
                            "relationship": "directly_impacts_service",
                            "node_id": incident_node.id
                        })
            
            result["graph_operations"].append(f"Direct incidents affecting {service_name}: {len(related_incidents)}")
            
            # Multi-hop: incidents affecting required env vars
            required_envvars = self.graph.get_neighbors(service_id, RelationTypes.SERVICE_REQUIRES_ENVVAR)
            
            for envvar in required_envvars:
                envvar_key = envvar.props.get("key")
                # Check if any incidents mention this env var in their context
                all_incidents = self.graph.get_nodes_by_type(EntityTypes.INCIDENT)
                
                for incident in all_incidents:
                    incident_text = incident.props.get("extracted_from", "")
                    if envvar_key and envvar_key in incident_text:
                        # Avoid duplicates
                        existing_ids = [inc["incident_id"] for inc in related_incidents]
                        if incident.props.get("id") not in existing_ids:
                            related_incidents.append({
                                "incident_id": incident.props.get("id"),
                                "relationship": f"mentions_required_envvar_{envvar_key}",
                                "node_id": incident.id
                            })
        else:
            # If no specific service, look for any incidents that might affect rollouts
            all_incidents = self.graph.get_nodes_by_type(EntityTypes.INCIDENT)
            for incident in all_incidents:
                related_incidents.append({
                    "incident_id": incident.props.get("id"),
                    "relationship": "potential_rollout_risk",
                    "node_id": incident.id
                })
        
        result["graph_operations"].append(f"Multi-hop analysis found {len(related_incidents)} total related incidents")
        
        if related_incidents:
            result["answer"] = f"Found {len(related_incidents)} incidents related to rollout risks"
            result["evidence"] = related_incidents
        else:
            result["answer"] = "No incidents found related to current rollout risks"
        
        return result
    
    def _analyze_service_dependencies(self, service_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze what a service depends on."""
        if not service_name:
            result["answer"] = "No service specified in query"
            return result
        
        service_id = f"svc:{service_name}"
        dependencies = []
        
        # Environment variable dependencies
        required_envvars = self.graph.get_neighbors(service_id, RelationTypes.SERVICE_REQUIRES_ENVVAR)
        for envvar in required_envvars:
            dependencies.append({
                "type": "environment_variable",
                "name": envvar.props.get("key"),
                "node_id": envvar.id
            })
        
        result["answer"] = f"Service {service_name} has {len(dependencies)} dependencies"
        result["evidence"] = dependencies
        result["graph_operations"].append(f"Analyzed dependencies for {service_name}")
        
        return result
    
    def _analyze_incident_impact(self, query: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze what services are impacted by an incident.""" 
        # Extract incident ID from query
        import re
        incident_matches = re.findall(r'(INC-\d+|#?\d+)', query)
        
        if not incident_matches:
            result["answer"] = "No incident ID found in query"
            return result
        
        incident_id = incident_matches[0]
        inc_node_id = f"inc:{incident_id}"
        
        incident_node = self.graph.get_node(inc_node_id)
        if not incident_node:
            result["answer"] = f"Incident {incident_id} not found in memory graph"
            return result
        
        impacted_services = self.graph.get_neighbors(inc_node_id, RelationTypes.INCIDENT_IMPACTS_SERVICE)
        
        impacts = []
        for service in impacted_services:
            impacts.append({
                "service_name": service.props.get("name"),
                "node_id": service.id
            })
        
        result["answer"] = f"Incident {incident_id} impacts {len(impacts)} services"
        result["evidence"] = impacts
        result["graph_operations"].append(f"Analyzed impact of incident {incident_id}")
        
        return result
    
    def _analyze_resource_impact(self, query: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze what services might be affected if a resource goes down."""
        import re
        
        # Extract resource name from query (e.g., Redis, DATABASE, etc.)
        resource_patterns = [
            r'if\s+([A-Za-z_]+)\s+goes down',
            r'([A-Za-z_]+)\s+goes down',
            r'affected by\s+([A-Za-z_]+)',
        ]
        
        resource_name = None
        for pattern in resource_patterns:
            matches = re.search(pattern, query, re.IGNORECASE)
            if matches:
                resource_name = matches.group(1).upper()
                break
        
        if not resource_name:
            result["answer"] = "Could not identify resource in query"
            return result
        
        result["graph_operations"].append(f"Searching for services dependent on {resource_name}")
        
        # Find all env vars that contain this resource name
        all_envvars = self.graph.get_nodes_by_type(EntityTypes.ENVVAR)
        related_envvars = [
            env for env in all_envvars 
            if resource_name.lower() in env.props.get("key", "").lower()
        ]
        
        result["graph_operations"].append(f"Found {len(related_envvars)} env vars related to {resource_name}")
        
        # Find services that depend on these env vars
        affected_services = []
        service_names = set()
        
        for envvar in related_envvars:
            # Look for services that require this env var (incoming edges)
            for edge in self.graph.edges:
                if (edge.type == RelationTypes.SERVICE_REQUIRES_ENVVAR and 
                    edge.to_id == envvar.id):
                    service_node = self.graph.get_node(edge.from_id)
                    if service_node:
                        service_name = service_node.props.get("name")
                        if service_name not in service_names:
                            service_names.add(service_name)
                            affected_services.append({
                                "type": "service_dependency",
                                "description": f"Service {service_name} depends on {envvar.props.get('key')}",
                                "service_name": service_name,
                                "env_var": envvar.props.get("key"),
                                "node_id": service_node.id
                            })
        
        if affected_services:
            result["answer"] = f"If {resource_name} goes down, {len(affected_services)} service(s) could be affected"
            result["evidence"] = affected_services
        else:
            result["answer"] = f"No services found that directly depend on {resource_name}"
            result["evidence"] = []
        
        return result
    
    def _show_all_dependencies(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Show all environment variable dependencies across all services."""
        all_services = self.graph.get_nodes_by_type(EntityTypes.SERVICE)
        
        dependencies = []
        
        for service in all_services:
            service_name = service.props.get("name")
            required_envvars = self.graph.get_neighbors(service.id, RelationTypes.SERVICE_REQUIRES_ENVVAR)
            
            for envvar in required_envvars:
                dependencies.append({
                    "type": "service_envvar_dependency",
                    "description": f"{service_name} requires {envvar.props.get('key')}",
                    "service_name": service_name,
                    "env_var": envvar.props.get("key"),
                    "service_id": service.id,
                    "envvar_id": envvar.id
                })
        
        result["graph_operations"].append(f"Analyzed {len(all_services)} services")
        result["answer"] = f"Found {len(dependencies)} environment variable dependencies across {len(all_services)} services"
        result["evidence"] = dependencies
        
        return result
    
    def _analyze_service_risks(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze which services have the most dependencies and highest risk."""
        all_services = self.graph.get_nodes_by_type(EntityTypes.SERVICE)
        
        service_risks = []
        
        for service in all_services:
            service_name = service.props.get("name")
            
            # Count dependencies
            required_envvars = self.graph.get_neighbors(service.id, RelationTypes.SERVICE_REQUIRES_ENVVAR)
            dependency_count = len(required_envvars)
            
            # Count incidents
            incident_count = 0
            for edge in self.graph.edges:
                if (edge.type == RelationTypes.INCIDENT_IMPACTS_SERVICE and 
                    edge.to_id == service.id):
                    incident_count += 1
            
            # Calculate risk score (simple heuristic)
            risk_score = dependency_count + (incident_count * 2)
            
            if dependency_count > 0 or incident_count > 0:
                service_risks.append({
                    "type": "service_risk_assessment",
                    "description": f"{service_name}: {dependency_count} dependencies, {incident_count} incidents (risk score: {risk_score})",
                    "service_name": service_name,
                    "dependency_count": dependency_count,
                    "incident_count": incident_count,
                    "risk_score": risk_score,
                    "node_id": service.id
                })
        
        # Sort by risk score (highest first)
        service_risks.sort(key=lambda x: x["risk_score"], reverse=True)
        
        result["graph_operations"].append(f"Analyzed risk for {len(all_services)} services")
        
        if service_risks:
            highest_risk = service_risks[0]
            result["answer"] = f"Highest risk service: {highest_risk['service_name']} with risk score {highest_risk['risk_score']}"
            result["evidence"] = service_risks
        else:
            result["answer"] = "No services with dependencies or incidents found"
            result["evidence"] = []
        
        return result