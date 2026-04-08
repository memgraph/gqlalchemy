# Copyright (c) 2016-2022 Memgraph Ltd. [https://memgraph.com]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional

from gqlalchemy import Memgraph, Node, Relationship, Field, match
from gqlalchemy.query_builders.memgraph_query_builder import Operator

db = Memgraph()


class UserSave(Node):
    id: str = Field(index=True, exist=True, unique=True, db=db)
    username: str = Field(index=True, exist=True, unique=True, db=db)


class UserMap(Node):
    id: str = Field(index=True, exist=True, unique=True, db=db)


class Streamer(UserMap):
    id: str = Field(index=True, exist=True, unique=True, db=db)
    username: Optional[str] = Field(index=True, exist=True, unique=True, db=db)
    url: Optional[str] = Field()
    followers: Optional[int] = Field()
    createdAt: Optional[str] = Field()
    totalViewCount: Optional[int] = Field()
    description: Optional[str] = Field()


class StreamerLoad(Node):
    id: str = Field(index=True, unique=True, db=db)
    name: Optional[str] = Field(index=True, exists=True, unique=True, db=db)


class Team(Node):
    name: str = Field(unique=True, db=db)


class IsPartOf(Relationship, type="IS_PART_OF"):
    date: Optional[str] = Field()


class Language(Node):
    name: str = Field(unique=True, db=db)


class ChatsWith(Relationship, type="CHATS_WITH"):
    lastChatted: Optional[str] = Field()


class Speaks(Relationship, type="SPEAKS"):
    pass


class SpeaksTemp(Relationship, type="SPEAKSTEMP"):
    pass


class TestMapNodesAndRelationships:
    def test_node_mapping(self):
        streamer = Streamer(
            id="7",
            username="Ivan",
            url="myurl.com",
            followers=888,
            createdAt="2022-26-01",
            totalViewCount=6666,
            description="Hi, I am streamer!",
        ).save(db)

        result = next(
            match()
            .node("Streamer", variable="s")
            .where(item="s.id", operator=Operator.EQUAL, literal="7")
            .return_()
            .execute()
        )["s"]

        assert result.id == streamer.id
        assert result.username == streamer.username
        assert result.url == streamer.url
        assert result.followers == streamer.followers
        assert result.createdAt == streamer.createdAt
        assert result.totalViewCount == streamer.totalViewCount
        assert result.description == streamer.description

    def test_relationship_mapping(self):
        streamer_1 = Streamer(
            id="8",
            username="Kate",
            url="myurl.com",
            followers=888,
            createdAt="2022-26-01",
            totalViewCount=6666,
            description="Hi, I am streamer!",
        ).save(db)
        streamer_2 = Streamer(
            id="9",
            username="Mislav",
            url="myurl.com",
            followers=888,
            createdAt="2022-26-01",
            totalViewCount=6666,
            description="Hi, I am streamer!",
        ).save(db)
        chats_with = ChatsWith(
            _start_node_id=streamer_1._id, _end_node_id=streamer_2._id, lastChatted="2021-04-25"
        ).save(db)

        result = next(match().node().to("CHATS_WITH", variable="c").node().return_().execute())["c"]

        assert result._start_node_id == streamer_1._id
        assert result._end_node_id == streamer_2._id
        assert result.lastChatted == chats_with.lastChatted
        assert result._type == chats_with._type


class TestSaveNodesAndRelationships:
    def test_node_saving_1(self):
        user = UserSave(id="3", username="John").save(db)
        language = Language(name="en").save(db)

        result = next(
            match()
            .node("UserSave", variable="u")
            .where(item="u.id", operator=Operator.EQUAL, literal="3")
            .return_()
            .execute()
        )["u"]

        assert result.id == user.id
        assert result.username == user.username

        result_2 = next(match().node("Language", variable="l").return_().execute())["l"]

        assert result_2._labels == language._labels

    def test_node_saving_2(self):
        user = UserSave(id="4", username="James")
        language = Language(name="hr")

        db.save_node(user)
        db.save_node(language)

        result = next(
            match()
            .node("UserSave", variable="u")
            .where(item="u.id", operator=Operator.EQUAL, literal="4")
            .return_()
            .execute()
        )["u"]

        assert result.id == user.id
        assert result.username == user.username

        result_2 = next(match().node("Language", variable="l").return_().execute())["l"]

        assert result_2._labels == language._labels

    def test_relationship_saving_1(self):
        user = UserSave(id="55", username="Jimmy").save(db)
        language = Language(name="ko").save(db)

        speaks_rel = Speaks(_start_node_id=user._id, _end_node_id=language._id).save(db)

        result = next(match().node().to("SPEAKS", variable="s").node().return_().execute())["s"]

        assert result._start_node_id == user._id
        assert result._end_node_id == language._id
        assert result._type == speaks_rel._type

    def test_relationship_saving_2(self):
        user = UserSave(id="35", username="Jessica").save(db)
        language = Language(name="de").save(db)

        speaks_rel = SpeaksTemp(_start_node_id=user._id, _end_node_id=language._id)
        db.save_relationship(speaks_rel)

        result = next(match().node().to("SPEAKSTEMP", variable="s").node().return_().execute())["s"]

        assert result._start_node_id == user._id
        assert result._end_node_id == language._id
        assert result._type == speaks_rel._type


class TestLoadNodesAndRelationships:
    def test_node_load(self):
        streamer = StreamerLoad(name="Jack", id="54").save(db)
        team = Team(name="Warriors").save(db)

        loaded_streamer = StreamerLoad(id="54").load(db=db)
        loaded_team = Team(name="Warriors").load(db=db)

        assert streamer.name == loaded_streamer.name
        assert streamer.id == loaded_streamer.id
        assert streamer._labels == {"StreamerLoad"}
        assert streamer._labels == loaded_streamer._labels
        assert team.name == loaded_team.name
        assert team._labels == {"Team"}
        assert team._labels == loaded_team._labels

        is_part_of = IsPartOf(_start_node_id=loaded_streamer._id, _end_node_id=loaded_team._id, date="2021-04-26").save(
            db
        )

        result = next(match().node().to("IS_PART_OF", variable="i").node().return_().execute())["i"]

        assert result._start_node_id == streamer._id
        assert result._end_node_id == team._id
        assert result._type == is_part_of._type

    def test_relationship_load(self):
        streamer = StreamerLoad(name="Hayley", id="36").save(db)
        team = Team(name="Lakers").save(db)
        is_part_of = IsPartOf(_start_node_id=streamer._id, _end_node_id=team._id, date="2021-04-20").save(db)
        loaded_is_part_of = IsPartOf(_start_node_id=streamer._id, _end_node_id=team._id).load(db)

        assert loaded_is_part_of._type == "IS_PART_OF"
        assert loaded_is_part_of._type == is_part_of._type
