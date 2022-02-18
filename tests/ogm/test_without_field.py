from gqlalchemy import Node, Field, match


def test_without_field(memgraph):
    class User(Node):
        name: str = Field(index=True, unique=True, db=memgraph)
        followers: int

    User(name="Mislav", followers=123).save(memgraph)

    result = next(
        match()
        .node("User", variable="u")
        .where("u.name", "=", "Mislav")
        .return_({"u.name": "name", "u.followers": "followers"})
        .execute()
    )

    assert result["name"] == "Mislav"
    assert result["followers"] == "None"
