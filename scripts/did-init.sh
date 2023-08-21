# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

set -e
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

KEY_TOOL=integration/ppssi/key_tools.py
ISSUER_KEY=docker/core/config/did/issuer.pem
ISSUER_DID_FILE=docker/core/config/did/issuer.did
SIM_DRONE_ID_KEY=docker/core/config/did/sim-drone-id.pem
SIM_DRONE_ID_DID_FILE=docker/core/config/did/sim-drone-id.did

python $KEY_TOOL generate_key $ISSUER_KEY
echo "Issuer key generated at $ISSUER_KEY"

python $KEY_TOOL generate_key $SIM_DRONE_ID_KEY
echo "Sim drone key generated at $SIM_DRONE_ID_KEY"

ISSUER_DID=`python $KEY_TOOL show_did --did_method did:key $ISSUER_KEY`
echo $ISSUER_DID > $ISSUER_DID_FILE
echo "Issuer DID: $ISSUER_DID"

SIM_DRONE_ID_DID=`python $KEY_TOOL show_did --did_method did:key $SIM_DRONE_ID_KEY`
echo $SIM_DRONE_ID_DID > $SIM_DRONE_ID_DID_FILE
echo "Sim drone DID: $SIM_DRONE_ID_DID"

$SCRIPT_DIR/jwt-gen.sh
