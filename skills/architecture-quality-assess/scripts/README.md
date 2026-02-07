# Helper Scripts Documentation

This directory contains Python helper scripts that power the Architecture Quality Assessment skill.

---

## Overview

The scripts in this directory provide modular analysis capabilities that can be:
- Called directly from command line for standalone analysis
- Imported as Python modules for integration
- Invoked by the main assessment orchestrator

---

## Scripts

### 1. `detect_project_type.py`

**Purpose**: Detects project type and framework from codebase structure

**Usage**:
```bash
# Detect current directory
python3 scripts/detect_project_type.py

# Detect specific project
python3 scripts/detect_project_type.py /path/to/project

# JSON output
python3 scripts/detect_project_type.py --format json
```

**Output**:
```json
{
  "project_type": "nextjs",
  "framework": "Next.js",
  "framework_version": "14.0.3",
  "architecture_pattern": "app_router",
  "confidence": 0.95,
  "detected_patterns": [
    "next.config.js exists",
    "app/ directory present",
    "package.json has next@14"
  ]
}
```

**Detection Logic**:
1. Checks for manifest files (package.json, requirements.txt, pyproject.toml)
2. Identifies framework-specific markers (next.config.js, django settings)
3. Analyzes directory structure (app/, pages/, src/)
4. Reads framework versions from dependencies
5. Determines architecture pattern (App Router vs Pages Router for Next.js)

**Supported Types**:
- `nextjs` - Next.js (App Router or Pages Router)
- `react` - React (Vite, CRA)
- `vue` - Vue (Nuxt, Vue CLI)
- `angular` - Angular
- `python-fastapi` - FastAPI
- `python-django` - Django
- `python-flask` - Flask
- `nodejs-express` - Express.js
- `nodejs-nestjs` - NestJS
- `unknown` - Unable to determine

**Exit Codes**:
- `0` - Success
- `1` - Project not found
- `2` - Multiple project types detected (ambiguous)

---

### 2. `analyze_coupling.py`

**Purpose**: Analyzes module coupling and calculates FAN-IN/FAN-OUT metrics

**Usage**:
```bash
# Analyze current project
python3 scripts/analyze_coupling.py

# Analyze specific directory
python3 scripts/analyze_coupling.py /path/to/src

# Filter by threshold
python3 scripts/analyze_coupling.py --fan-out-threshold 15

# JSON output
python3 scripts/analyze_coupling.py --format json

# Include circular dependencies
python3 scripts/analyze_coupling.py --detect-cycles
```

**Output**:
```json
{
  "modules": [
    {
      "path": "src/lib/auth-service.ts",
      "fan_in": 8,
      "fan_out": 18,
      "instability": 0.69,
      "dependencies": [
        "src/lib/db.ts",
        "src/lib/user-service.ts",
        "src/types/auth.ts"
      ],
      "dependents": [
        "src/api/login/route.ts",
        "src/api/logout/route.ts"
      ]
    }
  ],
  "summary": {
    "total_modules": 45,
    "average_fan_out": 7.2,
    "max_fan_out": 18,
    "high_coupling_count": 3
  },
  "circular_dependencies": [
    {
      "cycle": [
        "src/lib/user-service.ts",
        "src/lib/auth-service.ts",
        "src/lib/user-service.ts"
      ],
      "length": 2
    }
  ]
}
```

**Metrics**:
- **FAN-IN**: Count of modules depending on this module
  - High FAN-IN = Central/shared module
  - Changes impact many files

- **FAN-OUT**: Count of modules this module depends on
  - High FAN-OUT = Tightly coupled
  - Hard to test, fragile to changes

- **Instability**: FAN-OUT / (FAN-IN + FAN-OUT)
  - 0.0 = Stable (many dependents, few dependencies)
  - 1.0 = Unstable (many dependencies, few dependents)

**Thresholds**:
- FAN-OUT < 10: Good
- FAN-OUT 10-15: Acceptable
- FAN-OUT > 15: Refactor recommended

**Circular Dependency Detection**:
Uses depth-first search to find cycles in dependency graph.
Reports cycles with full path for debugging.

**Exit Codes**:
- `0` - Success, no high coupling
- `1` - High coupling detected (FAN-OUT > threshold)
- `2` - Circular dependencies found
- `3` - Both high coupling and cycles

---

### 3. `analyze_layer_separation.py`

**Purpose**: Validates Clean Architecture layer separation

**Usage**:
```bash
# Analyze layer separation
python3 scripts/analyze_layer_separation.py

# Specific project
python3 scripts/analyze_layer_separation.py /path/to/project

# JSON output
python3 scripts/analyze_layer_separation.py --format json

# Custom layer configuration
python3 scripts/analyze_layer_separation.py --config layers.json
```

