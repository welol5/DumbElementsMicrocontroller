from abc import ABC, abstractmethod

class Filter(ABC):

    @abstractmethod
    def apply_filter(self, colors:list[tuple]) -> list[tuple]:
        pass