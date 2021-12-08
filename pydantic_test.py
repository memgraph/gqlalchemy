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

# alice = Alice(name="alice", ssn=123)
# print(alice)
# db.execute("create (alice:Person {id: 7, name: 'alice'}) return alice limit 1")
result = list(db.execute_and_fetch("match (a:Person) return a limit 1"))
for node in result:
    d = node['a'].properties
    d["type"] = "Person"
    print(Node.parse_raw(str(d).replace("'", '"')))

# for node in result[0].values():
#     print(node)
#     a = Person.from_node(node)
#     print(a)
