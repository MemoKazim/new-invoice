from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    @abstractmethod
    def ensure_dirs(self) -> None: ...

    @abstractmethod
    def open_report(self, filepath: str) -> None: ...
