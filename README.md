# Metantic

> Metaprogramming with pydantic Models (creating types from types)

## Partial

> Create a partial model (all fields optional)

```python
from metantic import Partial

class User(BaseModel):
    id: str
    name: str
    age: int

Partial(User).model_validate(dict(id="id", name="name"))
# PartialUser(id='id', name='name', age=None)
```

## Fields

> Obtain a `Literal` type for the model's fields (which can be validated)

```python
from metantic import Fields

class User(BaseModel):
    id: str
    name: str
    age: int

Fields(User) # typing.Literal['id', 'name', 'age']

class Query(BaseModel):
    fields: Fields(User)

Query(fields=["id", "name"]) # OK
Query(fields=["email"]) # ValidationError: fields Input should be 'id', 'name' or 'age' [...]
```

## Omit

> Create a model with a subset of fields

```python
from metantic import Fields

class User(BaseModel):
    id: str
    name: str
    age: int

# the ID is unchangeable
def update(patch: Omit(User, ["id"])):
    ...
```

## Paths

> Type-safe paths

### Validate

```python
from metantic import paths

class FullName(BaseModel):
    first: str; middle: str; family: str

class User(BaseModel):
    id: str
    full_name: FullName
    friends: list[str]
    
paths.validate(['full_name', 'first'], User.model_json_schema()) # None
paths.validate(['bad_name', 'first'], User.model_json_schema()) # ValueError("Key 'bad_name' doesn't exist in ['id', 'full_name', 'friends'])"
```

### Type

> Create a path `RootModel` with validation
>

```python
from metantic.paths import Path

UserPath = Path(User)

UserPath(root=['full_name', 'first']) # PathT(root=['full_name', 'first'])
UserPath(root=['bad_name', 'first']) # raises ValueError(...)

```

### Builder

> Currently under construction. May fail for some generic/union types

```python
from metantic import paths
    
ps = paths.builder(User) # PathBuilder object
ps['id'].path # ['id']
ps['full_name']['first'].path # ['full_name', 'first']
ps['friends'][69].path # ['friends', 69]

ps['full_name']['second'].path # ERROR



```

- Works with tuples, lists, dicts, classes and pydantic models
- Type unions stop path generation