**Three-Tier Architecture**:
```
Presentation Layer (Routes, Controllers, UI)
         ↓ (can call)
Business Layer (Services, Domain Logic)
         ↓ (can call)
Data Layer (Repositories, Database, APIs)
```

**Violation Detection**:

**Type 1: SQL in Presentation Layer**
```typescript
// ❌ VIOLATION: API route with direct SQL
export async function GET() {
  const users = await db.query('SELECT * FROM users');
  return Response.json(users);
}

// ✅ CORRECT: API route calls service
export async function GET() {
  const users = await userService.getAll();
  return Response.json(users);
}
```

**Type 2: Business Logic in Data Layer**
```python
# ❌ VIOLATION: Validation in repository
class UserRepository:
    def create(self, user_data):
        if not user_data.get('email'):  # Business rule!
            raise ValueError("Email required")
        return db.execute(...)

# ✅ CORRECT: Validation in service
class UserService:
    def create_user(self, user_data):
        if not user_data.get('email'):
            raise ValueError("Email required")
        return user_repo.create(user_data)
```

**Type 3: UI Directly Accessing Data Layer**
```typescript
// ❌ VIOLATION: Component imports repository
import { UserRepository } from '@/lib/db/user-repo';

export function UserList() {
  const users = UserRepository.getAll();
  return <div>{users.map(...)}</div>;
}

// ✅ CORRECT: Component calls service
import { userService } from '@/lib/services/user-service';

export function UserList() {
  const users = userService.getAll();
  return <div>{users.map(...)}</div>;
}
```

**Configuration File** (`layers.json`):
```json
{
  "layers": {
    "presentation": {
      "patterns": ["*/api/**", "*/routes/**", "*/components/**"],
      "can_import": ["business"],
      "cannot_contain": ["sql", "prisma.create", "db.query"]
    },
    "business": {
      "patterns": ["*/services/**", "*/domain/**"],
      "can_import": ["data"],
      "cannot_contain": ["sql"]
    },
    "data": {
      "patterns": ["*/repositories/**", "*/db/**"],
      "can_import": [],
      "cannot_contain": ["validation", "business rules"]
    }
  }
}
```

**Exit Codes**:
- `0` - No violations
- `1` - Layer violations detected

---

### 4. `analyze_solid.py`

**Purpose**: Checks SOLID principles compliance

**Usage**:
```bash
# Analyze SOLID principles
python3 scripts/analyze_solid.py

# Specific directory
python3 scripts/analyze_solid.py /path/to/src

# Focus on specific principle
python3 scripts/analyze_solid.py --principle SRP
python3 scripts/analyze_solid.py --principle DIP

# JSON output
python3 scripts/analyze_solid.py --format json
```

**Principles Analyzed**:

**1. Single Responsibility Principle (SRP)**
- Detects classes > 500 LOC
- Detects modules with > 10 public methods
- Flags files doing multiple things (auth + db + validation)

**2. Open/Closed Principle (OCP)**
- Detects large if/else chains (> 5 branches)
- Detects switch statements on type fields
- Suggests strategy pattern for extensibility

**3. Liskov Substitution Principle (LSP)**
- Detects subclasses throwing NotImplementedError
- Detects changed method signatures in subclasses
- Flags broken inheritance hierarchies

**4. Interface Segregation Principle (ISP)**
- Detects interfaces with > 10 methods
- Detects implementations with empty stub methods
- Suggests smaller, focused interfaces

**5. Dependency Inversion Principle (DIP)**
- Detects direct imports of database clients
- Detects hardcoded API URLs
- Suggests dependency injection

**Output**:
```json
{
  "summary": {
    "overall_score": 72,
    "violations_count": 16
  },
  "principles": {
    "SRP": {
      "score": 65,
      "violations": [
        {
          "file": "src/lib/user-manager.ts",
          "line": 1,
          "severity": "high",
          "issue": "Class has 1,200 LOC and 25 methods",
          "recommendation": "Split into UserService, UserValidator, UserRepository"
        }
      ]
    },
    "DIP": {
      "score": 50,
      "violations": [
        {
          "file": "src/lib/auth-service.ts",
          "line": 12,
          "severity": "critical",
          "issue": "Direct import of Prisma client",
          "recommendation": "Inject database dependency via constructor"
        }
      ]
    }
  }
}
```

**Exit Codes**:
- `0` - All principles satisfied
- `1` - Violations detected

---

### 5. `analyze_design_patterns.py`

**Purpose**: Detects design patterns and anti-patterns

**Usage**:
```bash
# Detect patterns
python3 scripts/analyze_design_patterns.py

# Specific directory
python3 scripts/analyze_design_patterns.py /path/to/src

# Only detect anti-patterns
python3 scripts/analyze_design_patterns.py --anti-patterns-only

# JSON output
python3 scripts/analyze_design_patterns.py --format json
```

