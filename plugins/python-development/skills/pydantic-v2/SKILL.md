---
name: pydantic-v2
description: >
  Pydantic v2 patterns for production Python: validators (`@field_validator`, `@model_validator`), computed fields, strict types, discriminated unions, settings management, `model_validate` / `model_dump`, `condecimal` and `Annotated[Decimal, ...]` for money, performance tips, and a v1 -> v2 migration checklist. Also covers FastAPI integration (response_model serialization, request validation, error envelope customization).
  TRIGGER WHEN: writing or refactoring Pydantic models in Python 3.10+; migrating a codebase from Pydantic v1 to v2; choosing between `Annotated[Decimal, ...]` vs `condecimal`; hitting v2 performance or serialization surprises; designing FastAPI request/response schemas or error envelopes with Pydantic.
  DO NOT TRIGGER WHEN: the task is Python testing (use python-tdd), generic typing unrelated to Pydantic (use mypy / typing docs), or non-Python schema work (use typescript-development for Zod / io-ts).
---

# Pydantic v2

Pydantic v2 (released 2023-06, stable through 2.10+ as of 2026-04) is a near-complete rewrite on `pydantic-core` (Rust). API is similar but not identical to v1 -- several v1 patterns silently break or behave differently. This skill documents the v2 idioms, the v1 migration gotchas, and the FastAPI integration surface.

## When to load which section

- Writing a new model from scratch -> "Core model patterns" + "Validators"
- Migrating from v1 -> "v1 -> v2 migration checklist"
- Working with money / decimals -> "Monetary precision (CWE-681 defense)"
- FastAPI request/response models -> "FastAPI integration"
- Performance-sensitive hot path -> "Performance notes"

## Core model patterns

```python
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
    model_validator,
)

# Type aliases with constraints -- preferred in v2 over `constr()` / `conint()`
NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
USDAmount = Annotated[Decimal, Field(max_digits=14, decimal_places=2, ge=0)]

class LineItem(BaseModel):
    # model_config replaces inner `Config` class
    model_config = ConfigDict(
        strict=True,               # refuse string "1" for int field
        frozen=True,               # hashable + immutable
        populate_by_name=True,     # accept alias AND field name
        str_strip_whitespace=True, # strip on all str fields
        extra="forbid",            # reject unknown keys
    )

    sku: NonEmptyStr
    quantity: int = Field(ge=1)
    unit_price: USDAmount
    currency: Literal["USD", "EUR", "GBP"] = "USD"

    @computed_field
    @property
    def total(self) -> USDAmount:
        return self.unit_price * self.quantity

    @field_validator("sku")
    @classmethod
    def sku_format(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("sku must be alphanumeric")
        return v.upper()

    @model_validator(mode="after")
    def cross_field_check(self) -> "LineItem":
        if self.currency == "USD" and self.unit_price > Decimal("10000"):
            raise ValueError("USD line item exceeds single-item limit")
        return self
```

### Key points

