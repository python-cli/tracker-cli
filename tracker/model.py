from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime

from .config import *

@dataclass
class Record:
    id: int = field(default_factory=int)
    title: str = field(default_factory=str)
    tags: List[str] = field(default_factory=list)
    timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp()))

    @property
    def tags_str(self) -> Optional[str]:
        return ', '.join(self.tags) if self.tags else None

    def datetime(self, format: str = '%Y-%m-%d') -> str:
        return datetime.fromtimestamp(self.timestamp).strftime(format)

    def save(self) -> None:
        with DB() as db:
            # Auto-increment logic: Get max existing id + 1
            existing_ids = [r['id'] for r in db.all() if r['id'] is not None]
            self.id = max(existing_ids) + 1 if existing_ids else 1
            db.insert(asdict(self))
