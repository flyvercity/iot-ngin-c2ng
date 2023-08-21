from pathlib import Path

from c2ng.uas_sim.did_verifier import verify


def gen_config(resource_id):
    issuer_did = Path('did/issuer.did').read_text().strip()

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


def test_did_verifier():
    resource_id = 'sim-drone-id'
    config = gen_config(resource_id)
    token = Path(f'did/{resource_id}.jwt').read_text().strip()
    verified, error = verify(config, resource_id, token)
    assert verified
    assert not error
