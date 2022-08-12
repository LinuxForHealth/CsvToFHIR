from abc import ABC
from pydantic import BaseModel


class ImmutableModel(ABC, BaseModel):
    """
    Abstract base class for immutable pydantic models.
    """
    class Config:
        allow_mutation = False
        frozen = True
        extra = "forbid"
