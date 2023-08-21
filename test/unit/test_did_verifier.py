# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

from pathlib import Path

from c2ng.service.did.issuer import gen_verifier_config
from c2ng.uas_sim.did_verifier import verify


def test_did_verifier():
    issuer_did = Path('did/issuer.did').read_text().strip()
    resource_id = 'sim-drone-id'
    config = gen_verifier_config(issuer_did, resource_id)
    token = Path(f'did/{resource_id}.jwt').read_text().strip()
    verified, error = verify(config, resource_id, token)
    assert verified
    assert not error
