"""
Token Converter Module
代币转换器模块

Converts USD fees into AI token budgets (Claude + Kimi).
将 USD 费用转换为 AI 代币预算 (Claude + Kimi)。
"""

from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


# Fixed pricing (do NOT call external APIs)
# 固定定价（不调用外部 API）
PRICING = {
    "claude": {
        "tokens_per_dollar": 20000,
        "model_name": "Claude",
        "description": "Anthropic Claude API"
    },
    "kimi": {
        "tokens_per_dollar": 40000,
        "model_name": "Kimi",
        "description": "Moonshot Kimi API"
    }
}


@dataclass
class TokenPool:
    """Represents the token pool for a specific model."""
    model: str
    total_tokens: int
    allocated_tokens: int
    available_tokens: int
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pool to dictionary."""
        return {
            "model": self.model,
            "total_tokens": self.total_tokens,
            "allocated_tokens": self.allocated_tokens,
            "available_tokens": self.available_tokens,
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class ConversionResult:
    """Result of a fee-to-tokens conversion."""
    conversion_id: str
    usd_amount: Decimal
    claude_tokens: int
    kimi_tokens: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "conversion_id": self.conversion_id,
            "usd_amount": str(self.usd_amount),
            "claude_tokens": self.claude_tokens,
            "kimi_tokens": self.kimi_tokens,
            "timestamp": self.timestamp.isoformat()
        }


class TokenConverter:
    """
    Converts USD fees into AI token budgets.
    
    Features:
    - Fixed pricing (no external API calls)
    - Maintain token pools for Claude and Kimi
    - Track conversion history
    - Support proportional allocation
    """
    
    def __init__(self):
        """Initialize token converter with empty pools."""
        self._pools: Dict[str, TokenPool] = {
            "claude": TokenPool(model="claude", total_tokens=0, allocated_tokens=0, available_tokens=0),
            "kimi": TokenPool(model="kimi", total_tokens=0, allocated_tokens=0, available_tokens=0)
        }
        self._conversion_history: list = []
        self._conversion_counter: int = 0
    
    def _generate_conversion_id(self) -> str:
        """Generate unique conversion ID."""
        self._conversion_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"CONV-{timestamp}-{self._conversion_counter:06d}"
    
    def convert(self, usd_amount: float, allocation: Optional[Dict[str, float]] = None) -> ConversionResult:
        """
        Convert USD to tokens.
        
        Args:
            usd_amount: Amount in USD to convert
            allocation: Optional allocation ratio (e.g., {"claude": 0.5, "kimi": 0.5})
                       If None, defaults to 50/50 split
        
        Returns:
            ConversionResult with token amounts
            
        Raises:
            ValueError: If amount is negative or allocation invalid
        """
        if usd_amount < 0:
            raise ValueError("USD amount cannot be negative")
        
        # Default 50/50 allocation
        if allocation is None:
            allocation = {"claude": 0.5, "kimi": 0.5}
        
        # Validate allocation sums to 1.0
        total_allocation = sum(allocation.values())
        if not 0.99 <= total_allocation <= 1.01:  # Allow small float errors
            raise ValueError(f"Allocation must sum to 1.0, got {total_allocation}")
        
        # Convert to Decimal for precision
        decimal_amount = Decimal(str(usd_amount)).quantize(Decimal('0.01'))
        
        # Calculate tokens for each model
        claude_tokens = 0
        kimi_tokens = 0
        
        if "claude" in allocation:
            claude_usd = decimal_amount * Decimal(str(allocation["claude"]))
            claude_tokens = int(claude_usd * PRICING["claude"]["tokens_per_dollar"])
        
        if "kimi" in allocation:
            kimi_usd = decimal_amount * Decimal(str(allocation["kimi"]))
            kimi_tokens = int(kimi_usd * PRICING["kimi"]["tokens_per_dollar"])
        
        # Create result
        result = ConversionResult(
            conversion_id=self._generate_conversion_id(),
            usd_amount=decimal_amount,
            claude_tokens=claude_tokens,
            kimi_tokens=kimi_tokens
        )
        
        # Update pools
        self._pools["claude"].total_tokens += claude_tokens
        self._pools["claude"].available_tokens += claude_tokens
        self._pools["claude"].last_updated = datetime.now()
        
        self._pools["kimi"].total_tokens += kimi_tokens
        self._pools["kimi"].available_tokens += kimi_tokens
        self._pools["kimi"].last_updated = datetime.now()
        
        # Store conversion
        self._conversion_history.append(result)
        
        return result
    
    def get_pool(self, model: str) -> TokenPool:
        """
        Get token pool for a specific model.
        
        Args:
            model: "claude" or "kimi"
            
        Returns:
            TokenPool object
        """
        model = model.lower()
        if model not in self._pools:
            raise ValueError(f"Unknown model: {model}. Supported: claude, kimi")
        return self._pools[model]
    
    def get_all_pools(self) -> Dict[str, TokenPool]:
        """Get all token pools."""
        return self._pools.copy()
    
    def get_total_tokens(self) -> Dict[str, int]:
        """
        Get total token counts.
        
        Returns:
            Dictionary with total, allocated, and available counts
        """
        return {
            "claude": {
                "total": self._pools["claude"].total_tokens,
                "allocated": self._pools["claude"].allocated_tokens,
                "available": self._pools["claude"].available_tokens
            },
            "kimi": {
                "total": self._pools["kimi"].total_tokens,
                "allocated": self._pools["kimi"].allocated_tokens,
                "available": self._pools["kimi"].available_tokens
            }
        }
    
    def allocate_tokens(self, model: str, amount: int) -> bool:
        """
        Mark tokens as allocated (called by allocation engine).
        
        Args:
            model: "claude" or "kimi"
            amount: Number of tokens to allocate
            
        Returns:
            True if successful, False if insufficient available tokens
        """
        model = model.lower()
        if model not in self._pools:
            return False
        
        pool = self._pools[model]
        
        if amount > pool.available_tokens:
            return False
        
        pool.allocated_tokens += amount
        pool.available_tokens -= amount
        pool.last_updated = datetime.now()
        
        return True
    
    def release_tokens(self, model: str, amount: int) -> bool:
        """
        Release allocated tokens back to available pool.
        
        Args:
            model: "claude" or "kimi"
            amount: Number of tokens to release
            
        Returns:
            True if successful, False if trying to release more than allocated
        """
        model = model.lower()
        if model not in self._pools:
            return False
        
        pool = self._pools[model]
        
        if amount > pool.allocated_tokens:
            return False
        
        pool.allocated_tokens -= amount
        pool.available_tokens += amount
        pool.last_updated = datetime.now()
        
        return True
    
    def get_pricing(self) -> Dict[str, Any]:
        """Get current pricing information."""
        return PRICING.copy()
    
    def estimate_conversion(self, usd_amount: float, allocation: Optional[Dict[str, float]] = None) -> Dict[str, int]:
        """
        Estimate token conversion without actually converting.
        
        Args:
            usd_amount: Amount in USD
            allocation: Optional allocation ratio
            
        Returns:
            Dictionary with estimated token amounts
        """
        if allocation is None:
            allocation = {"claude": 0.5, "kimi": 0.5}
        
        decimal_amount = Decimal(str(usd_amount))
        
        claude_tokens = 0
        kimi_tokens = 0
        
        if "claude" in allocation:
            claude_usd = decimal_amount * Decimal(str(allocation["claude"]))
            claude_tokens = int(claude_usd * PRICING["claude"]["tokens_per_dollar"])
        
        if "kimi" in allocation:
            kimi_usd = decimal_amount * Decimal(str(allocation["kimi"]))
            kimi_tokens = int(kimi_usd * PRICING["kimi"]["tokens_per_dollar"])
        
        return {
            "claude_tokens": claude_tokens,
            "kimi_tokens": kimi_tokens,
            "total_tokens": claude_tokens + kimi_tokens
        }
    
    def get_conversion_history(self, limit: Optional[int] = None) -> list:
        """
        Get conversion history.
        
        Args:
            limit: Maximum number of conversions to return
            
        Returns:
            List of ConversionResult objects
        """
        history = sorted(self._conversion_history, key=lambda x: x.timestamp, reverse=True)
        if limit:
            history = history[:limit]
        return history
    
    def to_dict(self) -> Dict[str, Any]:
        """Export converter state to dictionary."""
        return {
            "pools": {model: pool.to_dict() for model, pool in self._pools.items()},
            "conversion_history": [conv.to_dict() for conv in self._conversion_history],
            "conversion_counter": self._conversion_counter,
            "pricing": PRICING
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenConverter':
        """Restore converter from dictionary."""
        converter = cls()
        
        # Restore pools
        for model, pool_data in data.get("pools", {}).items():
            converter._pools[model] = TokenPool(
                model=pool_data["model"],
                total_tokens=pool_data["total_tokens"],
                allocated_tokens=pool_data["allocated_tokens"],
                available_tokens=pool_data["available_tokens"],
                last_updated=datetime.fromisoformat(pool_data["last_updated"])
            )
        
        # Restore history
        converter._conversion_history = [
            ConversionResult(
                conversion_id=conv["conversion_id"],
                usd_amount=Decimal(conv["usd_amount"]),
                claude_tokens=conv["claude_tokens"],
                kimi_tokens=conv["kimi_tokens"],
                timestamp=datetime.fromisoformat(conv["timestamp"])
            )
            for conv in data.get("conversion_history", [])
        ]
        
        converter._conversion_counter = data.get("conversion_counter", 0)
        
        return converter
