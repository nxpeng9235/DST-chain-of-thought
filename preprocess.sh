#!/usr/bin/env bash

THIS_DIR="$( cd "$( dirname "$0" )" && pwd )"

DATA_DIR=${BASE_DIR}/data/multiwoz/data/MultiWOZ_2.2
DATA_BIN_DIR=${THIS_DIR}/data-bin

mkdir -p ${DATA_BIN_DIR}/

python3 src/preprocess.py ${DATA_DIR}/ ${DATA_BIN_DIR}/
