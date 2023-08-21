import json
from pathlib import Path

from jwt_pep import jwt_pep  # type: ignore  # noqa: F401


def gen_config(resource_id):
    issuer_did = Path('did/issuer.did').read_text().strip()
    issuer_did_self = Path('did/issuer.did.self').read_text().strip()

    config = {
        'resources': {
            'sim-drone-id': {
                'authorization': {
                    'type': 'jwt-vc',
                    'trusted_issuers': {
                        issuer_did: {
                            'issuer_key': issuer_did,
                            'issuer_key_type': 'did'
                        },
                        issuer_did_self: {
                            'issuer_key': issuer_did_self,
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


def did_verifier(config, resource_id, token):
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
    print('CAPS', capabilities)

    if 'CONTROL' not in capabilities[resource_id]:
        return False, 'CONTROL capability is not present'

    # TODO: Handle expiration
    # TODO: Handle DPoP
    return True, None


def test_did_verifier():
    resource_id = 'sim-drone-id'
    config = gen_config(resource_id)
    token = Path(f'did/{resource_id}.jwt').read_text().strip()
    verified, error = did_verifier(config, resource_id, token)
    assert verified
    assert not error
