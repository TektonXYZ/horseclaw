"""
HorseClaw Main Module - Bilingual AI Token Budget Manager
HorseClaw 主模块 - 双语 AI 代币预算管理器

The main orchestrator that brings together all modules.
整合所有模块的主协调器。
"""

import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Import all modules
try:
    # Package import
    from .agent_registry import AgentRegistry, Agent
    from .transaction_logger import TransactionLogger, TransactionType, TransactionStatus
    from .fee_collector import FeeCollector, FeePayment
    from .token_converter import TokenConverter, TokenPool, ConversionResult
    from .allocation_engine import AllocationEngine, AllocationRequest, AllocationResponse
    from .allocation_engine import AllocationStatus, Priority
except ImportError:
    # Direct import
    from agent_registry import AgentRegistry, Agent
    from transaction_logger import TransactionLogger, TransactionType, TransactionStatus
    from fee_collector import FeeCollector, FeePayment
    from token_converter import TokenConverter, TokenPool, ConversionResult
    from allocation_engine import AllocationEngine, AllocationRequest, AllocationResponse
    from allocation_engine import AllocationStatus, Priority


# I18n Support / 国际化支持
I18N_STRINGS = {
    "en": {
        # App
        "app_name": "HorseClaw",
        "app_description": "AI Token Budget Management System",
        "version": "Version",
        
        # Status
        "status_active": "Active",
        "status_inactive": "Inactive",
        "status_error": "Error",
        "status_ready": "Ready",
        
        # Modules
        "module_fee_collector": "Fee Collector",
        "module_token_converter": "Token Converter",
        "module_allocation_engine": "Allocation Engine",
        "module_agent_registry": "Agent Registry",
        "module_transaction_logger": "Transaction Logger",
        
        # Operations
        "op_success": "Success",
        "op_failed": "Failed",
        "op_pending": "Pending",
        "op_processing": "Processing",
        
        # Errors
        "err_insufficient_funds": "Insufficient funds",
        "err_agent_not_registered": "Agent not registered",
        "err_invalid_request": "Invalid request",
        "err_negative_balance": "Negative balance not allowed",
        "err_max_allocation": "Maximum allocation exceeded",
        "err_system": "System error occurred",
        "err_invalid_json": "Invalid JSON format",
        "err_missing_field": "Missing required field",
        
        # Allocation
        "alloc_approved": "Allocation approved",
        "alloc_partial": "Partial allocation granted",
        "alloc_rejected": "Allocation rejected",
        "alloc_reason_reserve": "Reserve requirement not met",
        "alloc_reason_limit": "Exceeds maximum allocation limit",
        "alloc_reason_unregistered": "Agent not in registry",
        
        # Pricing
        "price_claude": "Claude: $1 = 20,000 tokens",
        "price_kimi": "Kimi: $1 = 40,000 tokens",
        
        # Rules
        "rule_max_alloc": "Maximum 30% per request (50% for high priority)",
        "rule_reserve": "10% reserve always maintained",
        "rule_partial": "Partial allocation when insufficient",
        "rule_unregistered": "Unregistered agents rejected",
        
        # Stats
        "stat_total_fees": "Total Fees Collected",
        "stat_total_tokens": "Total Tokens Allocated",
        "stat_active_agents": "Active Agents",
        "stat_pending_requests": "Pending Requests",
        "stat_fulfillment_rate": "Fulfillment Rate",
        
        # General
        "welcome": "Welcome to HorseClaw",
        "ready": "System ready",
        "shutdown": "Shutting down",
        "saved": "State saved successfully",
        "loaded": "State loaded successfully",
        "error_saving": "Error saving state",
        "error_loading": "Error loading state",
    },
    "zh": {
        # App
        "app_name": "HorseClaw",
        "app_description": "AI 代币预算管理系统",
        "version": "版本",
        
        # Status
        "status_active": "活跃",
        "status_inactive": "非活跃",
        "status_error": "错误",
        "status_ready": "就绪",
        
        # Modules
        "module_fee_collector": "费用收集器",
        "module_token_converter": "代币转换器",
        "module_allocation_engine": "分配引擎",
        "module_agent_registry": "代理注册表",
        "module_transaction_logger": "交易记录器",
        
        # Operations
        "op_success": "成功",
        "op_failed": "失败",
        "op_pending": "待处理",
        "op_processing": "处理中",
        
        # Errors
        "err_insufficient_funds": "资金不足",
        "err_agent_not_registered": "代理未注册",
        "err_invalid_request": "无效请求",
        "err_negative_balance": "不允许负余额",
        "err_max_allocation": "超出最大分配额",
        "err_system": "系统错误发生",
        "err_invalid_json": "无效的 JSON 格式",
        "err_missing_field": "缺少必填字段",
        
        # Allocation
        "alloc_approved": "分配已批准",
        "alloc_partial": "已授予部分分配",
        "alloc_rejected": "分配被拒绝",
        "alloc_reason_reserve": "未满足储备要求",
        "alloc_reason_limit": "超出最大分配限制",
        "alloc_reason_unregistered": "代理不在注册表中",
        
        # Pricing
        "price_claude": "Claude: $1 = 20,000 代币",
        "price_kimi": "Kimi: $1 = 40,000 代币",
        
        # Rules
        "rule_max_alloc": "每次请求最多 30% (高优先级 50%)",
        "rule_reserve": "始终保持 10% 储备",
        "rule_partial": "不足时部分分配",
        "rule_unregistered": "拒绝未注册代理",
        
        # Stats
        "stat_total_fees": "收集的总费用",
        "stat_total_tokens": "分配的总代币",
        "stat_active_agents": "活跃代理",
        "stat_pending_requests": "待处理请求",
        "stat_fulfillment_rate": "满足率",
        
        # General
        "welcome": "欢迎使用 HorseClaw",
        "ready": "系统就绪",
        "shutdown": "正在关闭",
        "saved": "状态保存成功",
        "loaded": "状态加载成功",
        "error_saving": "保存状态时出错",
        "error_loading": "加载状态时出错",
    }
}