**Recognized Patterns**:

**Repository Pattern**:
```typescript
// Detected by: "repository" in filename + CRUD methods
export class UserRepository {
  async findById(id: string) { }
  async findAll() { }
  async create(data: User) { }
  async update(id: string, data: User) { }
  async delete(id: string) { }
}
```

**Factory Pattern**:
```typescript
// Detected by: "factory" in filename + create methods
export class UserFactory {
  static createAdmin(data: UserData): AdminUser { }
  static createCustomer(data: UserData): Customer { }
}
```

**Strategy Pattern**:
```typescript
// Detected by: interface + multiple implementations
export interface AuthStrategy {
  authenticate(credentials: Credentials): Promise<User>;
}

export class JWTAuthStrategy implements AuthStrategy { }
export class OAuth2AuthStrategy implements AuthStrategy { }
```

**Dependency Injection**:
```typescript
// Detected by: constructor parameters typed as interfaces
export class UserService {
  constructor(
    private userRepo: IUserRepository,
    private emailService: IEmailService
  ) {}
}
```

**Anti-Patterns**:

**God Object**:
```typescript
// Detected by: > 1000 LOC or > 20 methods
export class UserManager {
  // 1,200 lines, 25 methods
  // Does: validation, auth, email, db, logging, etc.
}
```

**Tight Coupling**:
```typescript
// Detected by: FAN-OUT > 15
import a from './a';
import b from './b';
// ... 16 more imports
```

**Magic Numbers**:
```typescript
// Detected by: numeric literals in business logic
if (user.age > 18) { }  // Should be const ADULT_AGE = 18
if (price * 0.2 > 100) { }  // Should be const TAX_RATE = 0.2
```

**Exit Codes**:
- `0` - Patterns found, no anti-patterns
- `1` - Anti-patterns detected

---

### 6. `generate_task_list.py`

**Purpose**: Generates refactoring task list from violations

**Usage**:
```bash
# Generate from violations JSON
python3 scripts/generate_task_list.py violations.json

# Specify output file
python3 scripts/generate_task_list.py violations.json --output tasks.md

# Priority filtering
python3 scripts/generate_task_list.py violations.json --priority P0,P1
```

**Input Format** (`violations.json`):
```json
{
  "violations": [
    {
      "id": "LSV-001",
      "category": "layer_separation",
      "severity": "critical",
      "title": "SQL in API Route",
      "file": "src/app/api/users/route.ts",
      "line": 12,
      "recommendation": "Move to service layer"
    }
  ]
}
```

**Output Format** (`tasks.md`):
```markdown
# Architecture Refactoring Tasks

## Phase 1: Critical Fixes (Priority P0)

### Task 1: Move SQL to Service Layer
**File**: src/app/api/users/route.ts
**Issue**: Direct database access in route handler (LSV-001)
**Action**:
1. Create UserService.getUserList() method
2. Move SQL query to service
3. Update route to call service method
**Verification**:
- [ ] Route only calls service method
- [ ] Service has proper error handling
- [ ] Tests pass
**Estimated Time**: 1 hour

### Task 2: Break Circular Dependency
**Files**: src/lib/user-service.ts ↔️ src/lib/auth-service.ts
**Issue**: Circular import prevents testing (CD-001)
**Action**:
1. Extract shared types to src/types/auth.ts
2. Use interfaces instead of concrete imports
3. Apply dependency injection
**Verification**:
- [ ] No circular imports remain
- [ ] Both services can be tested independently
- [ ] Tests pass
**Estimated Time**: 2 hours

## Phase 2: High Priority (Priority P1)

[...]
```

**Task Prioritization**:
- **P0 (Critical)**: Blocks development, security issues
- **P1 (High)**: Impacts maintainability significantly
- **P2 (Medium)**: Improvements, future maintenance
- **P3 (Low)**: Nice-to-have, cleanup

**Effort Estimation**:
Based on violation complexity:
- Simple (e.g., rename): 15-30 min
- Moderate (e.g., extract method): 1-2 hours
- Complex (e.g., redesign module): 4-8 hours

**Exit Codes**:
- `0` - Task list generated
- `1` - Invalid input JSON

---

## Common Workflows

### Workflow 1: Full Assessment

```bash
# Step 1: Detect project type
python3 scripts/detect_project_type.py > project-type.json

# Step 2: Analyze all dimensions
python3 scripts/analyze_coupling.py --format json > coupling.json
python3 scripts/analyze_layer_separation.py --format json > layers.json
python3 scripts/analyze_solid.py --format json > solid.json
python3 scripts/analyze_design_patterns.py --format json > patterns.json

# Step 3: Combine violations
cat coupling.json layers.json solid.json patterns.json | \
  python3 scripts/combine_violations.py > violations.json

# Step 4: Generate task list
python3 scripts/generate_task_list.py violations.json --output tasks.md

# Step 5: View results
cat tasks.md
```

