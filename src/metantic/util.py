from typing import TypeVar, Callable, GenericAlias, get_args, get_origin
from pydantic import BaseModel
import ramda as R

A = TypeVar('A', bound=BaseModel)
B = TypeVar('B', bound=BaseModel)
C = TypeVar('C')

@R.curry
def meta_map(f: Callable[[type[A]], type[B]], x: type[C]) -> type[C]:
    """Map a funcion `f: BaseModel -> BaseModel` across a generic type. Example
    
    ```
    class Client(BaseModel):
        id: str
        
    class Admin(BaseModel):
        id: str
        role: Role
    
    class Users(BaseModel):
        clients: list[list[dict[str, Client]]]
        admins: list[tuple[dict[str, Admin], int]]
        
    def add_name(model: type[BaseModel]) -> type[BaseModel]:
        match model:
            case User() | Admin():
                class Named(model):
                    name: str
                return Named
            case _:
                return model
                
    NamedUsers = meta_map(add_name, Users)
    
    # equivalent to:
    class NamedUsers(BaseModel):
        clients: list[list[dict[str, add_name(Client)]]]
        admins: list[tuple[dict[str, add_name(Admin)], int]]
    ```
    """
    if isinstance(x, GenericAlias):
        base = get_origin(x)
        args = get_args(x)
        mapped_args = tuple(R.map(meta_map(f), args))
        return base[mapped_args]
    elif issubclass(x, BaseModel):
        return f(x)
    else:
        return x