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

import platform
import pytest
import os

from gqlalchemy.transformations.importing.loaders import (
    CSVLocalFileSystemImporter,
    DataLoader,
    FeatherLocalFileSystemImporter,
    FileSystemHandler,
    NameMapper,
    ORCLocalFileSystemImporter,
    ParquetLocalFileSystemImporter,
)


path = os.path.join(os.path.dirname(__file__), "data")


class TestFileSystemHandler(FileSystemHandler):
    def __init__(self) -> None:
        super().__init__(fs=None)

    def get_path(self):
        pass


class TestDataLoader(DataLoader):
    def __init__(self, file_system_handler: FileSystemHandler) -> None:
        super().__init__(file_extension="none", file_system_handler=file_system_handler)
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


@pytest.mark.extras
@pytest.mark.arrow
def test_local_table_to_graph_importer_parquet(memgraph):
    """e2e test, using Local File System to import into memgraph, tests available file extensions"""
    my_configuration = {
        "indices": {"example": ["name"]},
        "name_mappings": {"example": {"label": "PERSON"}},
        "one_to_many_relations": {"example": []},
    }
    importer = ParquetLocalFileSystemImporter(path=path, data_configuration=my_configuration, memgraph=memgraph)
    importer.translate(drop_database_on_start=True)


@pytest.mark.extras
@pytest.mark.arrow
def test_local_table_to_graph_importer_csv(memgraph):
    """e2e test, using Local File System to import into memgraph, tests available file extensions"""
    my_configuration = {
        "indices": {"example": ["name"]},
        "name_mappings": {"example": {"label": "PERSON"}},
        "one_to_many_relations": {"example": []},
    }
    importer = CSVLocalFileSystemImporter(path=path, data_configuration=my_configuration, memgraph=memgraph)
    importer.translate(drop_database_on_start=True)


@pytest.mark.extras
@pytest.mark.arrow
def test_local_table_to_graph_importer_orc(memgraph):
    """e2e test, using Local File System to import into memgraph, tests available file extensions"""
    if platform.system() == "Windows":
        with pytest.raises(ValueError):
            ORCLocalFileSystemImporter(path="", data_configuration=None)
    else:
        my_configuration = {
            "indices": {"example": ["name"]},
            "name_mappings": {"example": {"label": "PERSON"}},
            "one_to_many_relations": {"example": []},
        }
        importer = ORCLocalFileSystemImporter(path=path, data_configuration=my_configuration, memgraph=memgraph)
        importer.translate(drop_database_on_start=True)


@pytest.mark.extras
@pytest.mark.arrow
def test_local_table_to_graph_importer_feather(memgraph):
    """e2e test, using Local File System to import into memgraph, tests available file extensions"""
    my_configuration = {
        "indices": {"example": ["name"]},
        "name_mappings": {"example": {"label": "PERSON"}},
        "one_to_many_relations": {"example": []},
    }
    importer = FeatherLocalFileSystemImporter(path=path, data_configuration=my_configuration, memgraph=memgraph)
    importer.translate(drop_database_on_start=True)
