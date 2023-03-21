#!/usr/bin/env bash

THIS_DIR="$( cd "$( dirname "$0" )" && pwd )"

TIME=`date +%Y%m%d%H%M%S`

until [[ -z "$1" ]]
do
    case $1 in
        --dataset)
            shift; DATASET=$1;
            shift;;
        --custom)
            shift; CUSTOM_FILE=$1;
            shift;;
        --data-bin)
            shift; HDFS_DATA_BIN=$1;
            shift;;
    esac
done

if [[ ${CUSTOM_FILE} ]]; then
    rm ${THIS_DIR}/src/utils.py
    cp ${CUSTOM_FILE} ${THIS_DIR}/src/utils.py
fi

if [[ ! ${DATASET} ]]; then
    DATASET="multiwoz2.2"
fi

mkdir -p ${THIS_DIR}/data/
if [[ ${DATASET} == "multiwoz2.2" ]]; then
    echo "Loading Multiwoz Data..."
    DATA_DIR=${THIS_DIR}/data/multiwoz/data/MultiWOZ_2.2
elif [[ ${DATASET} == "multiwoz2.1" ]]; then
    echo "Loading Multiwoz Data..."
    DATA_DIR=${THIS_DIR}/data/multiwoz/data/MultiWOZ_2.1_as_2.2
elif [[ ${DATASET} == "multiwoz2.0" ]]; then
    echo "Loading Multiwoz Data..."
    DATA_DIR=${THIS_DIR}/data/multiwoz/data/MultiWOZ_2.0
elif [[ ${DATASET} == "m2m-R-M" ]]; then
    echo "Loading M2M Data..."
    DATA_DIR=${THIS_DIR}/data/simulated-dialogue/sim-R-M
elif [[ ${DATASET} == "m2m-R" ]]; then
    echo "Loading M2M Data..."
    DATA_DIR=${THIS_DIR}/data/simulated-dialogue/sim-R
elif [[ ${DATASET} == "m2m-M" ]]; then
    echo "Loading M2M Data..."
    DATA_DIR=${THIS_DIR}/data/simulated-dialogue/sim-M
elif [[ ${DATASET} == "woz2.0" ]]; then
    echo "Loading woz2.0 Data..."
    DATA_DIR=${THIS_DIR}/data/woz2.0
elif [[ ${DATASET} == "dstc2" ]]; then
    echo "Loading dstc Data..."
    DATA_DIR=${THIS_DIR}/data/dstc2
elif [[ ${DATASET} == "sgd" ]]; then
    echo "Loading sgd Data..."
    DATA_DIR=${THIS_DIR}/data/dstc8-schema-guided-dialogue
else
    echo "DATASET should be chosen from ['multiwoz2.2', 'multiwoz2.1', 'm2m-R-M', 'm2m-R', 'm2m-M', 'woz2.0', 'dstc2', 'sgd']"
    exit -3
fi

cd ${THIS_DIR}

echo "Doing Preprocessing..."

DATA_BIN_DIR=${THIS_DIR}/data-bin-$TIME

if [[ ! ${HDFS_DATA_BIN} ]]; then
    mkdir -p ${DATA_BIN_DIR}/
    python3 src/preprocess.py ${DATA_DIR}/ ${DATA_BIN_DIR}/ ${DATASET} || exit -100
else
    cp -r ${HDFS_DATA_BIN}/ ${DATA_BIN_DIR}
fi

