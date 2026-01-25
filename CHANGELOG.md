# Changelog

All notable changes to the Claude Workspace Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-25

### Added

#### Core Framework
- Initial release of Claude Workspace Framework
- 7 core packages: memory-system, session-hub, email-system, yaml-registries, skills-framework, notification-layer, mcp-templates

#### Skills
- `/contribute-framework` - Push improvements to upstream framework repository

#### Scripts
- `framework-sync.sh` - Pull/push framework updates via git subtree
- `contribute-framework.sh` - Automated contribution workflow with validation
- `validate-framework.sh` - Check for project-specific content before pushing
- `install-hooks.sh` - Install git hooks for automatic validation
- `framework-update.sh` - Detect and apply framework updates to workspace

#### Protection & Validation
- GitHub Actions CI workflow for framework purity validation
- Pre-push hooks to prevent accidental exposure of secrets
- FRAMEWORK-RULES.md documentation for contribution guidelines

#### Templates
- CLAUDE.md - Workspace context template
- session-registry.yaml - Session management template
- checks.yaml / followups.yaml - Memory system templates
- registry.yaml - Entity registry template
- skill-template.md - Skill definition template
- mcp-boilerplate/ - MCP server starter code

#### Examples
- IT-Admin (Acme MSP) - Reference MSP workspace
- Phoenix-Voyages (Horizon Travel) - Reference travel agency workspace

#### Documentation
- GLOSSARY.md - Standardized terminology
- Playbooks for deployment and management
- FRAMEWORK-MANIFEST.yaml - Capability tracking for update detection

---

## How to Update

When pulling framework updates, run:

```bash
# Pull updates
./framework/scripts/framework-sync.sh pull

# See what's new
./framework/scripts/framework-update.sh

# Apply updates to workspace (experimental)
./framework/scripts/framework-update.sh --apply
```

## Contributing

See [FRAMEWORK-RULES.md](FRAMEWORK-RULES.md) for contribution guidelines.

Use `/contribute-framework` or `./framework/scripts/contribute-framework.sh` to push improvements upstream.
