def obj_to_toml(data: dict[str, dict]) -> str:
    """Very opinionated"""
    
    lines: list[str] = []
    for k, v in data.items():
        lines.append(f"[{k}]")
        for vk, vv in v.items():
            if isinstance(vv, dict):
                for vvk, vvv in vv.items():
                    if isinstance(vvv, str): vvv = f"\"{vvv}\""
                    else: vvv = str(vvv).replace(': ', '=').replace('\'', '')
                    lines.append(f"{vk}.{vvk} = {vvv}")
            else:
                if isinstance(vv, str): vv = f"\"{vv}\""
                lines.append(f"{vk} = {vv}")
        lines.append('')
    
    return "\n".join(lines)
