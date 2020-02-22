from typing import (
    List,
    Union,
)


def category_names(value: Union[str, List]) -> List[str]:
    """Validate (and normalize) category name"""
    if isinstance(value, str):
        value = [ent_id.strip() for ent_id in value.split(",")]

    return value
