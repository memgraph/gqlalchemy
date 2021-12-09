from typing import Optional

from gqlalchemy import Memgraph, Node, Relationship

db = Memgraph()


class Person(Node, type="Person"):
    name: Optional[str]


class Alice(Person, type="Alice"):
    pass


class Friends(Relationship, type="FRIENDS"):
    pass


# db.execute("create (:Person {id: 1, name: 'person'});")
# db.execute("create (:Alice {id: 8, name: 'alice'});")
# db.execute("match (a:Alice) match(b:Person) create (a)-[:FRIENDS]->(b);")

result = list(db.execute_and_fetch("match (a)-[r]->(b) return a, r, b"))
for node in result:
    print(node["a"], node["r"], node["b"])
