# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

set -e

JWT_TOOL=integration/ppssi/create_jwt.py
ISSUER_KEY=docker/core/config/did/issuer.pem
SIM_DRONE_ID_DID_FILE=docker/core/config/did/sim-drone-id.did
SIM_DRONE_ID_VC=docker/core/config/did/sim-drone-id.vc-credential.json
SIM_DRONE_ID_JWT=docker/core/config/did/sim-drone-id.jwt

SIM_DRONE_ID_DID=`cat $SIM_DRONE_ID_DID_FILE`

python $JWT_TOOL $ISSUER_KEY $SIM_DRONE_ID_DID $SIM_DRONE_ID_VC \
    --did_method did:key   \
    --validity_time 86400  \
    > $SIM_DRONE_ID_JWT
echo "Sim drone JWT generated at $SIM_DRONE_ID_JWT"