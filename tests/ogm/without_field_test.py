from gqlalchemy import Node, Field, Memgraph, match

memgraph = Memgraph()


class User(Node):
    name: str = Field(index=True, unique=True, db=memgraph)
    followers: int


def test_without_field():
    user = User(name="Mislav", followers=123)
    memgraph.save_node(user)

    result = next(
        match()
        .node("User", variable="u")
        .where("u.name", "=", "Mislav")
        .return_({"u.name": "name", "u.followers": "followers"})
        .execute()
    )

    assert result["name"] == "Mislav"
    assert result["followers"] == "None"
