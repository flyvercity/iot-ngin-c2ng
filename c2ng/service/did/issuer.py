# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

from pathlib import Path


def gen_verifier_config(issuer_did, resource_id):
    config = {
        'resources': {
            'sim-drone-id': {
                'authorization': {
                    'type': 'jwt-vc',
                    'trusted_issuers': {
                        issuer_did: {
                            'issuer_key': issuer_did,
                            'issuer_key_type': 'did'
                        }
                    },
                    'filters': [
                        [f"$.vc.credentialSubject.capabilities.'{resource_id}'[*]", 'CONTROL']
                    ]
                }
            }
        }
    }

    return config


class DIDIssuer:
    def __init__(self, config):
        self._config = config

    def issue_jwt(self, resource_id):
        jwt_file_path = self._config['resources'][resource_id]['jwt']
        jwt = Path(jwt_file_path).read_text().strip()
        return jwt

    def generate_config(self, resource_id):
        issuer_did_file = self._config['issuer-did']
        issuer_did = Path(issuer_did_file).read_text().strip()
        return gen_verifier_config(issuer_did, resource_id)
