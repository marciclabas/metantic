from dataclasses import dataclass
from pydantic import RootModel, BaseModel
from ._validate import validate
from ._str import str as strify

@dataclass
class Path:
    path: list[int | str]
    def __init__(self, path: list[int | str], model: type[BaseModel]):
        match validate(path, model.model_json_schema()):
            case None:
                self.path = path
            case ValueError() as err:
                raise err
            
    def __str__(self) -> str:
        return strify(self.path)