---

### Workflow 2: Quick Coupling Check

```bash
# Just check coupling, no full assessment
python3 scripts/analyze_coupling.py --fan-out-threshold 15

# If violations found, generate focused task list
python3 scripts/analyze_coupling.py --format json | \
  python3 scripts/generate_task_list.py --priority P0 > coupling-tasks.md
```

---

### Workflow 3: CI/CD Integration

```bash
# Exit code-based quality gate
python3 scripts/analyze_coupling.py --detect-cycles
if [ $? -eq 2 ]; then
  echo "Circular dependencies detected - blocking merge"
  exit 1
fi

python3 scripts/analyze_layer_separation.py
if [ $? -eq 1 ]; then
  echo "Layer violations detected - blocking merge"
  exit 1
fi

echo "Architecture quality checks passed ✅"
```

---

## Advanced Usage

### Custom Rules Configuration

Create `rules.json`:
```json
{
  "coupling": {
    "max_fan_out": 20,
    "max_fan_in": 30,
    "detect_cycles": true
  },
  "solid": {
    "max_class_loc": 800,
    "max_methods": 15
  },
  "layers": {
    "allow_sql_in_routes": false,
    "enforce_repository_pattern": true
  }
}
```

Use with scripts:
```bash
python3 scripts/analyze_coupling.py --config rules.json
python3 scripts/analyze_solid.py --config rules.json
```

---

### Caching Results

```bash
# Enable caching for faster repeated runs
export ARCH_ASSESS_CACHE_DIR=".cache/arch-assess"

python3 scripts/analyze_coupling.py --cache
# Second run is ~80% faster

# Clear cache
rm -rf .cache/arch-assess
```

---

### Parallel Execution

```bash
# Run all analyses in parallel
(
  python3 scripts/analyze_coupling.py --format json > coupling.json &
  python3 scripts/analyze_layer_separation.py --format json > layers.json &
  python3 scripts/analyze_solid.py --format json > solid.json &
  python3 scripts/analyze_design_patterns.py --format json > patterns.json &
  wait
)

echo "All analyses complete"
```

---

## Testing Scripts

All scripts include self-tests:

```bash
# Run tests for individual script
python3 -m pytest scripts/test_detect_project_type.py

# Run all script tests
python3 -m pytest scripts/test_*.py

# Run with coverage
python3 -m pytest --cov=scripts scripts/test_*.py
```

---

## Dependencies

**Required** (Standard library only):
- `pathlib` - File path operations
- `json` - JSON parsing
- `argparse` - Command-line argument parsing
- `ast` - Python AST parsing (for Python projects)
- `re` - Regular expressions

**Optional**:
- `networkx` - Enhanced circular dependency detection
- `tree-sitter` - Multi-language AST parsing
- `pytest` - For running tests

**Install optional dependencies**:
```bash
pip install networkx tree-sitter pytest
```

---

## Exit Code Reference

| Code | Meaning | Scripts |
|------|---------|---------|
| 0 | Success / No issues | All |
| 1 | Violations detected | Most analysis scripts |
| 2 | Circular dependencies | analyze_coupling.py |
| 3 | Both coupling + cycles | analyze_coupling.py |
| 4 | Invalid input | generate_task_list.py |

---

## Performance Tips

1. **Exclude unnecessary files**:
   ```bash
   --exclude "node_modules,dist,build,*.test.ts"
   ```

2. **Use caching**:
   ```bash
   --cache
   ```

3. **Target specific directories**:
   ```bash
   python3 scripts/analyze_coupling.py src/lib/
   ```

4. **Run analyses in parallel** (see Advanced Usage)

---

## Troubleshooting

**Issue**: "Module not found" error
**Fix**: Ensure you're running from project root with `python3 scripts/`

**Issue**: "No project type detected"
**Fix**: Ensure manifest files (package.json, requirements.txt) exist

**Issue**: "Permission denied"
**Fix**: Make scripts executable: `chmod +x scripts/*.py`

**Issue**: "Import error" for optional dependencies
**Fix**: Install optional deps: `pip install networkx tree-sitter`

---

## Contributing

To add a new analysis script:

1. Create `scripts/analyze_<feature>.py`
2. Implement consistent interface:
   - `--format json` flag
   - Exit codes (0 = success)
   - JSON output structure
3. Add tests: `scripts/test_analyze_<feature>.py`
4. Update this README
5. Update main SKILL.md

---

**Last Updated**: 2026-02-07
