from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from gqlalchemy import Memgraph, Node

db = Memgraph()

class Person(Node, type="Person"):
    name: Optional[str]
    ssn: Optional[int]

    def from_node(node: Node):
        return Person(**node.properties)

class Alice(Person, type="Alice"):
    haircut: Optional[str]

# db.execute("create (:Person {id: 1, name: 'person'});")
# db.execute("create (:Alice {id: 8, name: 'alice'});")

result = list(db.execute_and_fetch("match (a) return a"))
for node in result:
    print(node['a'])
