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

from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.handler import TransactionHandler

from codeSmell_processor.codeSmell_state import codeSmell
from codeSmell_processor.codeSmell_state import codeSmellState
from codeSmell_processor.codeSmell_state import CODESMELL_NAMESPACE
from codeSmell_processor.codeSmell_payload import codeSmellPayload

LOGGER = logging.getLogger(__name__)

class codeSmellTransactionHandler(TransactionHandler):

    @property
    def family_name(self):
        return 'code-smell'

    @property
    def family_versions(self):
        return ['0.1']

    @property
    def namespaces(self):
        return [CODESMELL_NAMESPACE]

    def apply(self, transaction, context):
        header = transaction.header
        signer = header.signer_public_key

        codeSmell_payload = codeSmellPayload.from_bytes(transaction.payload)
        codeSmell_state = codeSmellState(context)


        if codeSmell_payload.action == 'create':

            code_smell = codeSmell (
                         name=codeSmell_payload.name,
                         value=codeSmell_payload.value,
                         action=codeSmell_payload.action,
                         owner=signer)

            codeSmell_state.set_codeSmell(codeSmell_payload.name, code_smell)
            _display("Peer {} created a codeSmell config.".format(signer[:6]))

        else:
            raise InvalidTransaction('Unhandled action: {}'.format(
                payload.action))

def _display(msg):
    n = msg.count("\n")

    if n > 0:
        msg = msg.split("\n")
        lenght = max(len(line) for line in msg)
    else:
        lenght = len(msg)
        msg = [msg]

    #pylint: disable=logging-not-lazy
    LOGGER.debug("+" + (lenght + 2) * "-" + "+")
    for line in msg:
        LOGGER.debug("+" + line.center(lenght) + " +")
    LOGGER.debug("+" + (lenght + 2) * "-" + "+")
