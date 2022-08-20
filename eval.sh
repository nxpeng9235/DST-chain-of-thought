#!/usr/bin/env bash

BASE_DIR=/home/ningxin
DATA_DIR=${BASE_DIR}/data/multiwoz/data/MultiWOZ_2.2
EXP_DIR=${BASE_DIR}/code/DST-as-Prompting
OUTPUT_DIR=${EXP_DIR}/outputs/t5small_mwoz2.2

cd ${EXP_DIR}/

CUDA_VISIBLE_DEVICES=5

# python postprocess.py --data_dir "$DATA_DIR" --out_dir "$DATA_DIR/dummy/" --test_idx "$DATA_DIR/test.idx" \
#     --prediction_txt "$OUTPUT_DIR/generated_predictions.txt"

python eval.py --data_dir "$DATA_DIR" --prediction_dir "$DATA_DIR/dummy/" \
    --output_metric_file "$DATA_DIR/dummy/prediction_score"