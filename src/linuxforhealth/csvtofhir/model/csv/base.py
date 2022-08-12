from pydantic import BaseModel


class CsvBaseModel(BaseModel):
    """
    Provides fields common to all CSV models
    """
    filePath: str
    rowNum: int
