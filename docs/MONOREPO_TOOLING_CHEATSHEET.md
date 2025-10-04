# Monorepo Tooling Quick Reference Cheat Sheet

## For Z2 Platform Team

This is a condensed reference guide. For full analysis, see [MONOREPO_TOOLING_RECOMMENDATIONS.md](./MONOREPO_TOOLING_RECOMMENDATIONS.md).

---

## TL;DR Decision

```
Current: Yarn Workspaces + Poetry
Recommended: Add Nx (incremental, 3 weeks)
Defer: Bazel/Pants (unless team > 20 or builds > 30 min)
```

---

## When to Use What

| Scenario | Use Nx | Use Bazel/Pants |
|----------|--------|-----------------|
| JS/TS dominant codebase | ✅ | ❌ |
| Team < 20 developers | ✅ | ❌ |
| Need quick wins | ✅ | ❌ |
| Python + JS mixed | ✅ | ⚠️ |
| Need hermetic builds | ⚠️ | ✅ |
| Polyglot (3+ languages) | ⚠️ | ✅ |
| Compiled languages (Rust/Go) | ❌ | ✅ |
| Team > 50 developers | ⚠️ | ✅ |
| Build times > 30 min | ⚠️ | ✅ |
| Compliance requirements | ❌ | ✅ |

---

## Nx Quick Start (3 Weeks)

### Week 1: Install & Configure

```bash
# Install Nx
npm install -D nx@latest

# Initialize in existing workspace
npx nx@latest init

# Answer prompts:
# - Enable caching? Yes
# - Enable distributed caching? No (add later)
# - Create nx.json? Yes
```

**Create `nx.json`:**
```json
{
  "tasksRunnerOptions": {
    "default": {
      "runner": "nx/tasks-runners/default",
      "options": {
        "cacheableOperations": ["build", "test", "lint"]
      }
    }
  },
  "targetDefaults": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": ["production", "^production"]
    }
  }
}
```

### Week 2: Configure Projects

**Frontend (`frontend/project.json`):**
```json
{
  "name": "frontend",
  "sourceRoot": "frontend/src",
  "projectType": "application",
  "targets": {
    "build": {
      "executor": "@nx/vite:build",
      "outputs": ["{projectRoot}/dist"]
    },
    "test": {
      "executor": "@nx/vite:test"
    },
    "lint": {
      "executor": "nx:run-commands",
      "options": {
        "command": "eslint . --ext ts,tsx",
        "cwd": "{projectRoot}"
      }
    }
  }
}
```

**Backend (Custom Executor):**
```json
{
  "name": "backend",
  "sourceRoot": "backend/app",
  "projectType": "application",
  "targets": {
    "test": {
      "executor": "nx:run-commands",
      "options": {
        "command": "poetry run pytest",
        "cwd": "{projectRoot}"
      }
    },
    "lint": {
      "executor": "nx:run-commands",
      "options": {
        "command": "poetry run ruff check .",
        "cwd": "{projectRoot}"
      }
    }
  }
}
```

### Week 3: CI/CD Integration

**Update `.github/workflows/ci-cd.yml`:**
```yaml
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Nx needs full git history
      
      - uses: nrwl/nx-set-shas@v4
      
      - name: Install dependencies
        run: yarn install
      
      # Only build/test what changed
      - name: Run affected tasks
        run: npx nx affected -t build test lint --parallel=3
```

---

## Common Nx Commands

### Running Tasks
```bash
# Run single task
nx run frontend:build
nx run backend:test

# Run for all affected projects (based on git changes)
nx affected -t build
nx affected -t test --parallel=3

# Run for all projects
nx run-many -t build test --all

# Run with specific base
nx affected -t build --base=origin/main --head=HEAD
```

### Caching
```bash
# Clear cache
nx reset

# Skip cache for a run
nx run frontend:build --skip-nx-cache
```

### Visualization
```bash
# Show project graph
nx graph

# Show affected graph
nx affected:graph

# Show task graph for a specific target
nx graph --target=build
```

### Generators
```bash
# Create new React app
nx generate @nx/react:app my-app

# Create new library
nx generate @nx/react:lib my-lib

# List available generators
nx list @nx/react
```

---

## Cost Comparison (Year 1)

| Option | Setup Cost | Running Cost | Time Savings | ROI |
|--------|-----------|--------------|--------------|-----|
| **Current** | $0 | $0 | 0% | - |
| **Nx (self-hosted)** | $15k | $0 | 50% faster | +154% |
| **Nx Cloud** | $15k | $1.1k | 60% faster | +180% |
| **Bazel** | $90k | $30k | 70% faster | -42% |

*Based on 5-developer team*

---

## Red Flags: When NOT to Change

❌ Build times < 5 minutes  
❌ Team size < 5 developers  
❌ CI/CD works reliably  
❌ No coordination issues  
❌ Focus on shipping features  

**Action:** Optimize current setup instead of adding new tools.

---

## Green Lights: When to Add Nx

✅ Build times 10-30 minutes  
✅ Team size 5-20 developers  
✅ Wanting better caching  
✅ Need task orchestration  
✅ Planning to add more projects  

**Action:** Start 3-week Nx pilot.

---

## Yellow Lights: When to Consider Bazel/Pants