class I18n:
    """Internationalization helper class."""
    
    def __init__(self, language: str = "en"):
        """Initialize with language code."""
        self.language = language if language in I18N_STRINGS else "en"
        self._strings = I18N_STRINGS[self.language]
    
    def set_language(self, language: str):
        """Change language."""
        if language in I18N_STRINGS:
            self.language = language
            self._strings = I18N_STRINGS[language]
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """Get translated string."""
        return self._strings.get(key, default or key)
    
    def __call__(self, key: str, **kwargs) -> str:
        """Get and format translated string."""
        text = self._strings.get(key, key)
        return text.format(**kwargs) if kwargs else text


@dataclass
class SystemStatus:
    """Complete system status snapshot."""
    timestamp: datetime
    is_active: bool
    language: str
    
    # Balances
    total_fees_usd: Decimal
    total_tokens_claude: int
    total_tokens_kimi: int
    available_tokens_claude: int
    available_tokens_kimi: int
    
    # Counts
    registered_agents: int
    active_agents: int
    total_transactions: int
    pending_allocations: int
    
    # Rates
    fulfillment_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "is_active": self.is_active,
            "language": self.language,
            "balances": {
                "total_fees_usd": str(self.total_fees_usd),
                "tokens": {
                    "claude": {
                        "total": self.total_tokens_claude,
                        "available": self.available_tokens_claude
                    },
                    "kimi": {
                        "total": self.total_tokens_kimi,
                        "available": self.available_tokens_kimi
                    }
                }
            },
            "counts": {
                "registered_agents": self.registered_agents,
                "active_agents": self.active_agents,
                "total_transactions": self.total_transactions,
                "pending_allocations": self.pending_allocations
            },
            "fulfillment_rate": self.fulfillment_rate
        }


