from pydantic import ValidationError
from gqlalchemy import Node


# test whether the private properties are saved into Memgraph
def test_private_properties(memgraph):
    class User(Node):
        id: int
        _name: str

    user = User(id=1, _name="Jane").save(memgraph)
    loaded_user = memgraph.load_node(user)

    assert hasattr(loaded_user, "_name") is False
    assert loaded_user.id == 1
    assert loaded_user._label == "User"
    assert user._name == "Jane"


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
