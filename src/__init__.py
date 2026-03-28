"""
HorseClaw - AI Token Budget Management System
HorseClaw - AI 代币预算管理系统

A bilingual (EN/ZH) system for managing AI token budgets across agents.
"""

from .horseclaw import HorseClaw, I18n, SystemStatus
from .agent_registry import AgentRegistry, Agent
from .transaction_logger import TransactionLogger, TransactionType, TransactionStatus, Transaction
from .fee_collector import FeeCollector, FeePayment
from .token_converter import TokenConverter, TokenPool, ConversionResult, PRICING
from .allocation_engine import AllocationEngine, AllocationRequest, AllocationResponse
from .allocation_engine import AllocationStatus, Priority

__version__ = "1.0.0"
__author__ = "Tekton"

__all__ = [
    # Main
    "HorseClaw",
    "I18n",
    "SystemStatus",
    
    # Modules
    "AgentRegistry",
    "Agent",
    "TransactionLogger",
    "TransactionType",
    "TransactionStatus",
    "Transaction",
    "FeeCollector",
    "FeePayment",
    "TokenConverter",
    "TokenPool",
    "ConversionResult",
    "PRICING",
    "AllocationEngine",
    "AllocationRequest",
    "AllocationResponse",
    "AllocationStatus",
    "Priority",
]
