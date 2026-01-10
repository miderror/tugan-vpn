from typing import ClassVar

from pydantic import BaseModel


class IntegrationEvent(BaseModel):
    event_name: ClassVar[str]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "event_name"):
            cls.event_name = cls.__name__

    class Config:
        frozen = True
