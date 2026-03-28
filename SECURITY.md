# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please:

1. **DO NOT** open a public issue
2. Email security@horseclaw.ai with details
3. Allow 48 hours for initial response
4. Allow 7 days for vulnerability assessment

## Security Measures

- All financial calculations use `Decimal` for precision
- Input validation on all API endpoints
- State persistence with integrity checks
- No external API calls for pricing (fixed rates)
- Audit logging for all transactions

## Best Practices

- Use strong passwords for state files
- Regularly backup state files
- Monitor transaction logs
- Keep dependencies updated
