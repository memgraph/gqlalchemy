from abc import ABC, abstractmethod


class Importer(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def to_cypher_queries():
        raise NotImplementedError("Correct import strategy must be provided by subclasses.")
