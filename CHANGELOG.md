# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-03-28

### Added - 添加

#### Core Features - 核心功能
- **Agent Registry** - Register and manage AI agents
- **Fee Collector** - Collect USD/USDC/USDT fees from agents  
- **Token Converter** - Convert fees to Claude/Kimi tokens at fixed rates
- **Allocation Engine** - Distribute tokens with configurable safety rules
- **Transaction Logger** - Audit logging for all operations

#### Safety Rules - 安全规则
- 10% reserve requirement always maintained
- Max 30% allocation per request (50% for high priority)
- Never negative balance
- Partial allocation support
- Unregistered agent rejection

#### Bilingual Support - 双语支持
- Full English (EN) support
- Full Chinese (中文) support
- 50+ translated strings
- Runtime language switching

#### API & Integration - API 和集成
- JSON API interface for external integration
- CLI interface for command-line operations
- State persistence (save/load)
- Full system reporting

#### Testing & Quality - 测试和质量
- 35+ comprehensive unit tests
- Integration tests
- Safety rule tests
- CI/CD pipeline with GitHub Actions
- Type hints throughout

#### Documentation - 文档
- Comprehensive bilingual README
- API documentation
- Usage examples and demos
- Contributing guidelines

#### Token Pricing - 代币定价
- Claude: $1 = 20,000 tokens
- Kimi: $1 = 40,000 tokens
- Fixed rates (no external API calls)

### Technical Details - 技术细节

#### Architecture - 架构
```
HorseClaw Core
├── Agent Registry (agent management)
├── Fee Collector (payment processing)
├── Token Converter (USD → tokens)
├── Allocation Engine (distribution logic)
└── Transaction Logger (audit trail)
```

#### Project Structure - 项目结构
```
horseclaw/
├── src/               # Source code (3,100+ lines)
├── tests/             # Test suite (35+ tests)
├── examples/          # Usage demos
├── locales/           # i18n strings
├── docs/              # Documentation
└── .github/           # CI/CD workflows
```

### Stats - 统计
- **Total Lines of Code**: 3,139
- **Test Coverage**: 35+ tests
- **Languages**: English, 中文
- **Modules**: 5 core + CLI
- **Commits**: 6+

---

## Future Roadmap - 未来路线图

### [1.1.0] - Planned
- Web dashboard for monitoring
- Webhook notifications
- Rate limiting per agent
- Token usage tracking

### [1.2.0] - Planned
- Multi-currency support expansion
- Dynamic pricing models
- Advanced allocation strategies
- Performance analytics

### [2.0.0] - Planned
- Async/await support
- REST API server
- Database backends (PostgreSQL, MongoDB)
- Kubernetes deployment

---

## Credits -  credits

- **Author**: Tekton
- **Organization**: TektonXYZ
- **License**: MIT

---

*Thank you to all contributors!*  
*感谢所有贡献者！*
