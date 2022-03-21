from pydantic import ValidationError
from gqlalchemy import Node


# test whether the private properties are saved into Memgraph
def test_private_properties(memgraph):
    class User(Node):
        id: int
        last_name: str
        _name: str
        _age: int

    user = User(id=1, last_name="Smith", _name="Jane").save(memgraph)
    User(id=2, last_name="Scott").save(memgraph)
    loaded_user = memgraph.load_node(user)
    loaded_user._age = 24
    try:
        memgraph.load_node(User(id=2))
    except ValidationError:
        loaded_user2 = memgraph.load_node(User(id=2, last_name="Scott"))

    assert type(loaded_user) is User
    assert type(loaded_user2) is User
    assert hasattr(loaded_user, "_name") is False
    assert hasattr(loaded_user, "_age") is True
    assert hasattr(loaded_user2, "_name") is False
    assert hasattr(loaded_user2, "_age") is False
    assert loaded_user.id == 1
    assert loaded_user.last_name == "Smith"
    assert loaded_user._label == "User"
    assert loaded_user2.id == 2
    assert loaded_user2.last_name == "Scott"
    assert loaded_user2._label == "User"
    user._name == "Jane"
    assert loaded_user._age == 24


# test whether the node can be loaded with one of the properties
def test_partial_loading(memgraph):
    class User(Node):
        id: int
        name: str = None

    User(id=1, name="Jane").save(memgraph)
    try:
        memgraph.load_node(User(name="Jane"))
    except ValidationError:  # validation error since no 'id' is provided - missing field
        user_by_id = memgraph.load_node(
            User(id=1)
        )  # user_by_id will be loaded from the database ('name' is not missing)

    assert user_by_id.id == 1
    assert user_by_id.name == "Jane"
    assert user_by_id._label == "User"
