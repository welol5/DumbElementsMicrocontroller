from abc import ABC, abstractmethod

class Animation(ABC):

    @abstractmethod
    def get_next_animation_frame(self) -> list[tuple]:
        pass

    @abstractmethod
    def get_current_state(self) -> list[tuple]:
        pass