from jwt_pep import jwt_pep  # type: ignore  # noqa: F401

from pathlib import Path


def gen_config():
    issuer_did = Path('did/issuer.did').read_text().strip()
    issuer_did_self = Path('did/issuer.did.self').read_text().strip()

    config = {
        'resources': {
            'sim-drone-id': {
                'authorization': {
                    'type': 'jwt-vc',
                    "trusted_issuers": {
                        issuer_did: {
                            'issuer_key': issuer_did,
                            'issuer_key_type': 'did'
                        },
                        issuer_did_self: {
                            'issuer_key': issuer_did_self,
                            'issuer_key_type': 'did'
                        }
                    },
                    "filters": [
                        ["$.vc.credentialSubject.capabilities.'https://flyver.city/uas/ua/sim-drone-id'[*]", "CONTROL"]
                    ]
                }
            }
        }
    }

    return config


def did_verifier(config, resource_id, token):
    if not token:
        return False, "No token provided"

    if not (resource := config['resources'].get(resource_id)):
        return False, "Resource not found"

    trusted_issuers = resource['authorization']['trusted_issuers']
    filter = resource['authorization']['filters']

    jwt_pep_obj = jwt_pep()

    jwt_verified, ver_output = jwt_pep_obj.verify_jwt(
        token=token,
        trusted_issuers=trusted_issuers,
        filter=filter
    )

    print("JWT verified: ", jwt_verified)
    print("JWT verification output: ", ver_output)


def test_did_verifier():
    config = gen_config()
    token = Path('did/sim-drone-id.jwt').read_text().strip()
    did_verifier(config, 'sim-drone-id', token)
    assert False