class HorseClaw:
    """
    Main HorseClaw Agent - Bilingual AI Token Budget Manager
    
    Orchestrates all modules:
    - FeeCollector: Receives USD payments
    - TokenConverter: Converts to Claude/Kimi tokens
    - AllocationEngine: Processes allocation requests
    - AgentRegistry: Manages registered agents
    - TransactionLogger: Logs all operations
    
    Supports both English and Chinese (中文).
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, language: str = "en", state_file: Optional[str] = None):
        """
        Initialize HorseClaw agent.
        
        Args:
            language: "en" or "zh"
            state_file: Optional path to state file for persistence
        """
        # I18n
        self.i18n = I18n(language)
        self.language = language
        
        # State file
        self.state_file = state_file
        
        # Initialize all modules
        self.registry = AgentRegistry()
        self.logger = TransactionLogger()
        self.fee_collector = FeeCollector()
        self.token_converter = TokenConverter()
        self.allocation_engine = AllocationEngine(
            token_converter=self.token_converter,
            agent_registry=self.registry
        )
        
        # Link logger to modules
        self._link_logger()
        
        # System state
        self.is_active = True
        self.startup_time = datetime.now()
        
        # Load state if exists
        if state_file and Path(state_file).exists():
            self.load_state(state_file)
    
    def _link_logger(self):
        """Link transaction logger to all modules."""
        # Modules track their own state; logger is called explicitly
        pass
    
    # ==================== AGENT REGISTRY OPERATIONS ====================
    
    def register_agent(self, agent_id: str, name: str, 
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Register a new agent.
        
        Request: {"action": "register_agent", "agent_id": "...", "name": "...", "metadata": {...}}
        Response: {"success": true/false, "message": "...", "agent": {...}}
        """
        success = self.registry.register(agent_id, name, metadata)
        
        if success:
            # Log transaction
            self.logger.log(
                tx_type=TransactionType.AGENT_REGISTERED,
                agent_id=agent_id,
                metadata={"name": name, **(metadata or {})}
            )
            
            return {
                "success": True,
                "message": self.i18n("Agent registered successfully"),
                "agent": self.registry.get_agent(agent_id).to_dict()
            }
        else:
            return {
                "success": False,
                "message": self.i18n("Agent already registered"),
                "agent_id": agent_id
            }
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent information."""
        agent = self.registry.get_agent(agent_id)
        return agent.to_dict() if agent else None
    
    def list_agents(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """List all registered agents."""
        agents = self.registry.get_all_agents(active_only)
        return [a.to_dict() for a in agents]
    
    def deactivate_agent(self, agent_id: str) -> Dict[str, Any]:
        """Deactivate an agent."""
        success = self.registry.deactivate(agent_id)
        
        if success:
            self.logger.log(
                tx_type=TransactionType.AGENT_DEACTIVATED,
                agent_id=agent_id
            )
            return {
                "success": True,
                "message": self.i18n("Agent deactivated")
            }
        return {
            "success": False,
            "message": self.i18n("Agent not found")
        }
    
    # ==================== FEE COLLECTION ====================
    
    def collect_fee(self, source: str, amount: float, 
                   currency: str = "USD",
                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Collect a fee payment.
        
        Request: {"action": "collect_fee", "source": "...", "amount": 100.00, "currency": "USD"}
        Response: {"success": true, "payment_id": "...", "balance": "..."}
        """
        try:
            payment = self.fee_collector.collect(source, amount, currency, metadata)
            
            # Log transaction
            self.logger.log(
                tx_type=TransactionType.FEE_RECEIVED,
                agent_id=source,
                amount=float(payment.amount),
                currency=payment.currency
            )
            
            return {
                "success": True,
                "payment_id": payment.payment_id,
                "amount": str(payment.amount),
                "currency": payment.currency,
                "balance": str(self.fee_collector.get_balance(currency)),
                "message": self.i18n("op_success")
            }
        except ValueError as e:
            return {
                "success": False,
                "message": str(e)
            }
    
    def get_fee_balance(self, currency: str = "USD") -> Dict[str, Any]:
        """Get fee balance."""
        balance = self.fee_collector.get_balance(currency)
        total_usd = self.fee_collector.get_total_balance_usd()
        
        return {
            "currency": currency,
            "balance": str(balance),
            "total_usd_equivalent": str(total_usd)
        }
    
    # ==================== TOKEN CONVERSION ====================
    
    def convert_fees_to_tokens(self, usd_amount: float,
                               allocation: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Convert USD fees to tokens.
        
        Request: {"action": "convert", "usd_amount": 100, "allocation": {"claude": 0.5, "kimi": 0.5}}
        Response: {"success": true, "conversion_id": "...", "tokens": {"claude": ..., "kimi": ...}}
        """
        # Check if we have enough fees
        available = self.fee_collector.get_total_balance_usd()
        if Decimal(str(usd_amount)) > available:
            return {
                "success": False,
                "message": self.i18n("err_insufficient_funds"),
                "available": str(available),
                "requested": usd_amount
            }
        
        # Withdraw from fee collector
        withdrawn = self.fee_collector.withdraw(usd_amount, "USD")
        if not withdrawn:
            return {
                "success": False,
                "message": self.i18n("err_insufficient_funds")
            }
        
        # Convert to tokens
        result = self.token_converter.convert(usd_amount, allocation)
        
        # Log transaction
        self.logger.log(
            tx_type=TransactionType.TOKEN_CONVERTED,
            amount=usd_amount,
            currency="USD"
        )
        
        return {
            "success": True,
            "conversion_id": result.conversion_id,
            "usd_amount": str(result.usd_amount),
            "tokens": {
                "claude": result.claude_tokens,
                "kimi": result.kimi_tokens
            },
            "pools": {
                "claude": self.token_converter.get_pool("claude").to_dict(),
                "kimi": self.token_converter.get_pool("kimi").to_dict()
            }
        }
    
    def get_token_pools(self) -> Dict[str, Any]:
        """Get current token pool status."""
        return {
            "claude": self.token_converter.get_pool("claude").to_dict(),
            "kimi": self.token_converter.get_pool("kimi").to_dict()
        }
    
    def get_pricing(self) -> Dict[str, Any]:
        """Get token pricing."""
        return {
            "claude": self.i18n("price_claude"),
            "kimi": self.i18n("price_kimi"),
            "rates": self.token_converter.get_pricing()
        }
    
    # ==================== ALLOCATION ====================
    
    def request_tokens(self, agent_id: str, model: str, tokens: int,
                      priority: str = "normal",
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Request token allocation.
        
        Request: {"action": "request_tokens", "agent_id": "...", "model": "claude", "tokens": 1000, "priority": "high"}
        Response: {"status": "approved/partial/rejected", "tokens_granted": ..., "reason": "..."}
        """
        # Convert priority string to enum
        priority_map = {
            "low": Priority.LOW,
            "normal": Priority.NORMAL,
            "high": Priority.HIGH,
            "critical": Priority.CRITICAL
        }
        priority_enum = priority_map.get(priority.lower(), Priority.NORMAL)
        
        # Process request
        response = self.allocation_engine.request_allocation(
            agent_id=agent_id,
            model=model,
            tokens_requested=tokens,
            priority=priority_enum,
            metadata=metadata
        )
        
        # Log transaction
        status_map = {
            AllocationStatus.APPROVED: TransactionStatus.COMPLETED,
            AllocationStatus.PARTIAL: TransactionStatus.PARTIAL,
            AllocationStatus.REJECTED: TransactionStatus.FAILED,
            AllocationStatus.PENDING: TransactionStatus.PENDING
        }
        
        self.logger.log(
            tx_type=TransactionType.TOKEN_ALLOCATED,
            agent_id=agent_id,
            tokens_allocated=response.tokens_granted,
            model=model,
            status=status_map[response.status]
        )
        
        return response.to_dict()
    
    def get_allocation_stats(self) -> Dict[str, Any]:
        """Get allocation statistics."""
        return self.allocation_engine.get_stats()
    
    # ==================== STATUS & STATS ====================
    
    def get_status(self) -> SystemStatus:
        """Get complete system status."""
        # Get token totals
        token_totals = self.token_converter.get_total_tokens()
        
        # Get allocation stats
        alloc_stats = self.allocation_engine.get_stats()
        
        return SystemStatus(
            timestamp=datetime.now(),
            is_active=self.is_active,
            language=self.language,
            total_fees_usd=self.fee_collector.get_total_balance_usd(),
            total_tokens_claude=token_totals["claude"]["total"],
            total_tokens_kimi=token_totals["kimi"]["total"],
            available_tokens_claude=token_totals["claude"]["available"],
            available_tokens_kimi=token_totals["kimi"]["available"],
            registered_agents=self.registry.get_agent_count(active_only=False),
            active_agents=self.registry.get_agent_count(active_only=True),
            total_transactions=len(self.logger.get_all_transactions()),
            pending_allocations=0,  # TODO: Track pending
            fulfillment_rate=alloc_stats.get("fulfillment_rate", 0)
        )
    
    def get_full_report(self) -> Dict[str, Any]:
        """Get comprehensive system report."""
        status = self.get_status()
        
        return {
            "system": {
                "name": self.i18n("app_name"),
                "version": self.VERSION,
                "language": self.language,
                "uptime_seconds": (datetime.now() - self.startup_time).total_seconds(),
                "is_active": self.is_active
            },
            "status": status.to_dict(),
            "agents": {
                "total": self.registry.get_agent_count(active_only=False),
                "active": self.registry.get_agent_count(active_only=True),
                "list": [a.to_dict() for a in self.registry.get_all_agents(active_only=False)]
            },
            "finance": {
                "fees_collected": str(self.fee_collector.get_total_balance_usd()),
                "token_pools": self.get_token_pools()
            },
            "allocation": self.allocation_engine.get_stats(),
            "transactions": {
                "total": len(self.logger.get_all_transactions()),
                "stats": self.logger.get_stats()
            },
            "pricing": self.get_pricing()
        }
    
    # ==================== JSON I/O INTERFACE ====================
    
    def process_json_request(self, json_input: Union[str, Dict[str, Any]]) -> str:
        """
        Process a JSON request and return JSON response.
        Main entry point for external integration.
        
        Request format:
        {
            "action": "register_agent" | "collect_fee" | "convert" | "request_tokens" | 
                      "get_status" | "get_agents" | "get_pools" | "get_report",
            ...action-specific fields...
        }
        
        Returns: JSON string
        """
        try:
            # Parse input
            if isinstance(json_input, str):
                request = json.loads(json_input)
            else:
                request = json_input
            
            action = request.get("action")
            
            # Route to appropriate handler
            if action == "register_agent":
                result = self.register_agent(
                    agent_id=request["agent_id"],
                    name=request["name"],
                    metadata=request.get("metadata")
                )
            
            elif action == "collect_fee":
                result = self.collect_fee(
                    source=request["source"],
                    amount=request["amount"],
                    currency=request.get("currency", "USD"),
                    metadata=request.get("metadata")
                )
            
            elif action == "convert":
                result = self.convert_fees_to_tokens(
                    usd_amount=request["usd_amount"],
                    allocation=request.get("allocation")
                )
            
            elif action == "request_tokens":
                result = self.request_tokens(
                    agent_id=request["agent_id"],
                    model=request["model"],
                    tokens=request["tokens"],
                    priority=request.get("priority", "normal"),
                    metadata=request.get("metadata")
                )
            
            elif action == "get_status":
                result = self.get_status().to_dict()
            
            elif action == "get_agents":
                result = {
                    "agents": self.list_agents(request.get("active_only", True))
                }
            
            elif action == "get_pools":
                result = self.get_token_pools()
            
            elif action == "get_report":
                result = self.get_full_report()
            
            elif action == "get_pricing":
                result = self.get_pricing()
            
            elif action == "set_language":
                lang = request.get("language", "en")
                self.i18n.set_language(lang)
                self.language = lang
                result = {"success": True, "language": lang}
            
            else:
                result = {
                    "error": True,
                    "message": f"Unknown action: {action}"
                }
            
            return json.dumps(result, indent=2, ensure_ascii=False)
        
        except json.JSONDecodeError as e:
            return json.dumps({
                "error": True,
                "message": self.i18n("err_invalid_json"),
                "details": str(e)
            })
        
        except KeyError as e:
            return json.dumps({
                "error": True,
                "message": self.i18n("err_missing_field"),
                "field": str(e)
            })
        
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": self.i18n("err_system"),
                "details": str(e)
            })
    
    # ==================== PERSISTENCE ====================
    
    def save_state(self, filepath: Optional[str] = None) -> Dict[str, Any]:
        """
        Save complete system state to file.
        
        Returns:
            Status dictionary
        """
        path = filepath or self.state_file
        if not path:
            return {"success": False, "message": "No state file specified"}
        
        try:
            state = {
                "version": self.VERSION,
                "timestamp": datetime.now().isoformat(),
                "language": self.language,
                "is_active": self.is_active,
                "registry": self.registry.to_dict(),
                "fee_collector": self.fee_collector.to_dict(),
                "token_converter": self.token_converter.to_dict(),
                "allocation_engine": self.allocation_engine.to_dict(),
                "logger": self.logger.to_dict()
            }
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            return {"success": True, "message": self.i18n("saved"), "path": path}
        
        except Exception as e:
            return {"success": False, "message": self.i18n("error_saving"), "error": str(e)}
    
    def load_state(self, filepath: Optional[str] = None) -> Dict[str, Any]:
        """
        Load system state from file.
        
        Returns:
            Status dictionary
        """
        path = filepath or self.state_file
        if not path or not Path(path).exists():
            return {"success": False, "message": "State file not found"}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Restore language
            self.language = state.get("language", "en")
            self.i18n.set_language(self.language)
            
            # Restore modules
            self.registry = AgentRegistry.from_dict(state.get("registry", {}))
            self.fee_collector = FeeCollector.from_dict(state.get("fee_collector", {}))
            self.token_converter = TokenConverter.from_dict(state.get("token_converter", {}))
            self.logger = TransactionLogger.from_dict(state.get("logger", {}))
            
            # Restore allocation engine with new references
            self.allocation_engine = AllocationEngine.from_dict(
                state.get("allocation_engine", {}),
                token_converter=self.token_converter,
                agent_registry=self.registry
            )
            
            self.is_active = state.get("is_active", True)
            
            return {"success": True, "message": self.i18n("loaded"), "path": path}
        
        except Exception as e:
            return {"success": False, "message": self.i18n("error_loading"), "error": str(e)}
    
    # ==================== UTILITY ====================
    
    def set_language(self, language: str) -> bool:
        """Change system language."""
        if language in I18N_STRINGS:
            self.language = language
            self.i18n.set_language(language)
            return True
        return False
    
    def shutdown(self) -> Dict[str, Any]:
        """Graceful shutdown with state save."""
        self.is_active = False
        
        result = {"message": self.i18n("shutdown")}
        
        if self.state_file:
            save_result = self.save_state()
            result["save_status"] = save_result
        
        return result
