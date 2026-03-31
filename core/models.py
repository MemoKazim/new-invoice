from dataclasses import dataclass
from typing import Optional


@dataclass
class Certificate:
    tin: str
    name: str
    taxpayer_type: str
