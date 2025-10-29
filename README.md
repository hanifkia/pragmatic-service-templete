# Pragmatic Clean Architecture Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Core Principles](#core-principles)
3. [Directory Structure](#directory-structure)
4. [Layer Documentation](#layer-documentation)
5. [Development Workflow](#development-workflow)
6. [Examples](#examples)

---

## Architecture Overview

### What is Pragmatic Clean Architecture?

This is a **simplified Clean Architecture** optimized for solo developers building scalable FastAPI services. It balances simplicity with flexibility, allowing technology changes with minimal code modifications.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │            API (FastAPI Endpoints)                  │    │
│  │  • HTTP Request Handling                            │    │
│  │  • Input Validation (Pydantic Schemas)              │    │
│  │  • Response Formatting                              │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                      BUSINESS LAYER                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │              CORE (Domain Logic)                    │    │
│  │  • Services (Business Logic)                        │    │
│  │  • Models (Domain Entities)                         │    │
│  │  • Interfaces (Abstract Contracts)                  │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │            ADAPTERS (Implementations)               │    │
│  │  • Database (Postgres, MongoDB, etc.)               │    │
│  │  • Cache (Redis, Memcached, etc.)                   │    │
│  │  • Queue (RabbitMQ, Kafka, etc.)                    │    │
│  │  • Storage (S3, Local, etc.)                        │    │
│  │  • External Services (Email, SMS, etc.)             │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Dependency Rule

**Dependencies flow INWARD only:**
- API depends on Core
- Core depends on NOTHING (pure business logic)
- Adapters depend on Core interfaces
- Core NEVER depends on Adapters

---

## Core Principles

### 1. **Separation of Concerns**
Each layer has a single, well-defined responsibility.

### 2. **Dependency Inversion**
High-level modules don't depend on low-level modules. Both depend on abstractions (interfaces).

### 3. **Technology Agnostic**
Core business logic is independent of frameworks, databases, or external services.

### 4. **Testability**
Each layer can be tested independently using mocks.

### 5. **Scalability**
Architecture supports horizontal scaling, caching, and async processing.

---

## Directory Structure

```
project_root/
├── src/
│   ├── api/                    # Presentation Layer
│   │   ├── v1/
│   │   │   ├── endpoints/      # Route handlers
│   │   │   ├── schemas.py      # Request/Response models
│   │   │   ├── dependencies.py # API-level dependencies
│   │   │   └── router.py       # Router aggregator
│   │   ├── middleware.py       # HTTP middleware
│   │   └── exceptions.py       # API exceptions
│   │
│   ├── core/                   # Business Layer
│   │   ├── services/           # Business logic
│   │   ├── models/             # Domain entities
│   │   ├── interfaces/         # Abstract contracts
│   │   ├── exceptions.py       # Domain exceptions
│   │   └── validators.py       # Business validators
│   │
│   ├── adapters/               # Infrastructure Layer
│   │   ├── database/           # DB implementations
│   │   ├── cache/              # Cache implementations
│   │   ├── queue/              # Queue implementations
│   │   ├── storage/            # Storage implementations
│   │   └── external/           # External API clients
│   │
│   ├── config/                 # Configuration
│   │   ├── settings.py         # Application settings
│   │   ├── dependencies.py     # Dependency injection
│   │   └── logging.py          # Logging configuration
│   │
│   ├── utils/                  # Utilities
│   │   ├── security.py         # Security helpers
│   │   ├── datetime.py         # Date/time helpers
│   │   └── pagination.py       # Pagination helpers
│   │
│   └── main.py                 # Application entry point
│
├── tests/                      # Test suite
├── migrations/                 # Database migrations
├── scripts/                    # Utility scripts
├── docs/                       # Documentation
└── docker/                     # Docker configurations
```

---

## Layer Documentation

### 1. Presentation Layer (`src/api/`)

**Purpose:** Handle HTTP requests and responses, input validation, and API versioning.

**Responsibilities:**
- Receive HTTP requests
- Validate input using Pydantic schemas
- Call appropriate business services
- Format responses
- Handle HTTP-specific concerns (headers, status codes, etc.)

**Does NOT:**
- Contain business logic
- Access database directly
- Implement algorithms

---

### 2. Business Layer (`src/core/`)

**Purpose:** Contain all business logic and domain rules.

**Responsibilities:**
- Implement business operations
- Enforce business rules
- Coordinate between repositories
- Define domain models
- Define interfaces for external dependencies

**Does NOT:**
- Know about HTTP, databases, or external services
- Import from `api/` or `adapters/`
- Handle technical infrastructure concerns

---

### 3. Infrastructure Layer (`src/adapters/`)

**Purpose:** Implement technical details and external integrations.

**Responsibilities:**
- Implement repository interfaces
- Handle database operations
- Manage cache operations
- Integrate with external APIs
- Handle file storage

**Does NOT:**
- Contain business logic
- Make business decisions
- Know about HTTP requests/responses

## Development Workflow

### Adding a New Feature: "Products" Example

#### Step 1: Define Domain Model
```python
# src/core/models/product.py
@dataclass
class Product:
    id: Optional[str]
    name: str
    price: float
    description: str
    created_at: Optional[datetime] = None
```

#### Step 2: Define Repository Interface
```python
# src/core/interfaces/repositories.py
class ProductRepository(ABC):
    @abstractmethod
    async def get_by_id(self, product_id: str) -> Optional[Product]:
        pass
    
    @abstractmethod
    async def create(self, product: Product) -> Product:
        pass
    
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[Product]:
        pass
```

#### Step 3: Create Business Service
```python
# src/core/services/product_service.py
class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo
    
    async def create_product(self, name: str, price: float, description: str) -> Product:
        # Business logic here
        if price < 0:
            raise ValueError("Price cannot be negative")
        
        product = Product(
            id=None,
            name=name,
            price=price,
            description=description
        )
        return await self.product_repo.create(product)
```

#### Step 4: Implement Repository (Database Adapter)
```python
# src/adapters/database/postgres/repositories.py
class PostgresProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, product_id: str) -> Optional[Product]:
        # Postgres implementation
        pass
    
    async def create(self, product: Product) -> Product:
        # Postgres implementation
        pass
```

#### Step 5: Define API Schemas
```python
# src/api/v1/schemas.py
class CreateProductRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)
    description: str

class ProductResponse(BaseModel):
    id: str
    name: str
    price: float
    description: str
    created_at: datetime
```

#### Step 6: Create API Endpoint
```python
# src/api/v1/endpoints/products.py
router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    data: CreateProductRequest,
    product_service: ProductService = Depends(get_product_service)
):
    product = await product_service.create_product(
        name=data.name,
        price=data.price,
        description=data.description
    )
    return ProductResponse.from_domain(product)
```

#### Step 7: Wire Dependencies
```python
# src/config/dependencies.py
async def get_product_repository(
    db: AsyncSession = Depends(get_db)
) -> ProductRepository:
    return PostgresProductRepository(db)

async def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository)
) -> ProductService:
    return ProductService(product_repo)
```

### Flow Summary
```
1. Client Request → 2. API Endpoint → 3. Service → 4. Repository → 5. Database
                  ↓                  ↓           ↓              ↓
              Validation      Business Logic  Interface   Implementation
```

## Switching Technologies Example

### Switching from Postgres to MongoDB

**What needs to change:**

#### 1. Create MongoDB adapter (NEW FILE)
```python
# src/adapters/database/mongodb/repositories.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from core.interfaces.repositories import UserRepository
from core.models.user import User

class MongoUserRepository(UserRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        doc = await self.db.users.find_one({"_id": user_id})
        if not doc:
            return None
        return self._to_domain(doc)
    
    async def create(self, user: User) -> User:
        doc = self._to_document(user)
        result = await self.db.users.insert_one(doc)
        user.id = str(result.inserted_id)
        return user
    
    def _to_domain(self, doc: dict) -> User:
        return User(
            id=str(doc["_id"]),
            email=doc["email"],
            hashed_password=doc["hashed_password"],
            full_name=doc["full_name"],
            is_active=doc["is_active"],
            created_at=doc["created_at"]
        )
```

#### 2. Update dependencies (CHANGE ONE FUNCTION)
```python
# src/config/dependencies.py

# OLD (Postgres)
async def get_user_repository(
    db: AsyncSession = Depends(get_db)
) -> UserRepository:
    return PostgresUserRepository(db)

# NEW (MongoDB) - Just change these lines!
from motor.motor_asyncio import AsyncIOMotorClient

mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
mongo_db = mongo_client[settings.MONGO_DB_NAME]

async def get_user_repository() -> UserRepository:
    return MongoUserRepository(mongo_db)
```

**That's it!** Your API endpoints, business logic, and everything else remains unchanged. ✨

---

## Quick Reference

### File Locations Cheatsheet

| What you want to add | Where it goes |
|----------------------|---------------|
| New API endpoint | `src/api/v1/endpoints/` |
| Request/Response schema | `src/api/v1/schemas.py` |
| Business logic | `src/core/services/` |
| Domain model | `src/core/models/` |
| Repository interface | `src/core/interfaces/` |
| Database implementation | `src/adapters/database/{db_type}/` |
| Cache implementation | `src/adapters/cache/` |
| External API client | `src/adapters/external/` |
| Dependency injection | `src/config/dependencies.py` |
| Utility function | `src/utils/` |
| Unit test | `tests/unit/` |
| Integration test | `tests/integration/` |
| End-to-end test | `tests/e2e/` |

### Common Commands

```bash
# Development
make dev              # Run dev server
make test             # Run all tests
make test-unit        # Run unit tests only
make lint             # Run linters
make format           # Format code

# Docker
make docker-up        # Start services
make docker-down      # Stop services
make docker-logs      # View logs

# Database
make migrate-create msg="add users table"  # Create migration
make migrate-up       # Apply migrations
make seed             # Seed test data
make db-reset         # Reset database

# Deployment
make requirements     # Update requirements.txt
docker build -f docker/Dockerfile.prod -t myapp:latest .
```

### Architecture Decision Records (ADRs)

When making significant architectural decisions, document them:

```markdown
# ADR 001: Use Pragmatic Clean Architecture

## Status
Accepted

## Context
Building scalable FastAPI services as solo developer.
Need balance between simplicity and flexibility.

## Decision
Implement 3-layer architecture with adapters pattern.

## Consequences
✅ Easy to maintain as solo developer
✅ Technology-agnostic core logic
✅ Easy to test
✅ Scalable architecture
⚠️ Slightly more boilerplate than simple approach

---

# ADR 002: Use PostgreSQL as Primary Database

## Status
Accepted

## Context
Need reliable ACID-compliant database for user data.

## Decision
Use PostgreSQL with asyncpg driver.

## Consequences
✅ Strong consistency guarantees
✅ Rich query capabilities
✅ Well-supported ecosystem
⚠️ Can switch to MongoDB later via adapter pattern

---

# ADR 003: Use Redis for Caching

## Status
Accepted

## Context
Need fast caching for session data and API responses.

## Decision
Use Redis with async Python client.

## Consequences
✅ High performance
✅ Simple key-value operations
✅ Built-in expiration
⚠️ Additional infrastructure dependency
```

---

## Onboarding Checklist

### For New Developers

- [ ] Read this architecture documentation
- [ ] Understand the 3-layer structure (API → Core → Adapters)
- [ ] Understand dependency flow (outer → inner)
- [ ] Set up local environment (`make install`)
- [ ] Run tests (`make test`)
- [ ] Run application (`make dev`)
- [ ] Review existing code in each layer
- [ ] Try adding a simple endpoint (follow "Adding New Feature" guide)
- [ ] Review ADRs (Architecture Decision Records)
- [ ] Ask questions in team chat

### Environment Setup

1. **Clone repository**
   ```bash
   git clone <repo-url>
   cd <project>
   ```

2. **Copy environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Install dependencies**
   ```bash
   make install
   ```

4. **Start services**
   ```bash
   make docker-up
   ```

5. **Run migrations**
   ```bash
   make migrate-up
   ```

6. **Seed test data**
   ```bash
   make seed
   ```

7. **Run application**
   ```bash
   make dev
   ```

8. **Open browser**
   ```
   http://localhost:8000/docs
   ```

---

## Best Practices

### DO ✅

1. **Keep core layer pure** - No HTTP, no database, no external dependencies
2. **Use interfaces** - Always define interfaces in core, implement in adapters
3. **Test business logic** - Unit test services with mocks
4. **Keep services thin** - Services coordinate, don't do everything
5. **Use type hints** - Python type hints everywhere
6. **Document decisions** - Use ADRs for architectural choices
7. **Handle errors gracefully** - Use custom exceptions
8. **Log appropriately** - Info for normal flow, error for problems
9. **Use dependency injection** - Don't instantiate dependencies in code
10. **Follow naming conventions** - Be consistent

### DON'T ❌

1. **Don't put business logic in endpoints** - Endpoints validate and delegate
2. **Don't access database from services** - Use repository interfaces
3. **Don't import from outer layers** - Core never imports from API/Adapters
4. **Don't hardcode configuration** - Use environment variables
5. **Don't skip tests** - Especially for business logic
6. **Don't ignore errors** - Always handle exceptions
7. **Don't mix concerns** - Keep layers separate
8. **Don't create god classes** - Small, focused classes
9. **Don't optimize prematurely** - Make it work, then make it fast
10. **Don't forget documentation** - Document complex logic

---

## Troubleshooting

### Common Issues

#### Issue: Import errors
```
Solution: Ensure PYTHONPATH includes src directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### Issue: Database connection fails
```
Solution: Check DATABASE_URL in .env file
Ensure PostgreSQL is running: docker ps
```

#### Issue: Tests fail with "database not found"
```
Solution: Create test database
make db-reset
```

#### Issue: Circular imports
```
Solution: Check import order
- Core should never import from API/Adapters
- Use TYPE_CHECKING for type hints if needed
```

---

## Summary

This Pragmatic Clean Architecture provides:

✅ **Simplicity** - Only 3 layers, easy to understand
✅ **Flexibility** - Swap any technology via adapters
✅ **Testability** - Mock interfaces for unit tests
✅ **Scalability** - Async, cacheable, queue-ready
✅ **Maintainability** - Clear separation of concerns
✅ **Solo-friendly** - Not over-engineered for one person

### Key Principles to Remember:

1. **Dependency Rule**: Dependencies flow inward (API → Core ← Adapters)
2. **Interface Segregation**: Core defines interfaces, adapters implement
3. **Single Responsibility**: Each file/class has one clear purpose
4. **Technology Agnostic**: Business logic independent of frameworks
5. **Easy to Change**: Switch technologies with minimal code changes

### When in Doubt:

- **Business logic?** → Put in `core/services/`
- **Data access?** → Define interface in `core/interfaces/`, implement in `adapters/`
- **HTTP handling?** → Put in `api/endpoints/`
- **Utility function?** → Put in `utils/`
- **Configuration?** → Put in `config/settings.py`

---

**Happy coding! 🚀**

For questions or improvements to this documentation, please create an issue or PR in the repository.
            