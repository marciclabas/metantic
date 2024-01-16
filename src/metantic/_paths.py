from __future__ import annotations
from types import UnionType
from typing import TypeVar, get_origin, get_args, Callable, get_type_hints, Union
from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class ListBuilder:
    path: list[str | int]
    _children: Callable[[int], PathBuilder]
    def __getitem__(self, idx: int) -> PathBuilder:
        return self._children(idx)
    def __repr__(self) -> str:
        return f'ListBuilder(path={self.path}, keys=[0, 1, 2, ...])'
    
@dataclass
class TupleBuilder:
    path: list[str | int]
    _children: tuple[PathBuilder, ...]
    def __getitem__(self, idx: int) -> PathBuilder:
        if 0 <= idx < len(self._children):
            return self._children[idx]
        else:
            raise ValueError(f"Invalid index '{idx}' after path '{self.path}'. Valid indices are {list(range(len(self._children)))}")
    def __repr__(self) -> str:
        return f'TupleBuilder(path={self.path}, keys={list(range(len(self._children)))})'
    
@dataclass
class DictBuilder:
    path: list[str | int]
    _children: dict[str, PathBuilder]
    def __getitem__(self, name: str) -> PathBuilder:
        if name in self._children:
            return self._children[name]
        else:
            raise ValueError(f"Invalid key '{name}' after path '{self.path}'. Valid keys are {list(self._children.keys())}")
    def __repr__(self) -> str:
        return f'DictBuilder(path={self.path}, keys={list(self._children.keys())})'
    
@dataclass
class Path:
    path: list[str | int]
    
PathBuilder = ListBuilder | TupleBuilder | DictBuilder | Path

T = TypeVar('T')
    
def paths(cls: type[T], path = []) -> PathBuilder:
    """
    Returns a `PathBuilder` to generate valid paths of `cls`
    - Does not support unions (paths stop recursion upon finding a union)
    
    e.g:
    
    ```
    class FullName(TypedDict):
        first: str; middle: str; family: str

    class User:
        id: str
        full_name: FullName
        friends: list[str]
        
    ps = paths(User)
    ps['id'].path # ['id']
    ps['full_name']['first'].path # ['full_name', 'first']
    ps['friends'][69].path # ['friends', 69]
    
    ps['full_name']['second'].path # ERROR
    ```
    """
    base = get_origin(cls)
    if base is tuple:
        children = tuple(paths(x, path+[i]) for i, x in enumerate(get_args(cls)))
        return TupleBuilder(path=path, _children=children)
    elif base is list:
        [sub] = get_args(cls)
        return ListBuilder(path=path, _children=lambda i: paths(sub, path+[i]))
    elif base is UnionType:
        return Path(path=path)
    elif issubclass(cls, BaseModel):
        return DictBuilder(path=path, _children={
            field: paths(info.annotation, path+[field])
            for field, info in cls.model_fields.items()
        })
    elif (annotations := get_type_hints(cls)) != {}:
        return DictBuilder(path=path, _children={
            field: paths(ann, path+[field])
            for field, ann in annotations.items()
        })
    else:
        return Path(path=path)
