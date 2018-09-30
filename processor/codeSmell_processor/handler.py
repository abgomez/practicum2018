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

import logging
import sawtooth_sdk

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from codeSmell_processor.codeSmell_payload import codeSmellPayload
from codeSmell_processor.codeSmell_state import codeSmellState
from codeSmell_processor.codeSmell_state import CODESMELL_NAMESPACE


LOGGER = logging.getLogger(__name__)


class codeSmellTransactionHandler(TransactionHandler):

    @property
    def family_name(self):
        return 'code-smell'

    @property
    def family_versions(self):
        return ['0.1']

    @property
    def encodings(self):
        return ['application/json']

    @property
    def namespaces(self):
        return [CODESMELL_NAMESPACE]

    def apply(self, transaction, context):
        header = transaction.header
        signer = header.signer_public_key

        payload = codeSmellPayload(transaction.payload)
        state = codeSmellState(context)

        LOGGER.info('Handling transaction: %s > %s %s:: %s',
                    payload.action,
                    payload.asset,
                    '> ' + payload.owner[:8] + '... ' if payload.owner else '',
                    signer[:8] + '... ')

        if payload.action == 'create':
            _create_asset(asset=payload.asset,
                          owner=signer,
                          state=state)
        else:
            raise InvalidTransaction('Unhandled action: {}'.format(
                payload.action))


def _create_asset(asset, owner, state):
    if state.get_asset(asset) is not None:
        raise InvalidTransaction(
            'Invalid action: Asset already exists: {}'.format(asset))
    state.set_asset(asset, owner)
