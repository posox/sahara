# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import jsonschema
import unittest2

from savanna.openstack.common import uuidutils
from savanna.utils import api_validator


def _validate(schema, data):
    validator = api_validator.ApiValidator(schema)
    validator.validate(data)


class ApiValidatorTest(unittest2.TestCase):
    def _validate_success(self, schema, data):
        return _validate(schema, data)

    def _validate_failure(self, schema, data):
        self.assertRaises(jsonschema.ValidationError, _validate, schema, data)

    def test_validate_required(self):
        schema = {
            "type": "object",
            "properties": {
                "prop-1": {
                    "type": "string",
                },
            },
        }

        self._validate_success(schema, {
            "prop-1": "asd",
        })
        self._validate_success(schema, {
            "prop-2": "asd",
        })

        schema["required"] = ["prop-1"]

        self._validate_success(schema, {
            "prop-1": "asd",
        })
        self._validate_failure(schema, {
            "prop-2": "asd",
        })

    def test_validate_additionalProperties(self):
        schema = {
            "type": "object",
            "properties": {
                "prop-1": {
                    "type": "string",
                },
            },
            "required": ["prop-1"]
        }

        self._validate_success(schema, {
            "prop-1": "asd",
        })
        self._validate_success(schema, {
            "prop-1": "asd",
            "prop-2": "asd",
        })

        schema["additionalProperties"] = True

        self._validate_success(schema, {
            "prop-1": "asd",
        })
        self._validate_success(schema, {
            "prop-1": "asd",
            "prop-2": "asd",
        })

        schema["additionalProperties"] = False

        self._validate_success(schema, {
            "prop-1": "asd",
        })
        self._validate_failure(schema, {
            "prop-1": "asd",
            "prop-2": "asd",
        })

    def test_validate_string(self):
        schema = {
            "type": "string",
        }

        self._validate_success(schema, "asd")
        self._validate_success(schema, "")
        self._validate_failure(schema, 1)
        self._validate_failure(schema, 1.5)
        self._validate_failure(schema, True)

    def test_validate_string_with_length(self):
        schema = {
            "type": "string",
            "minLength": 1,
            "maxLength": 10,
        }

        self._validate_success(schema, "a")
        self._validate_success(schema, "a" * 10)
        self._validate_failure(schema, "")
        self._validate_failure(schema, "a" * 11)

    def test_validate_integer(self):
        schema = {
            'type': 'integer',
        }

        self._validate_success(schema, 0)
        self._validate_success(schema, 1)
        self._validate_failure(schema, "1")
        self._validate_failure(schema, "a")
        self._validate_failure(schema, True)

    def test_validate_integer_w_range(self):
        schema = {
            'type': 'integer',
            'minimum': 1,
            'maximum': 10,
        }

        self._validate_success(schema, 1)
        self._validate_success(schema, 10)
        self._validate_failure(schema, 0)
        self._validate_failure(schema, 11)

    def test_validate_uuid(self):
        schema = {
            "type": "string",
            "format": "uuid",
        }

        uuid = uuidutils.generate_uuid()

        self._validate_success(schema, uuid)
        self._validate_failure(schema, uuid.replace("-", ""))

    def test_validate_hostname(self):
        schema = {
            "type": "string",
            "format": "hostname",
        }

        self._validate_success(schema, "abcd")
        self._validate_success(schema, "abcd123")
        self._validate_success(schema, "abcd-123")
        self._validate_failure(schema, "abcd_123")
        self._validate_failure(schema, "_123")
        self._validate_failure(schema, "a" * 64)
        self._validate_failure(schema, "")