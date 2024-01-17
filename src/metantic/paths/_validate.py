import ramda as R

@R.curry
def ref(ref: str, defs: dict[str]) -> dict[str]:
    """`ref`: `'#/$defs/<key>'`"""
    key = ref.split('/')[-1]
    return defs[key]

def validate(path: list[str|int], schema: dict[str]) -> bool:
    """Validate `path` against `schema` as defined in the [JSON Schema](https://json-schema.org/learn/getting-started-step-by-step) spec
    - `schema` can be obtained via `BaseModel.model_json_schema()` ([pydantic docs](https://docs.pydantic.dev/latest/concepts/json_schema/))
    - Assumes `schema` is valid; otherwise an exception may be raised
    """
    def _validate(_schema: dict[str], _path: list[str]) -> bool:
        if _path == []:
            return True
        [k, *ks] = _path
        if '$ref' in _schema:
            sch = ref(_schema['$ref'], schema['$defs'])
            return _validate(sch, _path)
        if _schema.get("type") == "object":
            properties = _schema.get("properties", {})
            if k in properties:
                return _validate(properties[k], ks)
            else:
                return False
        elif _schema.get("type") == "array" and str(k).isdigit():
            items = _schema.get("items", {})
            return _validate(items, ks)
        else:
            return False
    return _validate(schema, path)