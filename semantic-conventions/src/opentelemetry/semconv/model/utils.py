#   Copyright The OpenTelemetry Authors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import re

from opentelemetry.semconv.model.exceptions import ValidationError


ID_RE = re.compile("([a-z](\\.?[a-z0-9_-]+)+)")


def validate_id(semconv_id, position):
    if not ID_RE.fullmatch(semconv_id):
        raise ValidationError.from_yaml_pos(
            position,
            "Invalid id {}. Semantic Convention ids MUST be {}".format(
                semconv_id, ID_RE.pattern
            ),
        )


def validate_values(yaml, keys, mandatory=()):
    """This method checks only valid keywords and value types are used"""
    unwanted = [k for k in yaml.keys() if k not in keys]
    if unwanted:
        position = yaml.lc.data[unwanted[0]]
        msg = "Invalid keys: {}".format(unwanted)
        raise ValidationError.from_yaml_pos(position, msg)
    if mandatory:
        check_no_missing_keys(yaml, mandatory)


def check_no_missing_keys(yaml, mandatory):
    missing = list(set(mandatory) - set(yaml))
    if missing:
        position = yaml.lc.data[list(yaml)[0]]
        msg = "Missing keys: {}".format(missing)
        raise ValidationError.from_yaml_pos(position, msg)


class ValidatableYamlNode:

    allowed_keys = ()
    mandatory_keys = ("id", "brief")

    def __init__(self, yaml_node):
        self.id = yaml_node.get("id").strip()
        self.brief = str(yaml_node.get("brief")).strip()

        self._position = [yaml_node.lc.line, yaml_node.lc.col]

    @classmethod
    def validate_keys(cls, node):
        unwanted = [key for key in node.keys() if key not in cls.allowed_keys]
        if unwanted:
            position = node.lc.data[unwanted[0]]
            msg = "Invalid keys: {}".format(unwanted)
            raise ValidationError.from_yaml_pos(position, msg)

        if cls.mandatory_keys:
            check_no_missing_keys(node, cls.mandatory_keys)

    def validate_values(self):
        """
        Subclasses may provide additional validation.
        This method should raise an exception with a descriptive
        message if the semantic convention is not valid.
        """
        validate_id(self.id, self._position)
