#!/usr/bin/env bash

BASE_DIR=/home/ningxin
DATA_DIR=${BASE_DIR}/data/multiwoz/data/MultiWOZ_2.2
EXP_DIR=${BASE_DIR}/code/DST-as-Prompting
OUTPUT_DIR=${EXP_DIR}/outputs

cd ${EXP_DIR}/transformers

CUDA_VISIBLE_DEVICES=4 python3 examples/pytorch/summarization/run_summarization.py \
    --model_name_or_path t5-small \
    --do_train \
    --do_predict \
    --train_file "$DATA_DIR/train.json" \
    --validation_file "$DATA_DIR/dev.json" \
    --test_file "$DATA_DIR/test.json" \
    --source_prefix "" \
    --output_dir "$OUTPUT_DIR/t5small_mwoz2.2" \
    --per_device_train_batch_size=4 \
    --per_device_eval_batch_size=4 \
    --predict_with_generate \
    --text_column="dialogue" \
    --summary_column="state" \
    --save_steps=500000
