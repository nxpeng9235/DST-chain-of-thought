#!/usr/bin/env bash

THIS_DIR="$( cd "$( dirname "$0" )" && pwd )"

DATA_DIR=${THIS_DIR}/data-bin
OUTPUT_DIR=${THIS_DIR}/outputs/t5small_mwoz2.2

CUDA_VISIBLE_DEVICES=5

python postprocess.py --data_dir "$DATA_DIR" --out_dir "$DATA_DIR/dummy/" --test_idx "$DATA_DIR/test.idx" \
    --prediction_txt "$OUTPUT_DIR/generated_predictions.txt"

python eval.py --data_dir "$DATA_DIR" --prediction_dir "$DATA_DIR/dummy/" \
    --output_metric_file "$DATA_DIR/dummy/prediction_score"