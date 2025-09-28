# Repository Cleanup Plan

## Overview
This document provides a comprehensive cleanup plan for the AIGG repository. Each file is analyzed with justifications for whether to keep, move, or delete it, along with potential breaking changes.

**Last Updated**: After commit 650cd96 - "Implement LLM-based market matching with DSPy"

## File Categories and Recommendations

### 1. Test Files (ROOT DIRECTORY) - **MOVE TO tests/**
These test files are currently scattered in the root directory and should be organized:

| File | Action | Justification | Breaking? |
|------|--------|---------------|-----------|
| `test_internal.py` | Move to `tests/integration/` | Integration test for internal APIs | No |
| `test_llm_market_matching.py` | Move to `tests/unit/` | **NEW** - Unit test for LLM market matching | No |
| `test_market_improvements.py` | Move to `tests/integration/` | **NEW** - Market improvement testing | No |
| `test_market_matching_fixes.py` | Move to `tests/integration/` | Market matching bug fixes test | No |
| `test_market_matching_real.py` | Move to `tests/integration/` | **NEW** - Real market data testing | No |
| `test_market_matching_standalone.py` | Move to `tests/unit/` | **NEW** - Standalone market matching test | No |
| `test_response_improvement.py` | Move to `tests/integration/` | Response quality testing | No |
| `test_twitter_improvements.py` | Move to `tests/integration/` | Twitter bot improvement tests | No |

### 2. Test Result Files - **DELETE**
These are test output files that shouldn't be in version control:

| File | Action | Justification |
|------|--------|---------------|
| `test_results_detailed_20250626_021409.json` | Delete | Test output, regenerate as needed |
| `test_results_summary_20250626_021409.json` | Delete | Test output, regenerate as needed |

### 3. Log Files - **DELETE FROM GIT, ADD TO .gitignore**
Logs should not be tracked in version control:

| Directory/File | Action | Justification |
|------|--------|---------------|
| `logs/` entire directory | Delete from git, add to .gitignore | Runtime logs don't belong in repo |
| `quality_improvements.log` | Delete | Log file in root directory |

### 4. Migration/Documentation Files - **CONSOLIDATE**
Multiple migration and improvement documents can be consolidated:

| File | Action | Justification | Merge Into |
|------|--------|---------------|------------|
| `MIGRATION_GUIDE.md` | Keep | Main migration guide | - |
| `MIGRATION_INSTRUCTIONS.md` | Delete | Duplicate content | `MIGRATION_GUIDE.md` |
| `MIGRATION_STATUS.md` | Move to `docs/` | Status tracking document | - |
| `INFRASTRUCTURE_MIGRATION.md` | Move to `docs/` | Infrastructure specific | - |
| `INTERNAL_IMPROVEMENT_PLAN.md` | Move to `docs/` | Internal documentation | - |
| `RESPONSE_LENGTH_ENHANCEMENTS.md` | Move to `docs/improvements/` | Feature improvement doc | - |
| `X_PREMIUM_IMPROVEMENTS.md` | Move to `docs/improvements/` | Feature improvement doc | - |
| `MARKET_MATCHING_FIXES_REPORT.md` | Move to `docs/improvements/` | Bug fix documentation | - |
| `PREMIUM_API_TESTING_PROTOCOL.md` | Move to `docs/testing/` | Testing protocol | - |
| `TWITTER_BOT_IMPROVEMENTS.md` | Move to `docs/improvements/` | Feature improvement doc | - |
| `DSPY_INTEGRATION_SUCCESS.md` | Move to `docs/improvements/` | Integration documentation | - |
| `LLM_MARKET_MATCHING.md` | Move to `docs/improvements/` | **NEW** - LLM matching documentation | - |

### 5. Flow Files - **CONSOLIDATE AND CLARIFY**
Multiple flow implementations need clarification:

| File | Action | Justification | Notes |
|------|--------|---------------|-------|
| `src/flows/enhanced_aigg_flow.py` | Keep | Main production flow | Primary |
| `src/flows/dspy_enhanced_aigg_flow.py` | Keep | DSPy-enhanced version | **UPDATED** - Active development |
| `src/flows/api_first_flow.py` | Archive or Delete | Check if still used | May be deprecated |
| `src/flows/database_first_flow.py` | Archive or Delete | Check if still used | May be deprecated |
| `src/flows/llm_market_matcher.py` | Keep | **NEW** - LLM-based matcher | Latest commit addition |
| `docs/archive/enhanced_flow.py` | Delete | Already archived | Redundant |

### 6. Script Files - **ORGANIZE**
Shell scripts and utility files:

| File | Action | Justification | Breaking? |
|------|--------|---------------|-----------|
| `check_status.sh` | Move to `scripts/` | Utility script | Update docs |
| `run_streamlit.sh` | Move to `scripts/` | Development script | Update docs |
| `start_services.sh` | Move to `scripts/` | Service management | Update systemd |
| `cleanup_old_markets.py` | Already in `scripts/` | Properly located | No |
| `continuous_improvement.py` | Move to `scripts/` or `src/utils/` | Utility script | No |
| `external_client.py` | Move to `examples/` | Example code | No |

