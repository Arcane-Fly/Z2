# Z2 Platform Documentation

Welcome to the Z2 AI Workforce Platform documentation hub.

## 📚 Core Documentation

### Architecture & Design
- [Technical Architecture](setup/technical-architecture.md) - System design and infrastructure
- [Deployment Architecture](DEPLOYMENT_ARCHITECTURE.md) - Production deployment patterns
- [Product Requirements](product-requirement-document.md) - Product specifications and features
- [Specifications](specifications.md) - Technical specifications

### Build & Development
- **[Monorepo Tooling Recommendations](MONOREPO_TOOLING_RECOMMENDATIONS.md)** - Decision guide for Nx vs Bazel/Pants ⭐
- **[Monorepo Tooling Cheatsheet](MONOREPO_TOOLING_CHEATSHEET.md)** - Quick reference for build tools ⭐
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to Z2

### Deployment
- [Railway Deployment Guide](RAILWAY_DEPLOYMENT_GUIDE.md) - Deploy to Railway.com
- [Railway Configuration](railway-config.md) - Railway-specific settings
- [Deployment Checklist](railway-deployment-checklist.md) - Pre-deployment verification

### Security
- [Authentication Guide](AUTHENTICATION.md) - Auth implementation details
- [Security Documentation](security/) - Security policies and best practices

### Testing
- [Testing Documentation](testing/) - Test strategies and practices
- [Heavy Analysis Integration](HEAVY_ANALYSIS_INTEGRATION.md) - Load testing setup

## 🗂️ Documentation Sections

### `/setup`
Initial setup and configuration guides:
- Getting started
- Environment configuration
- Development environment setup

### `/operations`
Operational guides:
- Monitoring and observability
- Incident response
- Performance tuning

### `/security`
Security documentation:
- Authentication and authorization
- Data protection
- Compliance

### `/testing`
Testing guides:
- Unit testing
- Integration testing
- E2E testing

## 🚀 Quick Links

### For New Developers
1. [Getting Started](setup/README.md) - Set up your development environment
2. [Contributing Guide](CONTRIBUTING.md) - Learn the contribution workflow
3. [Technical Architecture](setup/technical-architecture.md) - Understand the system

### For DevOps/SRE
1. [Deployment Architecture](DEPLOYMENT_ARCHITECTURE.md) - Production setup
2. [Railway Deployment Guide](RAILWAY_DEPLOYMENT_GUIDE.md) - Deployment process
3. [Monitoring Setup](operations/) - Observability configuration

### For Architects
1. [Technical Architecture](setup/technical-architecture.md) - System design
2. **[Monorepo Tooling Recommendations](MONOREPO_TOOLING_RECOMMENDATIONS.md)** - Build system decisions ⭐
3. [Specifications](specifications.md) - Technical specs

## 📋 Recent Updates

### 2025-01-08
- ✨ Added comprehensive monorepo tooling recommendations
- ✨ Created quick reference cheatsheet for Nx vs Bazel/Pants
- 📊 Decision matrix for build system selection
- 💡 Cost-benefit analysis for tooling options

### Previous
- [Session Report 2025-10-02](SESSION_REPORT_2025_10_02.md)
- [Upgrade Report 2024-12-19](UPGRADE_REPORT_2024-12-19.md)
- [Roadmap Updates](ROADMAP_UPDATE_SUMMARY.md)

## 🔍 Finding Documentation

Use GitHub's search or these patterns:

```bash
# Find deployment docs
ls docs/*deploy*

# Find security docs
ls docs/security/

# Find setup guides
ls docs/setup/
```

## 🤝 Contributing to Documentation

Documentation improvements are always welcome! Please:

1. Follow Markdown best practices
2. Keep navigation clear (use relative links)
3. Update this index when adding major docs
4. Use clear, concise language
5. Include code examples where helpful

## 📞 Need Help?

- **Questions:** Open a [GitHub Discussion](https://github.com/Arcane-Fly/Z2/discussions)
- **Issues:** Create a [GitHub Issue](https://github.com/Arcane-Fly/Z2/issues)
- **Urgent:** Contact the team in #engineering

---

**Note:** This is a living index. If you add significant documentation, please update this file.
