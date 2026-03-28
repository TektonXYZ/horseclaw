"""
Allocation Engine Module
分配引擎模块

Processes token allocation requests with safety rules.
根据安全规则处理代币分配请求。
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum


class AllocationStatus(Enum):
    """Status of allocation requests."""
    APPROVED = "approved"
    PARTIAL = "partial"
    REJECTED = "rejected"
    PENDING = "pending"


class Priority(Enum):
    """Priority levels for allocation requests."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AllocationRequest:
    """Represents a token allocation request from an agent."""
    request_id: str
    agent_id: str
    model: str  # "claude" or "kimi"
    tokens_requested: int
    priority: Priority
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "request_id": self.request_id,
            "agent_id": self.agent_id,
            "model": self.model,
            "tokens_requested": self.tokens_requested,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class AllocationResponse:
    """Response to an allocation request."""
    request_id: str
    status: AllocationStatus
    tokens_granted: int
    tokens_requested: int
    reason: str
    remaining_pool: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "request_id": self.request_id,
            "status": self.status.value,
            "tokens_granted": self.tokens_granted,
            "tokens_requested": self.tokens_requested,
            "reason": self.reason,
            "remaining_pool": self.remaining_pool,
            "timestamp": self.timestamp.isoformat()
        }


class AllocationEngine:
    """
    Processes token allocation requests with safety rules.
    
    Safety Rules:
    1. Never negative balance
    2. 10% reserve requirement always maintained
    3. Max 30% of pool per request (50% for high priority)
    4. Partial allocation allowed if insufficient
    5. Reject unregistered agents
    
    Features:
    - Process allocation requests
    - Enforce safety rules
    - Track request history
    - Calculate maximum allowable allocations
    """
    
    # Allocation limits
    MAX_ALLOCATION_PERCENT = 0.30  # 30% for normal priority
    MAX_ALLOCATION_HIGH_PRIORITY = 0.50  # 50% for high/critical priority
    RESERVE_PERCENT = 0.10  # 10% reserve
    
    def __init__(self, token_converter=None, agent_registry=None):
        """
        Initialize allocation engine.
        
        Args:
            token_converter: TokenConverter instance
            agent_registry: AgentRegistry instance
        """
        self.token_converter = token_converter
        self.agent_registry = agent_registry
        self._request_history: List[Tuple[AllocationRequest, AllocationResponse]] = []
        self._request_counter: int = 0
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        self._request_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"REQ-{timestamp}-{self._request_counter:06d}"
    
    def _is_agent_registered(self, agent_id: str) -> bool:
        """Check if agent is registered."""
        if self.agent_registry is None:
            # If no registry set, allow all (for testing)
            return True
        return self.agent_registry.is_registered(agent_id)
    
    def _get_available_tokens(self, model: str) -> int:
        """Get available tokens for a model."""
        if self.token_converter is None:
            return 0
        pool = self.token_converter.get_pool(model)
        return pool.available_tokens
    
    def _calculate_max_allowable(self, available: int, priority: Priority) -> int:
        """
        Calculate maximum allowable allocation based on rules.
        
        Args:
            available: Total available tokens
            priority: Request priority level
            
        Returns:
            Maximum tokens that can be allocated
        """
        # Calculate reserve (must keep 10%)
        reserve = int(available * self.RESERVE_PERCENT)
        allocatable = available - reserve
        
        # Determine max percentage based on priority
        if priority in (Priority.HIGH, Priority.CRITICAL):
            max_percent = self.MAX_ALLOCATION_HIGH_PRIORITY
        else:
            max_percent = self.MAX_ALLOCATION_PERCENT
        
        max_allowable = int(allocatable * max_percent)
        
        return max(0, max_allowable)
    
    def request_allocation(self,
                          agent_id: str,
                          model: str,
                          tokens_requested: int,
                          priority: Priority = Priority.NORMAL,
                          metadata: Optional[Dict[str, Any]] = None) -> AllocationResponse:
        """
        Process a token allocation request.
        
        Args:
            agent_id: Requesting agent ID
            model: "claude" or "kimi"
            tokens_requested: Number of tokens requested
            priority: Priority level
            metadata: Additional request info
            
        Returns:
            AllocationResponse with result
        """
        # Create request object
        request = AllocationRequest(
            request_id=self._generate_request_id(),
            agent_id=agent_id,
            model=model.lower(),
            tokens_requested=tokens_requested,
            priority=priority,
            metadata=metadata or {}
        )
        
        # Rule 1: Check if agent is registered
        if not self._is_agent_registered(agent_id):
            response = AllocationResponse(
                request_id=request.request_id,
                status=AllocationStatus.REJECTED,
                tokens_granted=0,
                tokens_requested=tokens_requested,
                reason="Agent not registered",
                remaining_pool=self._get_available_tokens(model.lower())
            )
            self._request_history.append((request, response))
            return response
        
        # Get available tokens
        available = self._get_available_tokens(model.lower())
        
        # Rule 2: Check if we have any tokens
        if available <= 0:
            response = AllocationResponse(
                request_id=request.request_id,
                status=AllocationStatus.REJECTED,
                tokens_granted=0,
                tokens_requested=tokens_requested,
                reason="No tokens available in pool",
                remaining_pool=0
            )
            self._request_history.append((request, response))
            return response
        
        # Calculate maximum allowable
        max_allowable = self._calculate_max_allowable(available, priority)
        
        # Rule 3: Check if request exceeds maximum allowable
        if tokens_requested > max_allowable:
            # Offer partial allocation
            if max_allowable > 0:
                response = AllocationResponse(
                    request_id=request.request_id,
                    status=AllocationStatus.PARTIAL,
                    tokens_granted=max_allowable,
                    tokens_requested=tokens_requested,
                    reason=f"Exceeds maximum allowable ({self.MAX_ALLOCATION_HIGH_PRIORITY*100:.0f}% for {priority.value} priority)",
                    remaining_pool=available - max_allowable
                )
            else:
                response = AllocationResponse(
                    request_id=request.request_id,
                    status=AllocationStatus.REJECTED,
                    tokens_granted=0,
                    tokens_requested=tokens_requested,
                    reason="Request exceeds available allocation limit",
                    remaining_pool=available
                )
            self._request_history.append((request, response))
            return response
        
        # Rule 4: Check if we have enough (after reserve)
        reserve = int(available * self.RESERVE_PERCENT)
        allocatable = available - reserve
        
        if tokens_requested > allocatable:
            # Offer what we can
            partial_amount = allocatable
            if partial_amount > 0:
                response = AllocationResponse(
                    request_id=request.request_id,
                    status=AllocationStatus.PARTIAL,
                    tokens_granted=partial_amount,
                    tokens_requested=tokens_requested,
                    reason="Insufficient tokens after reserve requirement",
                    remaining_pool=available - partial_amount
                )
            else:
                response = AllocationResponse(
                    request_id=request.request_id,
                    status=AllocationStatus.REJECTED,
                    tokens_granted=0,
                    tokens_requested=tokens_requested,
                    reason="Reserve requirement exceeds available tokens",
                    remaining_pool=available
                )
            self._request_history.append((request, response))
            return response
        
        # All checks passed - approve full request
        # Actually allocate the tokens
        if self.token_converter:
            success = self.token_converter.allocate_tokens(model.lower(), tokens_requested)
            if not success:
                response = AllocationResponse(
                    request_id=request.request_id,
                    status=AllocationStatus.REJECTED,
                    tokens_granted=0,
                    tokens_requested=tokens_requested,
                    reason="Token allocation failed",
                    remaining_pool=available
                )
                self._request_history.append((request, response))
                return response
        
        response = AllocationResponse(
            request_id=request.request_id,
            status=AllocationStatus.APPROVED,
            tokens_granted=tokens_requested,
            tokens_requested=tokens_requested,
            reason="Request approved",
            remaining_pool=available - tokens_requested
        )
        
        self._request_history.append((request, response))
        return response
    
    def get_request_history(self, 
                           agent_id: Optional[str] = None,
                           status: Optional[AllocationStatus] = None,
                           limit: Optional[int] = None) -> List[Tuple[AllocationRequest, AllocationResponse]]:
        """
        Get allocation request history.
        
        Args:
            agent_id: Filter by agent
            status: Filter by response status
            limit: Maximum number of results
            
        Returns:
            List of (request, response) tuples
        """
        results = self._request_history
        
        if agent_id:
            results = [(req, res) for req, res in results if req.agent_id == agent_id]
        
        if status:
            results = [(req, res) for req, res in results if res.status == status]
        
        # Sort by timestamp (most recent first)
        results = sorted(results, key=lambda x: x[0].timestamp, reverse=True)
        
        if limit:
            results = results[:limit]
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get allocation statistics."""
        total_requests = len(self._request_history)
        approved = sum(1 for _, res in self._request_history if res.status == AllocationStatus.APPROVED)
        partial = sum(1 for _, res in self._request_history if res.status == AllocationStatus.PARTIAL)
        rejected = sum(1 for _, res in self._request_history if res.status == AllocationStatus.REJECTED)
        
        total_granted = sum(res.tokens_granted for _, res in self._request_history)
        total_requested = sum(req.tokens_requested for req, _ in self._request_history)
        
        return {
            "total_requests": total_requests,
            "approved": approved,
            "partial": partial,
            "rejected": rejected,
            "total_tokens_granted": total_granted,
            "total_tokens_requested": total_requested,
            "fulfillment_rate": round(total_granted / total_requested, 4) if total_requested > 0 else 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Export engine state to dictionary."""
        return {
            "request_history": [
                {
                    "request": req.to_dict(),
                    "response": res.to_dict()
                }
                for req, res in self._request_history
            ],
            "request_counter": self._request_counter,
            "stats": self.get_stats()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], token_converter=None, agent_registry=None) -> 'AllocationEngine':
        """Restore engine from dictionary."""
        engine = cls(token_converter, agent_registry)
        
        for item in data.get("request_history", []):
            req_data = item["request"]
            res_data = item["response"]
            
            request = AllocationRequest(
                request_id=req_data["request_id"],
                agent_id=req_data["agent_id"],
                model=req_data["model"],
                tokens_requested=req_data["tokens_requested"],
                priority=Priority(req_data["priority"]),
                timestamp=datetime.fromisoformat(req_data["timestamp"]),
                metadata=req_data.get("metadata", {})
            )
            
            response = AllocationResponse(
                request_id=res_data["request_id"],
                status=AllocationStatus(res_data["status"]),
                tokens_granted=res_data["tokens_granted"],
                tokens_requested=res_data["tokens_requested"],
                reason=res_data["reason"],
                remaining_pool=res_data["remaining_pool"],
                timestamp=datetime.fromisoformat(res_data["timestamp"])
            )
            
            engine._request_history.append((request, response))
        
        engine._request_counter = data.get("request_counter", 0)
        
        return engine
