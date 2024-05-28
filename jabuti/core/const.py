TYPES_GROUP: dict[str, str] = {
    "str"      : "text",
    "int"      : "number",
    "float"    : "number",
    "bool"     : "flag",
    "set"      : "sequence",
    "list"     : "sequence",
    # "tuple"    : "sequence", # should not be used as a result
    "dict"     : "mapping",
    "DataFrame": "table",
}
