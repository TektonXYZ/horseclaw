"""
Transaction Logger Module
交易记录器模块

Logs all transactions and state changes in the HorseClaw system.
记录 HorseClaw 系统中的所有交易和状态变化。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json


class TransactionType(Enum):
    """Types of transactions in the system."""
    FEE_RECEIVED = "fee_received"
    TOKEN_ALLOCATED = "token_allocated"
    TOKEN_CONVERTED = "token_converted"
    AGENT_REGISTERED = "agent_registered"
    AGENT_DEACTIVATED = "agent_deactivated"
    SYSTEM_STATE_CHANGE = "system_state_change"
    ERROR = "error"


class TransactionStatus(Enum):
    """Status of transactions."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class Transaction:
    """Represents a single transaction in the system."""
    tx_id: str
    tx_type: TransactionType
    timestamp: datetime = field(default_factory=datetime.now)
    status: TransactionStatus = TransactionStatus.COMPLETED
    agent_id: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    tokens_allocated: Optional[int] = None
    model: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary."""
        return {
            "tx_id": self.tx_id,
            "tx_type": self.tx_type.value,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "agent_id": self.agent_id,
            "amount": self.amount,
            "currency": self.currency,
            "tokens_allocated": self.tokens_allocated,
            "model": self.model,
            "metadata": self.metadata,
            "error_message": self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create transaction from dictionary."""
        return cls(
            tx_id=data["tx_id"],
            tx_type=TransactionType(data["tx_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            status=TransactionStatus(data["status"]),
            agent_id=data.get("agent_id"),
            amount=data.get("amount"),
            currency=data.get("currency"),
            tokens_allocated=data.get("tokens_allocated"),
            model=data.get("model"),
            metadata=data.get("metadata", {}),
            error_message=data.get("error_message")
        )


class TransactionLogger:
    """
    Logs and manages all transactions in the HorseClaw system.
    
    Features:
    - Log all transactions with unique IDs
    - Query transaction history
    - Filter by type, agent, date range
    - Export logs
    - Maintain audit trail
    """
    
    def __init__(self):
        """Initialize empty transaction log."""
        self._transactions: List[Transaction] = []
        self._tx_counter: int = 0
    
    def _generate_tx_id(self) -> str:
        """Generate unique transaction ID."""
        self._tx_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"TX-{timestamp}-{self._tx_counter:06d}"
    
    def log(self, 
            tx_type: TransactionType,
            agent_id: Optional[str] = None,
            amount: Optional[float] = None,
            currency: Optional[str] = None,
            tokens_allocated: Optional[int] = None,
            model: Optional[str] = None,
            status: TransactionStatus = TransactionStatus.COMPLETED,
            metadata: Optional[Dict[str, Any]] = None,
            error_message: Optional[str] = None) -> Transaction:
        """
        Log a new transaction.
        
        Args:
            tx_type: Type of transaction
            agent_id: Agent involved (if applicable)
            amount: Monetary amount (if applicable)
            currency: Currency code (if applicable)
            tokens_allocated: Number of tokens (if applicable)
            model: AI model (if applicable)
            status: Transaction status
            metadata: Additional data
            error_message: Error description (if failed)
            
        Returns:
            The logged Transaction object
        """
        tx = Transaction(
            tx_id=self._generate_tx_id(),
            tx_type=tx_type,
            agent_id=agent_id,
            amount=amount,
            currency=currency,
            tokens_allocated=tokens_allocated,
            model=model,
            status=status,
            metadata=metadata or {},
            error_message=error_message
        )
        
        self._transactions.append(tx)
        return tx
    
    def get_all_transactions(self, 
                            limit: Optional[int] = None,
                            offset: int = 0) -> List[Transaction]:
        """
        Get all transactions with optional pagination.
        
        Args:
            limit: Maximum number to return
            offset: Skip first N transactions
            
        Returns:
            List of Transaction objects
        """
        transactions = self._transactions[offset:]
        if limit:
            transactions = transactions[:limit]
        return transactions
    
    def get_by_agent(self, agent_id: str) -> List[Transaction]:
        """Get all transactions for a specific agent."""
        return [tx for tx in self._transactions if tx.agent_id == agent_id]
    
    def get_by_type(self, tx_type: TransactionType) -> List[Transaction]:
        """Get all transactions of a specific type."""
        return [tx for tx in self._transactions if tx.tx_type == tx_type]
    
    def get_by_status(self, status: TransactionStatus) -> List[Transaction]:
        """Get all transactions with a specific status."""
        return [tx for tx in self._transactions if tx.status == status]
    
    def get_by_date_range(self, start: datetime, end: datetime) -> List[Transaction]:
        """Get transactions within a date range."""
        return [tx for tx in self._transactions if start <= tx.timestamp <= end]
    
    def get_transaction(self, tx_id: str) -> Optional[Transaction]:
        """Get a specific transaction by ID."""
        for tx in self._transactions:
            if tx.tx_id == tx_id:
                return tx
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get transaction statistics."""
        total = len(self._transactions)
        by_type = {}
        by_status = {}
        total_fees = 0.0
        total_tokens_allocated = 0
        
        for tx in self._transactions:
            # Count by type
            tx_type = tx.tx_type.value
            by_type[tx_type] = by_type.get(tx_type, 0) + 1
            
            # Count by status
            status = tx.status.value
            by_status[status] = by_status.get(status, 0) + 1
            
            # Sum fees
            if tx.amount and tx.tx_type == TransactionType.FEE_RECEIVED:
                total_fees += tx.amount
            
            # Sum tokens
            if tx.tokens_allocated:
                total_tokens_allocated += tx.tokens_allocated
        
        return {
            "total_transactions": total,
            "by_type": by_type,
            "by_status": by_status,
            "total_fees_usd": round(total_fees, 2),
            "total_tokens_allocated": total_tokens_allocated,
            "date_range": {
                "first": self._transactions[0].timestamp.isoformat() if self._transactions else None,
                "last": self._transactions[-1].timestamp.isoformat() if self._transactions else None
            }
        }
    
    def export_to_json(self, filepath: str):
        """Export all transactions to JSON file."""
        data = {
            "transactions": [tx.to_dict() for tx in self._transactions],
            "export_timestamp": datetime.now().isoformat(),
            "stats": self.get_stats()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_json(self, filepath: str):
        """Load transactions from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._transactions = [
            Transaction.from_dict(tx_data)
            for tx_data in data.get("transactions", [])
        ]
        
        # Restore counter
        if self._transactions:
            last_tx = self._transactions[-1]
            try:
                self._tx_counter = int(last_tx.tx_id.split('-')[-1])
            except:
                self._tx_counter = len(self._transactions)
    
    def clear(self):
        """Clear all transaction history."""
        self._transactions.clear()
        self._tx_counter = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Export logger state to dictionary."""
        return {
            "transactions": [tx.to_dict() for tx in self._transactions],
            "tx_counter": self._tx_counter,
            "stats": self.get_stats()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionLogger':
        """Restore logger from dictionary."""
        logger = cls()
        logger._transactions = [
            Transaction.from_dict(tx_data)
            for tx_data in data.get("transactions", [])
        ]
        logger._tx_counter = data.get("tx_counter", len(logger._transactions))
        return logger
