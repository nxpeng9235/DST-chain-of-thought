#!/usr/bin/env bash

THIS_DIR="$( cd "$( dirname "$0" )" && pwd )"

EVALUATION_ARGS=""

until [[ -z "$1" ]]
do
    case $1 in
        --exp_dir)
            shift; HDFS_DIR=$1;
            shift;;
        --output)
            shift; HDFS_OUTPUT=$1;
            shift;;
        *)
            EVALUATION_ARGS="${EVALUATION_ARGS} $1";
            shift;
    esac
done

if [[ ! ${HDFS_DIR} ]]; then
    echo "Please provide input directory!"
    exit -1
fi

echo "Downloading data-bin and checkpoints..."

DATA_BIN_DIR=${HDFS_DIR}/data-bin
CKPT_DIR=${HDFS_DIR}/outputs

echo "Evaluting all checkpoints..."

for dir in ${CKPT_DIR}/checkpoint-*
do
    if [ -d "$dir" ]; then
        echo "Evaluating $dir..."

        python3 src/train.py \
            --train_file "$DATA_BIN_DIR/train.json" \
            --validation_file "$DATA_BIN_DIR/dev.json" \
            --test_file "$DATA_BIN_DIR/test.json" \
            --do_predict \
            --predict_with_generate \
            --model_name_or_path $dir/ \
            --output_dir $dir/ ${EVALUATION_ARGS} || exit -200

    fi
done 
