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

from typing import Dict, Tuple, List

QM_KEY_NAME = "name"
QM_KEY_VALUE = "value"
QM_KEY_DEFAULT = "default"
QM_KEY_TYPE = "type"

QM_FIELD_NAME = "name"
QM_FIELD_IS_EDITABLE = "is_editable"
QM_FIELD_IS_WRITE = "is_write"
QM_FIELD_PATH = "path"
QM_FIELD_SIGNATURE = "signature"

LEFT_PARENTHESIS = "("
RIGHT_PARENTHESIS = ")"
EQUALS_DELIMITER = " = "
NAME_TYPE_DELIMITER = " :: "
COMMA_SEP = ", "
STRING_TYPE = "STRING"
QUOTATION_MARK = '"'


class QueryModule:
    """Class representing a single MAGE query module."""

    def __init__(self, **kwargs) -> None:
        arguments, returns = parse_query_module_signature(kwargs[QM_FIELD_SIGNATURE])

        self.name = kwargs[QM_FIELD_NAME]
        self.is_editable = kwargs[QM_FIELD_IS_EDITABLE]
        self.is_write = kwargs[QM_FIELD_IS_WRITE]
        self.path = kwargs[QM_FIELD_PATH]
        self.signature = kwargs[QM_FIELD_SIGNATURE]
        self.arguments = arguments
        self.returns = returns

    def __str__(self) -> str:
        return self.name

    def set_argument_values(self, **kwargs) -> None:
        """Set values for QueryModule arguments so the module can be called.

        Kwargs:
            Named arguments in self.arguments.

        Raises:
            KeyError: Passed an argument not in the self.arguments list.
        """
        for argument_name in kwargs:
            has_arg = False
            for argument_dict in self.arguments:
                if argument_dict[QM_KEY_NAME] == argument_name:
                    argument_dict[QM_KEY_VALUE] = str(kwargs[argument_name])
                    has_arg = True
                    break
            if not has_arg:
                raise KeyError(f"{argument_name} is not an argument in this query module.")

    def get_arguments_for_call(self) -> str:
        """return inputs in form "value1, value2, ..." for QueryBuilder call()
        method.

        Raises:
            KeyError: Cannot get all values of arguments because one or more is
            not set.
        """
        arguments_str = ""

        for argument_dict in self.arguments:
            if QM_KEY_VALUE in argument_dict:
                val = argument_dict[QM_KEY_VALUE]
            elif QM_KEY_DEFAULT in argument_dict:
                val = argument_dict[QM_KEY_DEFAULT]
            else:
                raise KeyError(f"{argument_dict[QM_KEY_NAME]} has no value set.")

            if argument_dict[QM_KEY_TYPE] == STRING_TYPE:
                arguments_str += QUOTATION_MARK + val + QUOTATION_MARK
            else:
                arguments_str += val

            arguments_str += COMMA_SEP

        return arguments_str[:-2]


def parse_query_module_signature(signature: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Query Modules signatures received from Memgraph are parsed into a
    list of dictionaries.

    One list is for arguments and another for returns.
    For instance, if a query module signature is:
    dummy_module.dummy(lst :: LIST OF STRING, num = 3 :: NUMBER) :: (ret :: STRING)
    the method should return a list of arguments:
    [{"name": "lst", "type": "LIST OF STRING"}, {"name": "num", "type": "NUMBER", "default": 3}]
    and a list of returns:
    [{"name": "ret", "type": "STRING"}]

    Dictionary consists of fields: "name" - argument name, "type" - data
    type of argument and "default" where default argument value is given

    Args:
        signature: module signature as returned by Cypher CALL operation
    """
    end_arguments_parenthesis = signature.index(RIGHT_PARENTHESIS)
    arguments_field = signature[signature.index(LEFT_PARENTHESIS) + 1 : end_arguments_parenthesis]
    returns_field = signature[
        signature.index(LEFT_PARENTHESIS, end_arguments_parenthesis)
        + 1 : signature.index(RIGHT_PARENTHESIS, end_arguments_parenthesis + 1)
    ]

    arguments = parse_field(
        vars_field=arguments_field.strip(),
        name_type_delimiter=NAME_TYPE_DELIMITER,
        default_value_delimiter=EQUALS_DELIMITER,
    )
    returns = parse_field(
        vars_field=returns_field.strip(),
        name_type_delimiter=NAME_TYPE_DELIMITER,
        default_value_delimiter=EQUALS_DELIMITER,
    )

    return arguments, returns


def parse_field(
    vars_field: str, name_type_delimiter: str = NAME_TYPE_DELIMITER, default_value_delimiter: str = EQUALS_DELIMITER
) -> List[Dict[str, str]]:
    """Parse a field of arguments or returns from Query Module signature.

    Args:
        vars_field: signature field inside parenthesis
    """
    if len(vars_field) == 0:
        return []

    vars = []

    for var in vars_field.split(COMMA_SEP):
        var_dict = {}
        sides = var.split(name_type_delimiter)
        var_dict[QM_KEY_TYPE] = sides[1]
        if default_value_delimiter in sides[0]:
            splt = sides[0].split(default_value_delimiter)
            var_dict[QM_KEY_NAME] = splt[0]
            var_dict[QM_KEY_DEFAULT] = splt[1].strip(QUOTATION_MARK)
        else:
            var_dict[QM_KEY_NAME] = sides[0]

        vars.append(var_dict)

    return vars
