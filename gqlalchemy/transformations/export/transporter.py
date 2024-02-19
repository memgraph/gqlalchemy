# Copyright (c) 2016-2023 Memgraph Ltd. [https://memgraph.com]
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

from abc import ABC, abstractmethod


class Transporter(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def export(query_results):
        """Abstract method that will be overridden by subclasses that will know which correct graph type to create.
        Raises:
            NotImplementedError: The method must be override by a specific translator.
        """
        raise NotImplementedError("Subclasses must override this method in order to produce graph of a correct type.")
