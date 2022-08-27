#!/usr/bin/env bash

THIS_DIR="$( cd "$( dirname "$0" )" && pwd )"

DATA_DIR=${THIS_DIR}/data-bin
OUTPUT_DIR=${THIS_DIR}/outputs

TIME=`date +%Y%m%d%H%M%S`

CUDA_VISIBLE_DEVICES=0 python3 src/train.py \
    --model_name_or_path t5-large \
    --do_train \
    --do_predict \
    --train_file "$DATA_DIR/train.json" \
    --validation_file "$DATA_DIR/dev.json" \
    --test_file "$DATA_DIR/test.json" \
    --source_prefix "" \
    --output_dir "$OUTPUT_DIR/t5large_mwoz2.2/$TIME" \
    --max_source_length=1024 \
    --max_target_length=256 \
    --per_device_train_batch_size=8 \
    --per_device_eval_batch_size=8 \
    --num_train_epochs=3 \
    --predict_with_generate \
    --text_column="dialogue" \
    --summary_column="result" \
    --save_steps=300000
