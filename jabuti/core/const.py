TYPES_GROUP: dict[str, str] = {
    "str"      : "text",
    "int"      : "numeric",
    "float"    : "numeric",
    "bool"     : "boolean",
    "set"      : "sequence",
    "list"     : "sequence",
    # "tuple"    : "sequence", # should not be used as a result
    "dict"     : "mapping",
    "DataFrame": "table",
}
