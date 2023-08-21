set -e

KEY_TOOL=integration/ppssi/key_tools.py
JWT_TOOL=integration/ppssi/create_jwt.py
ISSUER_KEY=docker/core/config/did/issuer.pem
ISSUER_DID_FILE=docker/core/config/did/issuer.did
ISSUER_DID_SELF_FILE=docker/core/config/did/issuer.did.self
SIM_DRONE_ID_KEY=docker/core/config/did/sim-drone-id.pem
SIM_DRONE_ID_DID_FILE=docker/core/config/did/sim-drone-id.did
SIM_DRONE_ID_JWT=docker/core/config/did/sim-drone-id.jwt
SIM_DRONE_ID_VC=docker/core/config/did/sim-drone-id.vc-credential.json

python $KEY_TOOL generate_key $ISSUER_KEY
echo "Issuer key generated at $ISSUER_KEY"

python $KEY_TOOL generate_key $SIM_DRONE_ID_KEY
echo "Sim drone key generated at $SIM_DRONE_ID_KEY"

ISSUER_DID=`python $KEY_TOOL show_did --did_method did:key $ISSUER_KEY`
echo $ISSUER_DID > $ISSUER_DID_FILE
echo "Issuer DID: $ISSUER_DID"

ISSUER_DID_SELF=`python $KEY_TOOL show_did $ISSUER_KEY`
echo $ISSUER_DID_SELF > $ISSUER_DID_SELF_FILE
echo "Issuer DID (self): $ISSUER_DID_SELF"

SIM_DRONE_ID_DID=`python $KEY_TOOL show_did --did_method did:key $SIM_DRONE_ID_KEY`
echo $SIM_DRONE_ID_DID > $SIM_DRONE_ID_DID_FILE
echo "Sim drone DID: $SIM_DRONE_ID_DID"

python $JWT_TOOL $ISSUER_KEY $SIM_DRONE_ID_DID $SIM_DRONE_ID_VC \
    --did_method did:key   \
    --validity_time 86400  \
    > $SIM_DRONE_ID_JWT
echo "Sim drone JWT generated at $SIM_DRONE_ID_JWT"
