# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
${SCRIPT_DIR}/service-follow.sh ctrl-core.sh c2ng
