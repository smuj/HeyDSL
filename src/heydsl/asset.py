from dataclasses import dataclass
from enum import Enum


class AssetType(Enum):
    STYLESHEET = "stylesheet"
    SCRIPT = "script"


@dataclass(frozen=True)
class ExternalAsset:
    type: AssetType
    url: str
    integrity: str | None = None
