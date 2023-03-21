#!/usr/bin/env bash

THIS_DIR="$( cd "$( dirname "$0" )" && pwd )"

BASE_DIR=/home/ningxin
DATA_DIR=${BASE_DIR}/data/multiwoz/data/MultiWOZ_2.2
DATA_BIN_DIR=${THIS_DIR}/data-bin
OUTPUT_DIR=$1

if [[ ! ${OUTPUT_DIR} ]]; then
    OUTPUT_DIR=${THIS_DIR}/outputs
fi

CUDA_VISIBLE_DEVICES=4

python src/postprocess.py --data_dir "$DATA_DIR" --out_dir "$OUTPUT_DIR/dummy/" --test_idx "$DATA_BIN_DIR/test.idx" \
    --prediction_txt "$OUTPUT_DIR/generated_predictions.txt"

python src/eval.py --data_dir "$DATA_DIR" --prediction_dir "$OUTPUT_DIR/dummy/" \
    --output_metric_file "$OUTPUT_DIR/dummy/prediction_score"