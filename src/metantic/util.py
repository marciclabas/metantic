from typing import get_args
import inspect
from pydantic import BaseModel

def model_type(t: type) -> type[BaseModel] | None:
    """Return the first `BaseModel` subclass within a generic type.
    
    Example:
    ```
    class Model(BaseModel):
        ...
        
    model_type(list[list[dict[str, Model]]]) # Model
    ```
    """
    if inspect.isclass(t):
        return t if issubclass(t, BaseModel) else None
    for a in get_args(t):
        m = model_type(a)
        if m is not None:
            return m