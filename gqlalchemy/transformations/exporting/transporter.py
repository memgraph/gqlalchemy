from abc import ABC, abstractmethod


class Transporter(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def export(query_results):
        """Abstract method that will be overriden by subclasses that will know which correct graph type to create.
        Args:
            query_results: Results from the query execution obtained by calling `execute()` method of `mgclient`.

        Raises:
            NotImplementedError: The method must be override by a specific translator.
        """
        raise NotImplementedError("Subclasses must override this method in order to produce graph of a correct type.")
