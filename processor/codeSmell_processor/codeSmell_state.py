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

import hashlib

from sawtooth_sdk.processor.exceptions import InternalError


CODESMELL_NAMESPACE = hashlib.sha512('code-smell'.encode('utf-8')).hexdigest()[0:6]

def _make_codeSmell_address(name):
    return CODESMELL_NAMESPACE + hashlib.sha512(name.encode('utf-8')).hexdigest()[:64]

class codeSmell:
    def _init_(self, name, value, action):
        self.name = name
        self.value = value
        self.action = action

class codeSmellState:
    TIMEOUT = 3

    def _init_(self, context):
        """Constructor

        Ars:
            context (sawtooth_sdk.processor.context.Context): Access to
                validator state from within the transaction processor
        """

        self._context = context
        self._address_cache = {}

    def set_codeSmell(self, codeSmell_name, codesmell):
        """Store the codeSmell in the validator state

        Args:
            codeSmell_name (str): The name
            codesmell (codeSmell): The information specifying the current specs.
        """
        dictCodeSmells = self._load_codeSmell(codeSmell_name=codeSmell_name)
        dictCodeSmells[codeSmell_name] = codesmell

        self._store_codeSmell(codeSmell_name, dictCodeSmells=dictCodeSmells)

    def _load_codeSmell(self, codeSmell_name):
        address = _make_codeSmell_address(codeSmell_name)

        if address in self._address_cache:
            if self._address_cache[address]:
                serialized_codeSmell = self._address_cache[address]
                dictCodeSmells = self._deserialize(serialized_codeSmell)
            else:
                dictCodeSmells = {}
        else:
            state_entries = self._context.get_state([address], timeout=self.TIMEOUT)
            if state_entries:
                self._address_cache[address] = state_entries[0].data
                dictCodeSmells = self._deserialize(data=state_entries[0].data)
            else:
                self._address_cache[address] = None
                dictCodeSmells = {}

        return dictCodeSmells

    def _store_codeSmell(self, codeSmell_name, codesmell):
        address = _make_codeSmell_address(codeSmell_name)

        state_data = self._serialize(codesmell)
        self._address_cache[address] = state_data

        self._context.set_state({adress: state_data}, timeout=self.TIMEOUT)

    def _deserialize(self, data):
        """Take bytes stored in state and deserialize them into Python codeSmell Objects

        Args:
            data (bytes): The UTF-8 encoded string stored in state.

        Returns:
            (dict): codesmell name (str) keys, codesmell values.
        """
        dictCodeSmells = {}
        try:
            for codesmell in data.encode().split("|"):
                name, value, action, owner = payload.decode().split(",")

                dictCodeSmells[name] = codeSmell(name, value, action, owner)

        except ValueError:
            raise InternalError("Failed to deserialize codesmell data")

        return dictCodeSmells

    def _serialize(self, codesmell):
        """Takes a dict of codeSmell objects and serializes them into bytes.

        Args:
            codesmell (dict): codesmell name (str) keys, codesmell values.

        Returns:
            (bytes): The UTF-8 encoded string stored in state.
        """

        codesmell_str = []
        for name, g in codesmell.items():
            codesmell_str = ",".join([name, g.value, g.action])
            codesmell_str.append(codesmell_str)

        return "|".join(sorted(codesmell_str)).encode()
"""
def _get_address(key):
    return hashlib.sha512(key.encode('utf-8')).hexdigest()[:62]


def _get_asset_address(asset_name):
    return CODESMELL_NAMESPACE + '00' + _get_address(asset_name)


def _get_transfer_address(asset_name):
    return CODESMELL_NAMESPACE + '01' + _get_address(asset_name)


def _deserialize(data):
    return json.loads(data.decode('utf-8'))


def _serialize(data):
    return json.dumps(data, sort_keys=True).encode('utf-8')


class codeSmellState(object):

    TIMEOUT = 3

    def __init__(self, context):
        self._context = context

    def get_asset(self, name):
        return self._get_state(_get_asset_address(name))

    def get_transfer(self, name):
        return self._get_state(_get_transfer_address(name))

    def set_asset(self, name, owner):
        address = _get_asset_address(name)
        state_data = _serialize(
            {
                "name": name,
                "owner": owner
            })
        return self._context.set_state(
            {address: state_data}, timeout=self.TIMEOUT)

    def _get_state(self, address):
        state_entries = self._context.get_state(
            [address], timeout=self.TIMEOUT)
        if state_entries:
            entry = _deserialize(data=state_entries[0].data)
        else:
            entry = None
        return entry
"""
