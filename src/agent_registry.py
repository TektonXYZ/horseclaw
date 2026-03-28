"""
Agent Registry Module
代理注册表模块

Manages registered agents in the HorseClaw system.
管理 HorseClaw 系统中的已注册代理。
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Agent:
    """Represents a registered agent in the system."""
    agent_id: str
    name: str
    registered_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "registered_at": self.registered_at.isoformat(),
            "is_active": self.is_active,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create agent from dictionary."""
        return cls(
            agent_id=data["agent_id"],
            name=data["name"],
            registered_at=datetime.fromisoformat(data["registered_at"]),
            is_active=data.get("is_active", True),
            metadata=data.get("metadata", {})
        )


class AgentRegistry:
    """
    Manages the registry of all agents in the HorseClaw system.
    
    Features:
    - Register new agents
    - Check if agent is registered
    - Get list of all agents
    - Activate/deactivate agents
    - Persist registry state
    """
    
    def __init__(self):
        """Initialize empty agent registry."""
        self._agents: Dict[str, Agent] = {}
        self._history: List[Dict[str, Any]] = []
    
    def register(self, agent_id: str, name: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a new agent in the system.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            metadata: Optional additional information
            
        Returns:
            True if registration successful, False if agent already exists
        """
        if agent_id in self._agents:
            return False
        
        agent = Agent(
            agent_id=agent_id,
            name=name,
            metadata=metadata or {}
        )
        
        self._agents[agent_id] = agent
        self._log_event("REGISTER", agent_id, f"Agent {name} registered")
        
        return True
    
    def is_registered(self, agent_id: str) -> bool:
        """
        Check if an agent is registered and active.
        
        Args:
            agent_id: Agent identifier to check
            
        Returns:
            True if agent exists and is active
        """
        if agent_id not in self._agents:
            return False
        return self._agents[agent_id].is_active
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent object if found, None otherwise
        """
        return self._agents.get(agent_id)
    
    def get_all_agents(self, active_only: bool = True) -> List[Agent]:
        """
        Get list of all registered agents.
        
        Args:
            active_only: If True, return only active agents
            
        Returns:
            List of Agent objects
        """
        agents = list(self._agents.values())
        if active_only:
            agents = [a for a in agents if a.is_active]
        return agents
    
    def deactivate(self, agent_id: str) -> bool:
        """
        Deactivate an agent (soft delete).
        
        Args:
            agent_id: Agent to deactivate
            
        Returns:
            True if deactivated, False if not found
        """
        if agent_id not in self._agents:
            return False
        
        self._agents[agent_id].is_active = False
        self._log_event("DEACTIVATE", agent_id, "Agent deactivated")
        
        return True
    
    def activate(self, agent_id: str) -> bool:
        """
        Activate a previously deactivated agent.
        
        Args:
            agent_id: Agent to activate
            
        Returns:
            True if activated, False if not found
        """
        if agent_id not in self._agents:
            return False
        
        self._agents[agent_id].is_active = True
        self._log_event("ACTIVATE", agent_id, "Agent activated")
        
        return True
    
    def unregister(self, agent_id: str) -> bool:
        """
        Permanently remove an agent from registry.
        
        Args:
            agent_id: Agent to remove
            
        Returns:
            True if removed, False if not found
        """
        if agent_id not in self._agents:
            return False
        
        del self._agents[agent_id]
        self._log_event("UNREGISTER", agent_id, "Agent unregistered")
        
        return True
    
    def get_agent_count(self, active_only: bool = True) -> int:
        """
        Get count of registered agents.
        
        Args:
            active_only: Count only active agents
            
        Returns:
            Number of agents
        """
        if active_only:
            return len([a for a in self._agents.values() if a.is_active])
        return len(self._agents)
    
    def _log_event(self, event_type: str, agent_id: str, message: str):
        """Log registry events."""
        self._history.append({
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "agent_id": agent_id,
            "message": message
        })
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get registry event history."""
        return self._history.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export registry to dictionary."""
        return {
            "agents": {aid: agent.to_dict() for aid, agent in self._agents.items()},
            "history": self._history,
            "total_agents": len(self._agents),
            "active_agents": len([a for a in self._agents.values() if a.is_active])
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentRegistry':
        """Restore registry from dictionary."""
        registry = cls()
        
        for agent_id, agent_data in data.get("agents", {}).items():
            registry._agents[agent_id] = Agent.from_dict(agent_data)
        
        registry._history = data.get("history", [])
        
        return registry


# Convenience functions for quick usage
def create_default_registry() -> AgentRegistry:
    """Create registry with default Moltbook agents."""
    registry = AgentRegistry()
    
    # Register default system agents
    default_agents = [
        ("system_orchestrator", "System Orchestrator"),
        ("market_analyzer", "Market Analyzer"),
        ("risk_manager", "Risk Manager"),
        ("execution_engine", "Execution Engine"),
        ("reporting_module", "Reporting Module"),
    ]
    
    for agent_id, name in default_agents:
        registry.register(agent_id, name, {"type": "system", "tier": "core"})
    
    return registry
