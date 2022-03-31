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

import pytest
from unittest.mock import patch, Mock

from gqlalchemy.loaders import (
    DataLoader,
    FileSystemHandler,
    FileSystemTypeEnum,
    NameMapper,
    PyarrowDataLoader,
    LocalFileSystemImporter,
    get_data_loader,
)


class TestFileSystemHandler(FileSystemHandler):
    def __init__(self) -> None:
        super().__init__()

    def get_path(self):
        pass


class TestDataLoader(DataLoader):
    def __init__(self, file_system_handler: FileSystemHandler) -> None:
        super().__init__(file_system_handler)
        self.num = 5

    def load_data(self, collection_name: str, is_cross_table: bool = False) -> None:
        self.num = 42


@pytest.fixture
def dummy_loader():
    return TestDataLoader(TestFileSystemHandler())


def test_name_mapper_get_label():
    """Test get_label from NameMapper class"""
    mappings = {"individuals": {"label": "INDIVIDUAL"}, "address": {"label": "ADDRESS"}}
    name_mapper = NameMapper(mappings)
    label = name_mapper.get_label("individuals")

    assert label == "INDIVIDUAL"


def test_name_mapper_get_property_name():
    """Test get_property_name from NameMapper class"""
    mappings = {"individuals": {"label": "INDIVIDUAL"}, "address": {"label": "ADDRESS"}}
    name_mapper = NameMapper(mappings)
    property_name = name_mapper.get_property_name("individuals", "label")
    assert property_name == "label"


def test_custom_data_loader(dummy_loader):
    """Test functionality of custom DataLoader with a custom FileSystemHandler"""
    dummy_loader.load_data("file")
    assert dummy_loader.num == 42


def test_get_data_loader_error():
    """Test get_data_loader when the file_extension is not supported"""
    with pytest.raises(ValueError):
        get_data_loader("fail", FileSystemTypeEnum.AmazonS3)


def test_get_data_loader_wrong_filesystem():
    """Test get_data_loader when the filesystem is not supported"""
    with pytest.raises(ValueError):
        get_data_loader("csv", 1)


def test_data_loader():
    """Test that for csv file extension a PyarrowDataLoader is returned"""
    get_filesystem_fake = Mock()
    get_filesystem_fake.return_value = None
    with patch("gqlalchemy.loaders.get_filesystem", wraps=get_filesystem_fake):
        assert type(get_data_loader("csv", FileSystemTypeEnum.Local)) is PyarrowDataLoader


@pytest.mark.parametrize(
    "file_extension",
    [
        "parquet",
        "csv",
        "orc",
        "feather",
    ],
)
def test_local_table_to_graph_importer(file_extension, memgraph):
    """e2e test, using Local File System to import into memgraph, tests available file extensions"""
    my_configuration = {
        "indices": {"example": ["name"]},
        "name_mappings": {"example": {"label": "PERSON"}},
        "one_to_many_relations": {"example": []},
    }

    print(file_extension)

    importer = LocalFileSystemImporter(
        file_extension=file_extension,
        data_configuration=my_configuration,
        local_storage_path="./tests/loaders/data",
        memgraph=memgraph,
    )

    importer.translate(drop_database_on_start=True)
