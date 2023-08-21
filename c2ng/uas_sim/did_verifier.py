# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

import json

# Importing from 'Privacy preserving Self-Sovereign Identities' IoT-NGIN Project
from jwt_pep import jwt_pep  # type: ignore  # noqa: F401


def verify(config, resource_id, token):
    if not token:
        return False, 'No token provided'

    if not (resource := config['resources'].get(resource_id)):
        return False, 'Resource not found'

    trusted_issuers = resource['authorization']['trusted_issuers']
    filter = resource['authorization']['filters']

    jwt_pep_obj = jwt_pep()

    jwt_verified, ver_output = jwt_pep_obj.verify_jwt(
        token=token,
        trusted_issuers=trusted_issuers,
        filter=filter
    )

    if not jwt_verified:
        return False, f'JWS was not verified ({ver_output})'

    payload = json.loads(ver_output)

    vc = payload['vc']
    capabilities = vc['credentialSubject']['capabilities']

    if 'CONTROL' not in capabilities[resource_id]:
        return False, 'CONTROL capability is not present'

    # TODO: Handle expiration
    # TODO: Handle DPoP
    return True, None