⚠️ Build times > 30 minutes  
⚠️ Team size > 20 developers  
⚠️ Hermetic builds required  
⚠️ Polyglot with compiled languages  
⚠️ Can dedicate 3 months to migration  

**Action:** Prototype Bazel in isolated service first.

---

## Z2-Specific Notes

### Contract Validation
```bash
# Add to nx.json targetDefaults
"validate-contracts": {
  "executor": "nx:run-commands",
  "options": {
    "command": "node scripts/validate-contracts.js"
  }
}

# Run before build
nx run contracts:validate-contracts
nx run-many -t validate-contracts build
```

### Railway Deployment
- **Keep Railway's Docker build** (don't use Bazel containers)
- **Use Nx for local/CI** (Railway handles production)
- **Nx outputs** → Railway containerizes → Deploy

### Feature-Based Architecture
```bash
# Nx aligns with feature-based structure
nx generate @nx/react:lib feature-auth --directory=libs/features
nx generate @nx/react:lib feature-dashboard --directory=libs/features
```

---

## Migration Checklist

### Nx Migration (3 weeks)

#### Week 1
- [ ] Install Nx: `npm install -D nx@latest`
- [ ] Run `npx nx@latest init`
- [ ] Create `nx.json` with caching config
- [ ] Test with one project: `nx run frontend:build`

#### Week 2
- [ ] Create `project.json` for all workspaces
- [ ] Configure task dependencies
- [ ] Test affected: `nx affected -t build`
- [ ] Verify cache: Run build twice, check time

#### Week 3
- [ ] Update CI/CD to use `nx affected`
- [ ] Train team (1-day workshop)
- [ ] Document in contributor guide
- [ ] Measure baseline metrics (build time, cache hits)

### Bazel Migration (3 months) - NOT RECOMMENDED NOW

#### Month 1: Prototype
- [ ] Install Bazel: `npm install -g @bazel/bazelisk`
- [ ] Create WORKSPACE/MODULE.bazel
- [ ] Write BUILD files for 1 service
- [ ] Test build: `bazel build //frontend:bundle`
- [ ] Evaluate: Is this worth it?

#### Month 2: Migrate (if prototype succeeded)
- [ ] Convert all BUILD files
- [ ] Write custom rules for Vite/Poetry
- [ ] Migrate CI/CD
- [ ] Team training (2 weeks)

#### Month 3: Stabilize
- [ ] Fix build issues
- [ ] Optimize cache
- [ ] Document extensively
- [ ] Support team

---

## Performance Expectations

### Current Setup
- **Cold build:** 5-10 minutes
- **Incremental build:** 3-5 minutes (manual)
- **CI time:** 8-12 minutes
- **Cache hit rate:** 0% (no caching)

### With Nx (Estimated)
- **Cold build:** 5-10 minutes (same)
- **Incremental build:** 30 seconds (cache hit)
- **CI time (affected only):** 2-4 minutes
- **Cache hit rate:** 70-80%
- **Time savings:** 50-60%

### With Bazel (Estimated)
- **Cold build:** 8-15 minutes (initial overhead)
- **Incremental build:** 10 seconds (fine-grained cache)
- **CI time (affected only):** 1-2 minutes
- **Cache hit rate:** 90-95%
- **Time savings:** 70-80%
- **Migration pain:** 3 months of reduced velocity

---

## Decision Tree

```
Q1: Are builds painful?
├─ NO → Stay with current setup ✅
└─ YES → Continue

Q2: Is team < 20 developers?
├─ YES → Use Nx ✅
└─ NO → Continue

Q3: Need hermetic builds?
├─ NO → Use Nx ✅
└─ YES → Continue

Q4: Can dedicate 3 months?
├─ NO → Use Nx ✅
└─ YES → Consider Bazel

Q5: Have Bazel expertise?
├─ NO → Use Nx ✅ (hire consultant if choosing Bazel)
└─ YES → Consider Bazel
```

**For Z2 right now: Nx ✅**

---

## Useful Links

### Nx
- Docs: https://nx.dev
- Getting Started: https://nx.dev/getting-started/intro
- Nx Cloud: https://nx.app
- Recipes: https://nx.dev/recipes

### Bazel
- Docs: https://bazel.build
- Getting Started: https://bazel.build/start
- Rules: https://github.com/bazelbuild/rules_nodejs
- Bzlmod: https://bazel.build/external/migration

### Pants
- Docs: https://www.pantsbuild.org
- Getting Started: https://www.pantsbuild.org/docs/getting-started

### Python Tools
- uv: https://github.com/astral-sh/uv
- Poetry: https://python-poetry.org

---

## Key Takeaways

1. **Nx is right for Z2 now** (JS-heavy, small team, fast iteration)
2. **Start with 3-week pilot** (low risk, high value)
3. **Defer Bazel** until team > 20 or builds > 30 min
4. **Measure success** (build time, cache hits, developer happiness)
5. **Re-evaluate every 6 months** as team/codebase grows

---

**Next Steps:**
1. Read full recommendations: [MONOREPO_TOOLING_RECOMMENDATIONS.md](./MONOREPO_TOOLING_RECOMMENDATIONS.md)
2. Discuss with team (30-min meeting)
3. Approve Nx pilot (or defer)
4. Assign Nx champion
5. Start Week 1 setup

---

**Questions?** Ask in #engineering channel or open a GitHub Discussion.
