from pydantic import BaseModel, ConfigDict

def to_camel_case(snake_str: str) -> str:
    words = snake_str.split('_')
    return words[0] + ''.join(x.title() for x in words[1:])

class BaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel_case,
        populate_by_name=True,
    )

    