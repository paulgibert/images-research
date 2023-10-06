def image_full_name(registry_domain: str,
                    registry_path: str, image_name: str,
                    tag: str) -> str:
    if registry_path is None:
        return f"{registry_domain}/{image_name}:{tag}"
    
    return f"{registry_domain}/{registry_path}/{image_name}:{tag}"