# Copyright 2018 Intel Corporation
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
# -----------------------------------------------------------------------------

from sawtooth_sdk.processor.exceptions import InvalidTransaction


class codeSmellPayload(object):

    def __init__(self, payload):
        try:
            #The payload is csv utf-8 encoded string
            name, value, action, owner = payload.decode().split(",")
        except ValueError:
            raise InvalidTransaction("Invalid payload serialization")

        if not name:
            raise InvalidTransaction ('Name is required')
        if not value:
            raise InvalidTransaction ('Value is required')
        if not action:
            raise InvalidTransaction('Action is required')
        if action not in ('create', 'propose', 'vote'):
            raise InvalidTransaction('Invalid action: {}'.format(action))

        self.name = name
        self.value = value
        self.action = action
        self.owner = owner

    @staticmethod
    def from_bytes(payload):
        return codeSmellPayload(payload=payload)

    @property
    def name(self):
        return self.name

    @property
    def value(self):
        return self.value

    @property
    def action(self):
        return self.action

    @property
    def owner(self):
        return self.owner