### 7. Configuration Files - **CLEAN UP**
Environment and config files:

| File | Action | Justification |
|------|--------|---------------|
| `.env` | Keep (ensure in .gitignore) | Local configuration |
| `.env.example` | Keep | Template for developers |
| `api/.env` | Delete (ensure in .gitignore) | Should not be tracked |
| `vinnie.json` | Move to `config/` or Delete | Unclear purpose, needs investigation |

### 8. Documentation Structure - **REORGANIZE**

Current structure is flat. Suggested new structure:
```
docs/
├── setup/
│   ├── TWITTER_ACCOUNT_SETUP.md
│   ├── TWITTER_SETUP.md
│   └── TWITTER_DEPLOYMENT_CHECKLIST.md
├── improvements/
│   ├── RESPONSE_LENGTH_ENHANCEMENTS.md
│   ├── X_PREMIUM_IMPROVEMENTS.md
│   ├── MARKET_MATCHING_FIXES_REPORT.md
│   ├── TWITTER_BOT_IMPROVEMENTS.md
│   ├── DSPY_INTEGRATION_SUCCESS.md
│   └── LLM_MARKET_MATCHING.md
├── migration/
│   ├── MIGRATION_GUIDE.md
│   ├── MIGRATION_STATUS.md
│   └── INFRASTRUCTURE_MIGRATION.md
├── testing/
│   └── PREMIUM_API_TESTING_PROTOCOL.md
├── api/
│   └── TWITTER_INTEGRATION_SUMMARY.md
└── archive/
    └── [existing archive files]
```

### 9. Reference Directory - **EVALUATE**
| Directory | Action | Justification |
|------|--------|---------------|
| `reference/langchain-doc-graph/` | Evaluate | Large reference implementation - check if actively used |

### 10. Unused/Unclear Files - **INVESTIGATE**
| File | Action | Justification |
|------|--------|---------------|
| `vinnie.json` | Investigate purpose | Appears to be test data |
| `langsearch/` directory | Investigate | Separate project? Consider moving out |
| `.DS_Store` | Delete and add to .gitignore | MacOS system file |

### 11. API Directory - **ORGANIZE**
The `api/` directory structure needs minor adjustments:

| File | Action | Justification |
|------|--------|---------------|
| `api/main.py` | Keep | **UPDATED** - Main API server |
| `api/insights.py` | Keep | API insights module |
| `api/llm_search_endpoint.py` | Move to `api/endpoints/` or integrate | **NEW** - Separate endpoint file |
| `api/.env` | Delete from tracking | Should not be in git |
| `api/output_logs/` | Add to .gitignore | Runtime output |

### 12. Utility Files - **NEW ADDITIONS**
New utility modules added in latest commit:

| File | Action | Justification |
|------|--------|---------------|
| `src/utils/dspy_utilities.py` | Keep | **NEW** - DSPy utility functions |

### 13. Systemd Files - **KEEP**
| File | Action | Justification |
|------|--------|---------------|
| `systemd/` directory | Keep | Deployment configuration |

## Summary of Latest Changes (Commit 650cd96)

The latest commit added significant LLM-based market matching functionality:
- **4 new test files** added to root (need organizing)
- **New flow**: `llm_market_matcher.py` for LLM-based matching
- **New utilities**: `dspy_utilities.py` for DSPy support
- **New API endpoint**: `llm_search_endpoint.py` (should be integrated or moved)
- **Updated files**: `api/main.py` and `dspy_enhanced_aigg_flow.py`
- **New documentation**: `LLM_MARKET_MATCHING.md`

## Implementation Priority

1. **High Priority** (Do First):
   - Delete all log files from git
   - Update .gitignore with logs/, *.log, .DS_Store, .env files
   - Move all test_*.py files to organized test directory (now 12 files total)

2. **Medium Priority**:
   - Consolidate migration documents
   - Reorganize documentation structure
   - Move utility scripts to scripts/

3. **Low Priority**:
   - Investigate and clean up unclear files
   - Archive deprecated flow implementations
   - Evaluate reference directory necessity

## Breaking Changes Summary

Most changes are non-breaking, but these require attention:
- Moving shell scripts may require updating:
  - systemd service files
  - Documentation
  - CI/CD pipelines
- Any active imports of test files will need path updates

## Recommended .gitignore Additions
```
# Logs
logs/
*.log

# Test outputs
test_results_*.json

# OS files
.DS_Store

# Environment files
.env
api/.env

# Output directories
api/output_logs/
```

## Next Steps
1. Review this plan with the team
2. Create a backup branch before cleanup
3. Execute cleanup in priority order
4. Update all documentation references
5. Test all functionality after cleanup