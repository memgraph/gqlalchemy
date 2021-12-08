from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class Node(BaseModel):
    _id: int
    @property
    def labels(self) -> Set[str]:
        return self._labels

class Relationship(BaseModel):
    _id: int
    @property
    def type(self) -> str:
        return self._type

    @property
    def end_node(self) -> int:
        return self._end_node

    @property
    def start_node(self) -> int:
        return self._start_node

    @property
    def nodes(self) -> Tuple[int, int]:
        return (self.start_node, self.end_node)


external_data = {}
node = Node(**external_data)
print(node)
