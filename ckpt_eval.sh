#!/usr/bin/env bash

THIS_DIR="$( cd "$( dirname "$0" )" && pwd )"

EVALUATION_ARGS=""

until [[ -z "$1" ]]
do
    case $1 in
        --dataset)
            shift; DATASET=$1;
            shift;;
        --exp_dir)
            shift; HDFS_DIR=$1;
            shift;;
        --output)
            shift; HDFS_OUTPUT=$1;
            shift;;
        --custom)
            shift; CUSTOM_FILE=$1;
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

if [[ ! ${HDFS_OUTPUT} ]]; then
    HDFS_OUTPUT="${HDFS_DIR}/evaluations"
fi
mkdir -p ${HDFS_OUTPUT}

if [[ ${CUSTOM_FILE} ]]; then
    rm ${THIS_DIR}/src/utils.py
    cp ${CUSTOM_FILE} ${THIS_DIR}/src/utils.py
fi

if [[ ! ${DATASET} ]]; then
    DATASET="multiwoz2.2"
fi

mkdir ${THIS_DIR}/data/
if [[ ${DATASET} == "multiwoz2.2" ]]; then
    echo "Downloading Multiwoz Data..."
    DATA_DIR=${THIS_DIR}/data/multiwoz/data/MultiWOZ_2.2
elif [[ ${DATASET} == "multiwoz2.1" ]]; then
    echo "Downloading Multiwoz Data..."
    DATA_DIR=${THIS_DIR}/data/multiwoz/data/MultiWOZ_2.1_as_2.2
elif [[ ${DATASET} == "m2m-R-M" ]]; then
    echo "Downloading M2M Data..."
    DATA_DIR=${THIS_DIR}/data/simulated-dialogue/sim-R-M
elif [[ ${DATASET} == "m2m-R" ]]; then
    echo "Downloading M2M Data..."
    DATA_DIR=${THIS_DIR}/data/simulated-dialogue/sim-R
elif [[ ${DATASET} == "m2m-M" ]]; then
    echo "Downloading M2M Data..."
    DATA_DIR=${THIS_DIR}/data/simulated-dialogue/sim-M
elif [[ ${DATASET} == "woz2.0" ]]; then
    echo "Downloading woz2.0 Data..."
    DATA_DIR=${THIS_DIR}/data/woz2.0
elif [[ ${DATASET} == "dstc2" ]]; then
    echo "Downloading dstc2 Data..."
    DATA_DIR=${THIS_DIR}/data/dstc2
elif [[ ${DATASET} == "sgd" ]]; then
    echo "Downloading sgd Data..."
    DATA_DIR=${THIS_DIR}/data/dstc8-schema-guided-dialogue
else
    echo "DATASET should be chosen from ['multiwoz2.2', 'multiwoz2.1', 'm2m-R-M', 'm2m-R', 'm2m-M', 'woz2.0', 'dstc2', 'sgd']"
    exit -3
fi

echo "Downloading data-bin and checkpoints..."

DATA_BIN_DIR=${HDFS_DIR}/data-bin
CKPT_DIR=${HDFS_DIR}/outputs

echo "Evaluting all checkpoints..."

for dir in ${CKPT_DIR}/checkpoint-*
do
    if [ -d "$dir" ]; then
        echo "Evaluating $dir..."

        # python3 src/train.py \
        #     --train_file "$DATA_BIN_DIR/train.json" \
        #     --validation_file "$DATA_BIN_DIR/dev.json" \
        #     --test_file "$DATA_BIN_DIR/test.json" \
        #     --do_predict \
        #     --predict_with_generate \
        #     --model_name_or_path $dir/ \
        #     --output_dir $dir/ ${EVALUATION_ARGS} || exit -200

        echo "Doing Prediction & Evaluation..."

        python3 src/postprocess.py --data_dir "$DATA_DIR" --out_dir "$dir/dummy/" --test_idx "$DATA_BIN_DIR/test.idx" \
            --prediction_txt "$dir/generated_predictions.txt" --dataset ${DATASET}

        python3 src/eval.py --data_dir "$DATA_DIR" --prediction_dir "$dir/dummy/" \
            --output_metric_file "$dir/dummy/prediction_score" --dataset ${DATASET}
    fi
done 