- `model_config = ConfigDict(...)` replaces the v1 inner `class Config:` pattern. Importing `ConfigDict` gives you autocomplete.
- `Annotated[T, Field(...)]` or `Annotated[T, StringConstraints(...)]` is the idiomatic v2 way to attach constraints -- prefer over `constr()`, `conint()`, `condecimal()` wrappers (still supported, but Annotated composes better with Python's type system).
- `@computed_field` replaces the v1 `@property` + `validator(always=True)` dance; shows up in `model_dump()` automatically.
- `@field_validator("field_name")` replaces v1 `@validator("field_name")`. Decorator is classmethod; must have `@classmethod` decorator after `@field_validator`.
- `@model_validator(mode="before" | "after")` replaces v1 `@root_validator(pre=True | False)`. In `mode="after"` the method returns `self`, not a dict.

## Validators

### Field validators

```python
@field_validator("email")
@classmethod
def email_lowercase(cls, v: str) -> str:
    return v.lower()

@field_validator("password")
@classmethod
def password_strength(cls, v: str, info: ValidationInfo) -> str:
    # info.data has already-validated fields; info.field_name is the field
    if len(v) < 12:
        raise ValueError("password must be at least 12 chars")
    return v
```

- Default `mode="after"`: runs after type coercion
- `mode="before"`: runs on raw input before coercion (use when the field is parsed from a non-matching type)
- `mode="plain"`: fully custom, no coercion at all
- `mode="wrap"`: intercepts both input and output, can call `handler(...)` to run default validation then post-process

### Model validators

```python
@model_validator(mode="before")
@classmethod
def normalize_input(cls, data: dict) -> dict:
    # Fix incoming API shape before Pydantic processes it
    if "userEmail" in data and "user_email" not in data:
        data["user_email"] = data.pop("userEmail")
    return data

@model_validator(mode="after")
def check_date_order(self) -> "Event":
    if self.start_date > self.end_date:
        raise ValueError("start_date must be <= end_date")
    return self
```

## Serialization: `model_dump`, `model_dump_json`, `model_validate`

v2 renamed the v1 methods:

| v1 | v2 |
|----|----|
| `model.dict()` | `model.model_dump()` |
| `model.json()` | `model.model_dump_json()` |
| `Model.parse_obj(...)` | `Model.model_validate(...)` |
| `Model.parse_raw(...)` | `Model.model_validate_json(...)` |
| `Model.construct(...)` | `Model.model_construct(...)` |
| `Model.schema()` | `Model.model_json_schema()` |
| `Model.__fields__` | `Model.model_fields` |

All deprecated v1 names still work with deprecation warnings. Production: use the v2 names.

### Serialization modes

```python
model.model_dump(mode="python")  # native Python types (Decimal stays Decimal)
model.model_dump(mode="json")    # JSON-compatible types (Decimal -> str)

model.model_dump(exclude={"password_hash"})
model.model_dump(include={"id", "name"})
model.model_dump(exclude_none=True)
model.model_dump(by_alias=True)   # use field aliases as keys
model.model_dump(round_trip=True) # output can be fed back into model_validate
```

## Discriminated unions

The pattern for "this field determines which model to parse":

```python
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field

class EmailEvent(BaseModel):
    type: Literal["email"]
    to: str
    subject: str

class SmsEvent(BaseModel):
    type: Literal["sms"]
    to: str
    body: str

Event = Annotated[Union[EmailEvent, SmsEvent], Field(discriminator="type")]

class Envelope(BaseModel):
    id: str
    event: Event

Envelope.model_validate({"id": "1", "event": {"type": "email", "to": "x@y", "subject": "hi"}})
```

Faster than v1 unions (pydantic-core picks the variant without trying each) and produces cleaner error messages.

## Monetary precision (CWE-681 defense)

Never use `float` for money. Two idiomatic v2 options:

```python
from decimal import Decimal
from typing import Annotated
from pydantic import BaseModel, Field, condecimal

# Option A (preferred): Annotated with Field constraints
USDAmount = Annotated[Decimal, Field(max_digits=14, decimal_places=2, ge=0)]

# Option B: condecimal() wrapper (still supported)
USDAmountV1Style = condecimal(max_digits=14, decimal_places=2, ge=0)

class Invoice(BaseModel):
    subtotal: USDAmount
    tax: USDAmount
    total: USDAmount
```

For currency arithmetic, pair with `decimal.getcontext()` for rounding mode:

```python
from decimal import ROUND_HALF_EVEN, getcontext
getcontext().rounding = ROUND_HALF_EVEN  # banker's rounding for financial totals
```

See `senior-review:defect-taxonomy` CWE-681 / CWE-682 for the full monetary-precision rules.

## Settings management (`pydantic-settings`)

v2 extracted settings into a separate package `pydantic-settings`:

```python
# pip install pydantic-settings
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        case_sensitive=False,
    )

    database_url: str
    stripe_secret_key: SecretStr  # redacted in repr / model_dump_json
    debug: bool = False
    port: int = Field(default=8000, ge=1, le=65535)

settings = AppSettings()
```

- `SecretStr` / `SecretBytes` hide the value in logs / tracebacks -- use for every API key, password, or token
- Reading the value: `settings.stripe_secret_key.get_secret_value()`
- Source priority (high -> low): init args > env vars > .env file > defaults

## FastAPI integration

### Response models

```python
from fastapi import FastAPI
from pydantic import BaseModel

class UserOut(BaseModel):
    id: int
    email: str

class UserDB(UserOut):
    password_hash: str  # server-side only, never exposed

app = FastAPI()

@app.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int) -> UserDB:
    # Returning the broader UserDB is fine; FastAPI projects through UserOut.
    return await fetch_user(user_id)
```

FastAPI uses the `response_model` for serialization, which strips `password_hash`. Prefer this to manual dict construction.

### Request validation and custom error envelopes

```python
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_failed",
            "details": exc.errors(),   # Pydantic v2 error format
            "request_id": request.headers.get("x-request-id"),
        },
    )
```

v2 error shape differs from v1: `ctx`, `input`, and `url` fields changed. If you serialize errors to clients, pin the shape in an integration test.

### Streaming / long-lived response models

`model_dump_json()` is faster than `json.dumps(model.model_dump())` for streaming. For SSE / WebSocket, cache the serializer:

```python
from typing import Any
serializer = MyModel.__pydantic_serializer__
raw = serializer.to_json(instance)  # bytes
```

## Performance notes

- `model_validate` is significantly faster than `parse_obj` in v2 (both call pydantic-core, but `model_validate` has a cleaner path).
- `model_construct(**data)` skips validation entirely -- use only for known-valid data (e.g., freshly loaded from a DB with a matching schema).
- Large models with many validators: consider `strict=True` at config level to skip coercion attempts.
- Avoid `@field_validator(..., mode="before")` on hot paths when a constraint via `Field(...)` would do -- core-side constraints are faster than Python-level callbacks.
- JSON -> model: `model_validate_json(raw_bytes)` is faster than `model_validate(json.loads(raw_bytes))`.

## v1 -> v2 migration checklist

Run `bump-pydantic` for the mechanical transforms:

```bash
uvx bump-pydantic src/
```

Then handle the cases the bot can't:

- `@validator` -> `@field_validator` + `@classmethod` decorator above the validator
- `@root_validator(pre=True)` -> `@model_validator(mode="before")`, method is classmethod, first arg is `cls`, takes raw dict
- `@root_validator` (no pre) -> `@model_validator(mode="after")`, method returns `self`
- `Config.allow_population_by_field_name` -> `model_config = ConfigDict(populate_by_name=True)`
- `Config.orm_mode` -> `model_config = ConfigDict(from_attributes=True)`
- `Config.schema_extra` -> `model_config = ConfigDict(json_schema_extra={...})`
- `Config.extra = "allow"|"forbid"|"ignore"` -> `ConfigDict(extra=...)`
- `parse_obj` -> `model_validate`; `parse_raw` -> `model_validate_json`; `dict()` -> `model_dump()`; `json()` -> `model_dump_json()`
- Generic `BaseModel[T]` -- v2 uses native Python generics, not `GenericModel`
- `Field(..., env="FOO")` in settings -> moved to `pydantic-settings` package (`BaseSettings` is no longer in `pydantic`)
- `__fields__` -> `model_fields` (the shape changed: `FieldInfo` objects, not `ModelField`)
- `__root__` model -> use `RootModel[T]` (`from pydantic import RootModel`)
- `Optional[X] = None` without default -> still optional but now must have default; v1 allowed no default on Optional, v2 requires it
- `smart_union` -> default behavior in v2; old `smart_union=True` is a no-op
- `ValidationError.errors()` format changed: `msg`, `type`, `loc`, `input`, `ctx` -- regenerate any error-envelope tests

## Common gotchas

- **`strict=True` breaks JSON API boundaries**: by default, FastAPI coerces `"1"` -> `1` for path/query params. If you set `strict=True` globally, int query params must be sent as JSON numbers. Apply strict selectively.
- **`extra="forbid"` + evolving clients**: rejects unknown fields. Fine for internal APIs, risky for public APIs where clients may send forward-compatible fields. Use `"ignore"` (default) for public ingress.
- **`@computed_field` with expensive work**: runs on every `model_dump()`. Cache if expensive, or use a regular property (which won't be serialized).
- **Frozen models are hashable**: useful for use as dict keys / in sets, but `model_copy(update={...})` is now required to "change" one -- can't just assign.
- **`model_validate_json` raw bytes vs str**: accepts both; bytes path avoids decode cost on hot paths.
- **Discriminator must be a `Literal`, not `str`**: `Field(discriminator="type")` requires each union member to declare `type: Literal["..."]`, not `type: str`.
- **v2 does NOT validate on `__setattr__` by default**: assigning to a mutable model attribute after construction skips validation. Set `ConfigDict(validate_assignment=True)` if you need it.

## Integration

- Python architecture / API design that uses Pydantic v2 -> `python-development:python-engineer` agent
- Testing Pydantic models -> `python-development:python-tdd` skill
- FastAPI project scaffolding with v2 defaults -> `python-development:python-scaffold` command (`--type fastapi`)
- Monetary precision patterns -> `senior-review:defect-taxonomy` (CWE-681 / CWE-682)
- TypeScript equivalent (Zod / valibot) -> `typescript-development:mastering-typescript` skill

## References

- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [Pydantic v2 Core Concepts](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [bump-pydantic migration tool](https://github.com/pydantic/bump-pydantic)
- [FastAPI + Pydantic v2](https://fastapi.tiangolo.com/tutorial/response-model/)
