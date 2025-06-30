from dataclasses import dataclass, field, asdict
from typing import List
from .config import *

@dataclass
class Record:
    id: int  # timestamp with millisecond
    title: str  # required
    tags: List[str] = field(default_factory=list)  # optional

    def save(self):
        with DB() as db:
            db.insert(asdict(self))
