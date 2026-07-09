# Analyzer Details

Per-analyzer violation heuristics and example output, moved verbatim from SKILL.md. Read when you need to explain WHY the assessment flagged something or what an analyzer checks.

## Features

### 1. Project Type Detection

Automatically detects project type and framework:

**Supported Project Types:**
- **Next.js** - App Router and Pages Router
- **Python** - FastAPI, Django, Flask, general Python
- **Node.js** - Express, NestJS, general Node
- **React** - Vite, Create React App
- **Vue** - Nuxt, Vue CLI
- **Angular** - Angular CLI

**Detection Strategy:**
1. Analyzes package.json, requirements.txt, pyproject.toml
2. Checks for framework-specific patterns (next.config.js, django settings)
3. Examines directory structure (app/, pages/, src/)
4. Validates configuration files

**Example Output:**
```markdown
## Project Detection

**Project Type**: Next.js (App Router)
**Framework Version**: 14.0.3
**Architecture Pattern**: Three-tier (Route Handlers → Service Layer → Data Layer)
```

---

### 2. Layer Separation Analysis

Validates Clean Architecture layer separation:

**Three-Tier Architecture:**
1. **Presentation Layer** - Routes, controllers, UI components
2. **Business Layer** - Services, domain logic, use cases
3. **Data Layer** - Database access, external APIs, repositories

**Violation Detection:**
- SQL queries in presentation layer (route handlers)
- Direct database access from UI components
- Business logic in data access objects
- Cross-layer tight coupling

**Example Violations:**
```markdown
### Layer Separation Violations (3)

**CRITICAL**: SQL in API Route
- File: `src/app/api/users/route.ts`
- Line: 12
- Issue: Direct SQL query in route handler
- Recommendation: Move to service layer

**HIGH**: Business Logic in Database Layer
- File: `src/lib/db/user-repository.ts`
- Line: 45
- Issue: User validation logic in repository
- Recommendation: Move to service layer
```

---

### 3. SOLID Principles Analysis

Checks compliance with all 5 SOLID principles:

#### Single Responsibility Principle (SRP)
Detects classes/modules with multiple responsibilities.

**Violations:**
- Classes with > 500 LOC
- Modules with > 10 public methods
- Files doing both business logic + data access

#### Open/Closed Principle (OCP)
Detects hardcoded conditional logic that should use polymorphism.

**Violations:**
- Large if/else chains (> 5 branches)
- Switch statements on type fields
- Repeated instanceof checks

#### Liskov Substitution Principle (LSP)
Detects inheritance violations.

**Violations:**
- Subclasses throwing NotImplementedError
- Overridden methods changing behavior contracts
- Subclasses requiring more preconditions

#### Interface Segregation Principle (ISP)
Detects overly large interfaces.

**Violations:**
- Interfaces with > 10 methods
- Implementations with empty stub methods
- Fat interfaces forcing unnecessary dependencies

#### Dependency Inversion Principle (DIP)
Detects direct dependencies on concrete implementations.

**Violations:**
- Direct imports of database clients in business logic
- Hardcoded external API URLs
- Tight coupling to specific libraries

**Example Output:**
```markdown
### SOLID Principles Compliance

**Overall Score**: 72/100 (Medium)

**Single Responsibility**: 65/100 (4 violations)
**Open/Closed**: 80/100 (2 violations)
**Liskov Substitution**: 90/100 (1 violation)
**Interface Segregation**: 75/100 (3 violations)
**Dependency Inversion**: 50/100 (6 violations) ⚠️
```

---

### 4. Design Pattern Detection

Identifies common design patterns and anti-patterns:

**Recognized Patterns:**
- **Repository Pattern** - Data access abstraction
- **Factory Pattern** - Object creation delegation
- **Strategy Pattern** - Algorithm encapsulation
- **Singleton Pattern** - Single instance management
- **Observer Pattern** - Event-driven architecture
- **Dependency Injection** - Inversion of Control

