"""
HorseClaw - Main Agent Class
HorseClaw - 主代理类

The autonomous AI agent that manages token budgets for Moltbook.
管理 Moltbook 代币预算的自主 AI 代理。
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from .agent_registry import AgentRegistry, Agent, create_default_registry
from .transaction_logger import TransactionLogger, TransactionType, TransactionStatus


class ModelType(Enum):
    """Supported AI models."""
    CLAUDE = "claude"
    KIMI = "kimi"


class Priority(Enum):
    """Request priority levels."""
    NORMAL = "normal"
    HIGH = "high"


@dataclass
class TokenPool:
    """Represents the current token pool."""
    claude_tokens: int = 0
    kimi_tokens: int = 0
    usd_balance: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def total_value_usd(self) -> float:
        """Calculate total value in USD."""
        claude_value = self.claude_tokens / 20000  # $1 = 20k tokens
        kimi_value = self.kimi_tokens / 40000      # $1 = 40k tokens
        return self.usd_balance + claude_value + kimi_value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "claude_tokens": self.claude_tokens,
            "kimi_tokens": self.kimi_tokens,
            "usd_balance": round(self.usd_balance, 2),
            "last_updated": self.last_updated.isoformat(),
            "total_value_usd": round(self.total_value_usd(), 2)
        }


@dataclass 
class FeePayment:
    """Represents a fee payment received."""
    source: str
    amount: float
    currency: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "amount": self.amount,
            "currency": self.currency,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class TokenRequest:
    """Represents an agent's request for tokens."""
    agent_id: str
    requested_tokens: int
    model: ModelType
    priority: Priority = Priority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "requested_tokens": self.requested_tokens,
            "model": self.model.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class AllocationResult:
    """Result of a token allocation request."""
    agent_id: str
    model: str
    tokens_allocated: int
    status: str  # "approved", "partial", "rejected"
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "model": self.model,
            "tokens_allocated": self.tokens_allocated,
            "status": self.status,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat()
        }


