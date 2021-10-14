CREATE (:Node{id: 0, name: "name1"});
CREATE (:Node{id: 1, data: [1, 2, 3]});
CREATE (:Node{id: 2, data: {a: 1, b: "abc"}});
MATCH (n:Node {id: 0}), (m:Node {id: 1}) MERGE (n)-[:RELATION {id: 0, name: "name1"}]->(m);
MATCH (n:Node {id: 1}), (m:Node {id: 2}) MERGE (n)-[:RELATION {id: 1, num: 100}]->(m);
MATCH (n:Node {id: 2}), (m:Node {id: 0}) MERGE (n)-[:RELATION {id: 2, data: [1, 2, 3]}]->(m);
