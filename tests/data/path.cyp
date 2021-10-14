CREATE (:Node{id: 0});
CREATE (:Node{id: 1});
CREATE (:Node{id: 2});
CREATE (:Node{id: 3});
MATCH (n:Node {id: 0}), (m:Node {id: 1}) MERGE (n)-[:RELATION {id: 0}]->(m);
MATCH (n:Node {id: 1}), (m:Node {id: 2}) MERGE (n)-[:RELATION {id: 1}]->(m);
MATCH (n:Node {id: 2}), (m:Node {id: 3}) MERGE (n)-[:RELATION {id: 2}]->(m);
