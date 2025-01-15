from abc import ABC, abstractmethod

# Abstrakcyjna klasa bazowa dla różnych streamów
class VideoStream(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def get_frame(self):
        pass

    @abstractmethod
    def stop(self):
        pass