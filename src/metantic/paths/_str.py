import builtins

def str(path: list[builtins.str]) -> builtins.str:
    return '/' + '/'.join(builtins.str(p) for p in path)