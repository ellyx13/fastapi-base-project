## Why I use `Generic[TModel]` and `TypeVar`

In this codebase, I use `Generic[TModel]` to define reusable base service classes (e.g. `BaseServices`) that can work with any Pydantic model while retaining **type safety** and **IDE support**.

### Benefits:
- ✅ Enables full autocompletion for `self.model(...)`, including field names and methods from the actual model (e.g. `UserModel`, `TaskModel`).
- ✅ Improves code readability and refactoring safety by making the expected data shape explicit at each layer.
- ✅ Ensures `model` is always a subclass of `BaseModel`, enforced by `TypeVar(..., bound=BaseModel)`.
- ✅ Allows shared business logic in `BaseServices`, while letting each service bind to its own model type without repeating code.

```python
TModel = TypeVar("TModel", bound=BaseModel)

class BaseServices(Generic[TModel]):
    def __init__(self, model: Type[TModel]):
        self.model = model

    def parse(self, data: dict) -> TModel:
        return self.model(**data)  # IDE knows the exact type!
```