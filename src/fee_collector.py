"""
Fee Collector Module
费用收集器模块

Collects and manages fee payments from Moltbook agents.
收集并管理来自 Moltbook 代理的费用付款。
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import json


@dataclass
class FeePayment:
    """Represents a single fee payment."""
    payment_id: str
    source: str
    amount: Decimal
    currency: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert payment to dictionary."""
        return {
            "payment_id": self.payment_id,
            "source": self.source,
            "amount": str(self.amount),
            "currency": self.currency,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeePayment':
        """Create payment from dictionary."""
        return cls(
            payment_id=data["payment_id"],
            source=data["source"],
            amount=Decimal(data["amount"]),
            currency=data["currency"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


class FeeCollector:
    """
    Collects and manages fee payments in the HorseClaw system.
    
    Features:
    - Receive fee payments from agents
    - Track running balance
    - Support multiple currencies
    - Calculate totals by source
    - Maintain payment history
    """
    
    # Supported currencies
    SUPPORTED_CURRENCIES = {"USD", "USDC", "USDT"}
    
    def __init__(self):
        """Initialize fee collector with zero balance."""
        self._balances: Dict[str, Decimal] = {}
        self._payments: List[FeePayment] = []
        self._payment_counter: int = 0
    
    def _generate_payment_id(self) -> str:
        """Generate unique payment ID."""
        self._payment_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"FEE-{timestamp}-{self._payment_counter:06d}"
    
    def collect(self, 
                source: str, 
                amount: float, 
                currency: str = "USD",
                metadata: Optional[Dict[str, Any]] = None) -> FeePayment:
        """
        Collect a fee payment.
        
        Args:
            source: Agent or system that paid the fee
            amount: Fee amount (must be positive)
            currency: Currency code (default: USD)
            metadata: Additional payment information
            
        Returns:
            FeePayment object
            
        Raises:
            ValueError: If amount is negative or currency unsupported
        """
        # Validate amount
        if amount < 0:
            raise ValueError("Fee amount cannot be negative")
        
        # Validate currency
        currency = currency.upper()
        if currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}. "
                           f"Supported: {self.SUPPORTED_CURRENCIES}")
        
        # Convert to Decimal for precision
        decimal_amount = Decimal(str(amount)).quantize(
            Decimal('0.01'), 
            rounding=ROUND_HALF_UP
        )
        
        # Create payment record
        payment = FeePayment(
            payment_id=self._generate_payment_id(),
            source=source,
            amount=decimal_amount,
            currency=currency,
            metadata=metadata or {}
        )
        
        # Update balance
        if currency not in self._balances:
            self._balances[currency] = Decimal('0')
        self._balances[currency] += decimal_amount
        
        # Store payment
        self._payments.append(payment)
        
        return payment
    
    def get_balance(self, currency: str = "USD") -> Decimal:
        """
        Get current balance for a specific currency.
        
        Args:
            currency: Currency code
            
        Returns:
            Current balance as Decimal
        """
        return self._balances.get(currency.upper(), Decimal('0'))
    
    def get_total_balance_usd(self) -> Decimal:
        """
        Get total balance in USD (assuming 1:1 for stablecoins).
        
        Returns:
            Total USD equivalent
        """
        total = Decimal('0')
        for currency, amount in self._balances.items():
            # For now, assume all are 1:1 with USD
            # In production, use oracle/price feed
            total += amount
        return total
    
    def get_payments(self,
                    source: Optional[str] = None,
                    currency: Optional[str] = None,
                    limit: Optional[int] = None) -> List[FeePayment]:
        """
        Get payment history with optional filters.
        
        Args:
            source: Filter by payment source
            currency: Filter by currency
            limit: Maximum number of payments to return
            
        Returns:
            List of FeePayment objects
        """
        payments = self._payments
        
        if source:
            payments = [p for p in payments if p.source == source]
        
        if currency:
            currency = currency.upper()
            payments = [p for p in payments if p.currency == currency]
        
        # Return most recent first
        payments = sorted(payments, key=lambda p: p.timestamp, reverse=True)
        
        if limit:
            payments = payments[:limit]
        
        return payments
    
    def get_stats_by_source(self) -> Dict[str, Dict[str, Any]]:
        """
        Get fee statistics grouped by source.
        
        Returns:
            Dictionary with stats per source
        """
        stats = {}
        
        for payment in self._payments:
            source = payment.source
            if source not in stats:
                stats[source] = {
                    "total_payments": 0,
                    "total_amount": Decimal('0'),
                    "currencies": set()
                }
            
            stats[source]["total_payments"] += 1
            stats[source]["total_amount"] += payment.amount
            stats[source]["currencies"].add(payment.currency)
        
        # Convert sets to lists for JSON serialization
        for source in stats:
            stats[source]["currencies"] = list(stats[source]["currencies"])
            stats[source]["total_amount"] = str(stats[source]["total_amount"])
        
        return stats
    
    def withdraw(self, amount: float, currency: str = "USD") -> bool:
        """
        Withdraw from balance (for token conversion).
        
        Args:
            amount: Amount to withdraw
            currency: Currency to withdraw
            
        Returns:
            True if successful, False if insufficient funds
        """
        currency = currency.upper()
        decimal_amount = Decimal(str(amount)).quantize(Decimal('0.01'))
        
        current_balance = self._balances.get(currency, Decimal('0'))
        
        if decimal_amount > current_balance:
            return False
        
        self._balances[currency] = current_balance - decimal_amount
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Export collector state to dictionary."""
        return {
            "balances": {c: str(a) for c, a in self._balances.items()},
            "payments": [p.to_dict() for p in self._payments],
            "payment_counter": self._payment_counter,
            "total_payments": len(self._payments)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeeCollector':
        """Restore collector from dictionary."""
        collector = cls()
        
        # Restore balances
        for currency, amount_str in data.get("balances", {}).items():
            collector._balances[currency] = Decimal(amount_str)
        
        # Restore payments
        collector._payments = [
            FeePayment.from_dict(p_data)
            for p_data in data.get("payments", [])
        ]
        
        collector._payment_counter = data.get("payment_counter", len(collector._payments))
        
        return collector