**Anti-Patterns Detected:**
- **God Object** - Classes with excessive responsibilities
- **Spaghetti Code** - Unstructured control flow
- **Tight Coupling** - Excessive inter-module dependencies
- **Magic Numbers** - Hardcoded values without constants

**Example Output:**
```markdown
### Design Patterns

**Detected Patterns (5)**:
✅ Repository Pattern - `lib/repositories/*`
✅ Factory Pattern - `lib/factories/user-factory.ts`
✅ Strategy Pattern - `lib/strategies/auth-strategy.ts`
✅ Dependency Injection - Constructor-based DI throughout

**Anti-Patterns (3)**:
❌ God Object - `src/lib/user-manager.ts` (1,200 LOC, 25 methods)
❌ Tight Coupling - `src/api/orders.ts` → 15 direct dependencies
❌ Magic Numbers - `src/lib/pricing.ts` (8 hardcoded constants)
```

---

### 5. Dependency Management

Analyzes module dependencies and coupling:

**Coupling Metrics:**
- **FAN-IN** - Number of modules depending on this module (higher = more central)
- **FAN-OUT** - Number of modules this module depends on (higher = more coupled)
- **Instability** - FAN-OUT / (FAN-IN + FAN-OUT) (0 = stable, 1 = unstable)

**Circular Dependencies:**
Uses graph algorithms to detect dependency cycles.

**Example Output:**
```markdown
### Coupling Metrics

**Most Coupled Modules** (FAN-OUT > 10):
1. `src/lib/auth-service.ts` - FAN-OUT: 18 (❌ too high)
2. `src/lib/user-service.ts` - FAN-OUT: 15 (⚠️ high)
3. `src/lib/order-service.ts` - FAN-OUT: 12 (⚠️ high)

**Circular Dependencies (2)**:
1. `src/lib/user-service.ts` ↔️ `src/lib/auth-service.ts`
2. `src/lib/order-service.ts` → `src/lib/product-service.ts` → `src/lib/inventory-service.ts` → `src/lib/order-service.ts`

**Recommendation**: Break cycles using interface abstractions or event-driven patterns.
```

---

### 6. Code Organization

Validates file structure and naming conventions:

**Checks:**
- File naming consistency (kebab-case, camelCase, PascalCase)
- Directory structure alignment with architecture patterns
- Module size (files > 500 LOC flagged)
- Unused imports/exports
- Public API surface area

**Example Output:**
```markdown
### Code Organization

**File Structure**: ✅ Follows Next.js App Router conventions
**Naming Consistency**: ⚠️ Mixed (kebab-case and camelCase)
**Module Sizes**: ⚠️ 3 files > 500 LOC

**Recommendations**:
- Standardize on kebab-case for file names
- Split large modules:
  - `src/lib/user-service.ts` (842 LOC)
  - `src/lib/order-service.ts` (654 LOC)
  - `src/lib/product-service.ts` (521 LOC)
```

---

### 7. Drift Detection (Memory Bank Integration)

Compares actual architecture vs documented architecture:

**Reads from Memory Bank:**
- `memory-bank/systemPatterns.md` - Documented architecture patterns
- `memory-bank/systemArchitecture.md` - System design decisions

**Detects:**
- Undocumented components (code exists, not in docs)
- Deviation from documented patterns (docs say X, code does Y)
- Deprecated patterns still in use
- New patterns not yet documented

**Example Output:**
```markdown
### Drift from Documented Architecture

**Drift Score**: 23/100 (Low drift = good)

**New Components (Undocumented)**:
- `src/lib/notification-service.ts` (added 2 weeks ago)
- `src/api/webhooks/` (new feature)

**Pattern Deviations**:
- Documentation specifies Repository Pattern
- Found: 8 files with direct database access (bypassing repositories)

**Recommendations**:
1. Document new notification service in systemPatterns.md
2. Update 8 files to use repository pattern
3. Archive deprecated patterns from documentation
```

---
