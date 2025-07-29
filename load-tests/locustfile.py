"""
Z2 Platform Load Testing with Locust

This module provides comprehensive load testing scenarios for the Z2 AI Workforce Platform.
Tests include API endpoints, authentication, agent operations, and workflow executions.
"""

import random
import time
from locust import HttpUser, TaskSet, task, between
import json
import uuid


class AuthenticationTasks(TaskSet):
    """Authentication and user management load tests."""
    
    def on_start(self):
        """Setup test user credentials."""
        self.test_user = {
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPassword123!",
            "full_name": "Load Test User"
        }
        self.access_token = None
    
    @task(1)
    def register_user(self):
        """Test user registration endpoint."""
        response = self.client.post("/api/v1/auth/register", 
                                   json=self.test_user)
        if response.status_code == 201:
            self.access_token = response.json().get("access_token")
    
    @task(3)
    def login_user(self):
        """Test user login endpoint."""
        if not self.access_token:
            login_data = {
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
            response = self.client.post("/api/v1/auth/login", 
                                       json=login_data)
            if response.status_code == 200:
                self.access_token = response.json().get("access_token")
    
    @task(2)
    def get_current_user(self):
        """Test getting current user info."""
        if self.access_token:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            self.client.get("/api/v1/auth/me", headers=headers)


class AgentTasks(TaskSet):
    """Agent operations load tests."""
    
    def on_start(self):
        """Setup authentication for agent tests."""
        self.access_token = self.authenticate()
        self.agent_ids = []
    
    def authenticate(self):
        """Helper method to authenticate and get access token."""
        user_data = {
            "email": f"agent_test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPassword123!",
            "full_name": "Agent Test User"
        }
        
        # Register user
        response = self.client.post("/api/v1/auth/register", json=user_data)
        if response.status_code == 201:
            return response.json().get("access_token")
        
        # Try login if registration fails
        login_data = {"email": user_data["email"], "password": user_data["password"]}
        response = self.client.post("/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json().get("access_token")
        
        return None
    
    @task(2)
    def list_agents(self):
        """Test listing agents."""
        if self.access_token:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            self.client.get("/api/v1/agents", headers=headers)
    
    @task(1)
    def create_agent(self):
        """Test creating a new agent."""
        if self.access_token:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            agent_data = {
                "name": f"Test Agent {uuid.uuid4().hex[:8]}",
                "description": "Load test agent",
                "role": "assistant",
                "capabilities": ["text_processing", "data_analysis"],
                "model": "openai/gpt-4o-mini",
                "config": {
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            }
            response = self.client.post("/api/v1/agents", 
                                       json=agent_data, headers=headers)
            if response.status_code == 201:
                agent_id = response.json().get("id")
                if agent_id:
                    self.agent_ids.append(agent_id)
    
    @task(1)
    def get_agent_details(self):
        """Test getting agent details."""
        if self.access_token and self.agent_ids:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            agent_id = random.choice(self.agent_ids)
            self.client.get(f"/api/v1/agents/{agent_id}", headers=headers)


class WorkflowTasks(TaskSet):
    """Workflow operations load tests."""
    
    def on_start(self):
        """Setup authentication for workflow tests."""
        self.access_token = self.authenticate()
        self.workflow_ids = []
    
    def authenticate(self):
        """Helper method to authenticate and get access token."""
        user_data = {
            "email": f"workflow_test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPassword123!",
            "full_name": "Workflow Test User"
        }
        
        response = self.client.post("/api/v1/auth/register", json=user_data)
        if response.status_code == 201:
            return response.json().get("access_token")
        
        login_data = {"email": user_data["email"], "password": user_data["password"]}
        response = self.client.post("/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json().get("access_token")
        
        return None
    
    @task(2)
    def list_workflows(self):
        """Test listing workflows."""
        if self.access_token:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            self.client.get("/api/v1/workflows", headers=headers)
    
    @task(1)
    def create_workflow(self):
        """Test creating a new workflow."""
        if self.access_token:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            workflow_data = {
                "name": f"Test Workflow {uuid.uuid4().hex[:8]}",
                "description": "Load test workflow",
                "steps": [
                    {
                        "name": "Step 1",
                        "agent_role": "assistant",
                        "task": "Analyze the input data",
                        "model": "openai/gpt-4o-mini"
                    }
                ],
                "config": {
                    "max_agents": 3,
                    "timeout_seconds": 300
                }
            }
            response = self.client.post("/api/v1/workflows", 
                                       json=workflow_data, headers=headers)
            if response.status_code == 201:
                workflow_id = response.json().get("id")
                if workflow_id:
                    self.workflow_ids.append(workflow_id)


class HealthCheckTasks(TaskSet):
    """Health and monitoring endpoint tests."""
    
    @task(5)
    def health_check(self):
        """Test general health endpoint."""
        self.client.get("/health")
    
    @task(3)
    def liveness_probe(self):
        """Test Kubernetes liveness probe."""
        self.client.get("/health/live")
    
    @task(3)
    def readiness_probe(self):
        """Test Kubernetes readiness probe."""
        self.client.get("/health/ready")
    
    @task(2)
    def metrics_endpoint(self):
        """Test Prometheus metrics endpoint."""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Metrics endpoint failed: {response.status_code}")
    
    @task(1)
    def json_metrics(self):
        """Test JSON metrics endpoint."""
        self.client.get("/metrics/json")


class ApiUser(HttpUser):
    """Main user class for load testing the Z2 API."""
    
    # Wait time between tasks (1-5 seconds)
    wait_time = between(1, 5)
    
    # Define task sets with weights
    tasks = {
        HealthCheckTasks: 30,
        AuthenticationTasks: 25,
        AgentTasks: 25,
        WorkflowTasks: 20
    }
    
    def on_start(self):
        """Setup for each user."""
        # Test basic connectivity
        response = self.client.get("/health/live")
        if response.status_code != 200:
            print(f"Warning: Health check failed with status {response.status_code}")


class HighLoadUser(HttpUser):
    """High-load user for stress testing."""
    
    wait_time = between(0.1, 1)  # Faster requests
    
    tasks = {
        HealthCheckTasks: 50,
        AuthenticationTasks: 30,
        AgentTasks: 20
    }


class BurstUser(HttpUser):
    """Burst traffic user for spike testing."""
    
    wait_time = between(0, 0.5)  # Very fast requests
    
    tasks = {
        HealthCheckTasks: 70,
        AuthenticationTasks: 30
    }