class HorseClaw:
    """
    Main HorseClaw agent class.
    
    Manages:
    - Fee collection
    - Token conversion (USD -> Claude/Kimi tokens)
    - Token allocation to agents
    - Safety rules and limits
    - State persistence
    
    Safety Rules:
    1. Never allow negative balances
    2. Max 30% allocation per request (50% for high priority)
    3. Always keep 10% reserve
    4. One request = one response (no infinite loops)
    5. Reset to last valid state on error
    """
    
    # Pricing constants
    CLAUDE_RATE = 20000  # $1 = 20,000 tokens
    KIMI_RATE = 40000    # $1 = 40,000 tokens
    
    # Allocation rules
    MAX_ALLOCATION_PERCENT = 0.30      # 30% for normal priority
    MAX_ALLOCATION_HIGH_PRIORITY = 0.50  # 50% for high priority
    RESERVE_PERCENT = 0.10             # 10% reserve
    
    def __init__(self, registry: Optional[AgentRegistry] = None):
        """Initialize HorseClaw agent."""
        self.registry = registry or create_default_registry()
        self.logger = TransactionLogger()
        self.token_pool = TokenPool()
        self._last_valid_state: Optional[Dict[str, Any]] = None
        self._save_state()
    
    # ==================== FEE COLLECTION ====================
    
    def collect_fee(self, source: str, amount: float, currency: str = "USD") -> Dict[str, Any]:
        """
        Collect a fee payment from an agent.
        
        Args:
            source: Name of the paying agent/system
            amount: Amount paid
            currency: Currency code (default USD)
            
        Returns:
            Result dictionary with status and new balance
        """
        try:
            # Validate input
            if amount <= 0:
                raise ValueError("Fee amount must be positive")
            
            # Record payment
            payment = FeePayment(
                source=source,
                amount=amount,
                currency=currency
            )
            
            # Update USD balance
            self.token_pool.usd_balance += amount
            self.token_pool.last_updated = datetime.now()
            
            # Log transaction
            self.logger.log(
                tx_type=TransactionType.FEE_RECEIVED,
                amount=amount,
                currency=currency,
                metadata={"source": source}
            )
            
            self._save_state()
            
            return {
                "status": "success",
                "message": f"Fee collected: {amount} {currency}",
                "new_balance_usd": round(self.token_pool.usd_balance, 2),
                "total_pool_value": round(self.token_pool.total_value_usd(), 2)
            }
            
        except Exception as e:
            self._restore_state()
            return {
                "status": "error",
                "message": str(e)
            }
    
    # ==================== TOKEN CONVERSION ====================
    
    def convert_fees_to_tokens(self) -> Dict[str, Any]:
        """
        Convert all USD balance to Claude and Kimi tokens.
        Uses fixed pricing rates.
        
        Returns:
            Result with conversion details
        """
        try:
            if self.token_pool.usd_balance <= 0:
                return {
                    "status": "error",
                    "message": "No USD balance to convert"
                }
            
            usd_amount = self.token_pool.usd_balance
            
            # Split 50/50 between Claude and Kimi
            claude_usd = usd_amount * 0.5
            kimi_usd = usd_amount * 0.5
            
            # Calculate tokens
            claude_tokens = int(claude_usd * self.CLAUDE_RATE)
            kimi_tokens = int(kimi_usd * self.KIMI_RATE)
            
            # Update pool
            self.token_pool.claude_tokens += claude_tokens
            self.token_pool.kimi_tokens += kimi_tokens
            self.token_pool.usd_balance = 0.0
            self.token_pool.last_updated = datetime.now()
            
            # Log conversion
            self.logger.log(
                tx_type=TransactionType.TOKEN_CONVERTED,
                amount=usd_amount,
                currency="USD",
                metadata={
                    "claude_tokens": claude_tokens,
                    "kimi_tokens": kimi_tokens,
                    "split_ratio": "50/50"
                }
            )
            
            self._save_state()
            
            return {
                "status": "success",
                "message": "Fees converted to tokens",
                "conversion": {
                    "usd_amount": round(usd_amount, 2),
                    "claude_tokens": claude_tokens,
                    "kimi_tokens": kimi_tokens
                },
                "new_pool": self.token_pool.to_dict()
            }
            
        except Exception as e:
            self._restore_state()
            return {
                "status": "error",
                "message": str(e)
            }
    
    # ==================== ALLOCATION ENGINE ====================
    
    def request_tokens(self, 
                      agent_id: str, 
                      requested_tokens: int, 
                      model: str,
                      priority: str = "normal") -> AllocationResult:
        """
        Process a token allocation request from an agent.
        
        Args:
            agent_id: Requesting agent's ID
            requested_tokens: Number of tokens requested
            model: "claude" or "kimi"
            priority: "normal" or "high"
            
        Returns:
            AllocationResult with status and details
        """
        try:
            # Validate request
            if requested_tokens <= 0:
                return AllocationResult(
                    agent_id=agent_id,
                    model=model,
                    tokens_allocated=0,
                    status="rejected",
                    reason="Invalid token amount"
                )
            
            # Check if agent is registered
            if not self.registry.is_registered(agent_id):
                return AllocationResult(
                    agent_id=agent_id,
                    model=model,
                    tokens_allocated=0,
                    status="rejected",
                    reason="Agent not registered"
                )
            
            # Parse model and priority
            try:
                model_type = ModelType(model.lower())
                priority_type = Priority(priority.lower())
            except ValueError:
                return AllocationResult(
                    agent_id=agent_id,
                    model=model,
                    tokens_allocated=0,
                    status="rejected",
                    reason="Invalid model or priority"
                )
            
            # Get available tokens for this model
            if model_type == ModelType.CLAUDE:
                available = self.token_pool.claude_tokens
            else:
                available = self.token_pool.kimi_tokens
            
            # Calculate reserve requirement (10% of total)
            total_pool = self.token_pool.claude_tokens + self.token_pool.kimi_tokens
            reserve = int(total_pool * self.RESERVE_PERCENT)
            allocatable = max(0, available - reserve)
            
            if allocatable <= 0:
                # Log and return rejection
                self.logger.log(
                    tx_type=TransactionType.TOKEN_ALLOCATED,
                    agent_id=agent_id,
                    tokens_allocated=0,
                    model=model,
                    status=TransactionStatus.REJECTED,
                    error_message="Insufficient tokens (reserve requirement)"
                )
                
                return AllocationResult(
                    agent_id=agent_id,
                    model=model,
                    tokens_allocated=0,
                    status="rejected",
                    reason="Insufficient tokens (reserve requirement)"
                )
            
            # Determine max allocation based on priority
            if priority_type == Priority.HIGH:
                max_allocation = int(available * self.MAX_ALLOCATION_HIGH_PRIORITY)
            else:
                max_allocation = int(available * self.MAX_ALLOCATION_PERCENT)
            
            # Apply limits
            max_allocation = min(max_allocation, allocatable)
            
            # Calculate final allocation
            if requested_tokens <= max_allocation:
                allocated = requested_tokens
                status = "approved"
                reason = "Full allocation approved"
            else:
                allocated = max_allocation
                status = "partial"
                reason = f"Partial allocation: max {self.MAX_ALLOCATION_PERCENT*100:.0f}% for {priority} priority"
            
            # Update token pool
            if model_type == ModelType.CLAUDE:
                self.token_pool.claude_tokens -= allocated
            else:
                self.token_pool.kimi_tokens -= allocated
            
            self.token_pool.last_updated = datetime.now()
            
            # Log transaction
            tx_status = TransactionStatus.APPROVED if status == "approved" else TransactionStatus.PARTIAL
            self.logger.log(
                tx_type=TransactionType.TOKEN_ALLOCATED,
                agent_id=agent_id,
                tokens_allocated=allocated,
                model=model,
                status=tx_status,
                metadata={
                    "requested": requested_tokens,
                    "priority": priority,
                    "max_allowed": max_allocation
                }
            )
            
            self._save_state()
            
            return AllocationResult(
                agent_id=agent_id,
                model=model,
                tokens_allocated=allocated,
                status=status,
                reason=reason
            )
            
        except Exception as e:
            self._restore_state()
            return AllocationResult(
                agent_id=agent_id,
                model=model,
                tokens_allocated=0,
                status="rejected",
                reason=f"System error: {str(e)}"
            )
    
    # ==================== STATE MANAGEMENT ====================
    
    def _save_state(self):
        """Save current state as last valid state."""
        self._last_valid_state = self.to_dict()
    
    def _restore_state(self):
        """Restore to last valid state after error."""
        if self._last_valid_state:
            self.from_dict(self._last_valid_state)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export full state to dictionary."""
        return {
            "token_pool": self.token_pool.to_dict(),
            "registry": self.registry.to_dict(),
            "logger": self.logger.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Restore state from dictionary."""
        if "token_pool" in data:
            pool_data = data["token_pool"]
            self.token_pool = TokenPool(
                claude_tokens=pool_data.get("claude_tokens", 0),
                kimi_tokens=pool_data.get("kimi_tokens", 0),
                usd_balance=pool_data.get("usd_balance", 0.0),
                last_updated=datetime.fromisoformat(pool_data.get("last_updated", datetime.now().isoformat()))
            )
        
        if "registry" in data:
            self.registry = AgentRegistry.from_dict(data["registry"])
        
        if "logger" in data:
            self.logger = TransactionLogger.from_dict(data["logger"])
    
    def save_to_file(self, filepath: str):
        """Save state to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, filepath: str):
        """Load state from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.from_dict(data)
        self._save_state()
    
    # ==================== STATUS & REPORTING ====================
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "status": "active",
            "token_pool": self.token_pool.to_dict(),
            "agents": {
                "total": self.registry.get_agent_count(active_only=False),
                "active": self.registry.get_agent_count(active_only=True)
            },
            "transactions": self.logger.get_stats(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_pool_breakdown(self) -> Dict[str, Any]:
        """Get detailed breakdown of token pool."""
        total = self.token_pool.claude_tokens + self.token_pool.kimi_tokens
        
        return {
            "claude": {
                "tokens": self.token_pool.claude_tokens,
                "usd_value": round(self.token_pool.claude_tokens / self.CLAUDE_RATE, 2),
                "percentage": round((self.token_pool.claude_tokens / total * 100), 2) if total > 0 else 0
            },
            "kimi": {
                "tokens": self.token_pool.kimi_tokens,
                "usd_value": round(self.token_pool.kimi_tokens / self.KIMI_RATE, 2),
                "percentage": round((self.token_pool.kimi_tokens / total * 100), 2) if total > 0 else 0
            },
            "usd_balance": round(self.token_pool.usd_balance, 2),
            "total_usd_value": round(self.token_pool.total_value_usd(), 2),
            "reserve_requirement": round(total * self.RESERVE_PERCENT)
        }
