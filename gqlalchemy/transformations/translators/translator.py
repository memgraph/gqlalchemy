from abc import ABC, abstractmethod
from typing import Callable, List, Set, Union, Type
from translators.constants import LABELS_CONCAT
from numbers import Number
from gqlalchemy.models import Node, Relationship
# TODO: fix the import order

class Translator(ABC):


    # Lambda function to concat list of labels
    merge_labels: Callable[[Set[str]], str] = lambda labels, default_node_label: LABELS_CONCAT.join([label for label in labels]) if len(labels) else default_node_label

    def __init__(self) -> None:
        super().__init__()



    @abstractmethod
    def to_cypher_queries(graph):
        """Abstract method which doesn't know how to produce cypher queries for a specific graph type and thus needs to be overriden.
        Args:
            graph: Can be of any type supported by the derived Translator object.

        Raises:
            NotImplementedError: The method must be override by a specific translator.
        """
        raise NotImplementedError("Subclasses must override this method to produce cypher queries for specific graph type.")

    @abstractmethod
    def get_instance(query_results):
        """Abstract method which doesn't know how to create the concrete instance so it needs to be overriden.
        Args:
            query_results: Results from the query execution obtained by calling `execute()` method of `mgclient`.

        Raises:
            NotImplementedError: The method must be override by a specific translator.
        """
        raise NotImplementedError("Subclasses must override this method to correctly parse query results for specific graph type.")

    @classmethod
    def get_entity_numeric_properties(cls, entity: Union[Node, Relationship]):
        """
        """
        numeric_properties = {}
        for key, val in entity._properties.items():
            if Translator._is_most_inner_type_number(val):
                numeric_properties[key] = val
        return numeric_properties

    @classmethod
    def _is_most_inner_type_number(cls, obj):
        """Checks if the most inner object type is a type derived from Number. E.g For a List[List[int]] return True
        Args:
            obj: Object that will be checked.

        Returns:
            None if the object is empty(type cannot be inferred) or the type of the most inner object.
        """
        if isinstance(obj, list):
            return len(obj) and Translator._is_most_inner_type_number(obj[0])
        return isinstance(obj, Number)
