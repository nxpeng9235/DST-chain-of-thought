#!/usr/bin/env bash

set -x

THIS_DIR="$( cd "$( dirname "$0" )" && pwd )"

until [[ -z "$1" ]]
do
    case $1 in
        --custom)
            shift; CUSTOM_FILE=$1;
            shift;;
        --ckpt_dir)
            shift; CKPT_DIR=$1;
            shift;;
    esac
done

if [[ ${CUSTOM_FILE} ]]; then
    rm ${THIS_DIR}/utils.py
    cp ${CUSTOM_FILE} ${THIS_DIR}/utils.py
fi

for dir in ${CKPT_DIR}/outputs/checkpoint-*
do
    if [ -d "$dir" ]; then
        echo "Evaluating $dir..."

        python3 finegrain_postprocess.py --data_dir ../data/woz2.0 --out_dir $dir/finegrain --test_idx ${CKPT_DIR}/data-bin/test.idx --prediction_txt $dir/generated_predictions.txt --dataset woz2.0
        python3 finegrain_eval.py --data_dir ../data/woz2.0 --prediction_dir $dir/finegrain --eval_set test --dataset woz2.0 --output_metric_file $dir/finegrain/dummy_score_0-6.json --length_range 0-6
        python3 finegrain_eval.py --data_dir ../data/woz2.0 --prediction_dir $dir/finegrain --eval_set test --dataset woz2.0 --output_metric_file $dir/finegrain/dummy_score_6-8.json --length_range 6-8
        python3 finegrain_eval.py --data_dir ../data/woz2.0 --prediction_dir $dir/finegrain --eval_set test --dataset woz2.0 --output_metric_file $dir/finegrain/dummy_score_8-10.json --length_range 8-10
        python3 finegrain_eval.py --data_dir ../data/woz2.0 --prediction_dir $dir/finegrain --eval_set test --dataset woz2.0 --output_metric_file $dir/finegrain/dummy_score_10-40.json --length_range 10-40

        python3 finegrain_eval_cot.py --data_dir ../data/woz2.0 --prediction_dir $dir/finegrain --eval_set test --dataset woz2.0 --output_metric_file $dir/finegrain/dummy_score_1.json --length_range 1
        python3 finegrain_eval_cot.py --data_dir ../data/woz2.0 --prediction_dir $dir/finegrain --eval_set test --dataset woz2.0 --output_metric_file $dir/finegrain/dummy_score_2.json --length_range 2
        python3 finegrain_eval_cot.py --data_dir ../data/woz2.0 --prediction_dir $dir/finegrain --eval_set test --dataset woz2.0 --output_metric_file $dir/finegrain/dummy_score_3.json --length_range 3

        # python3 finegrain_postprocess.py --data_dir ../data/simulated-dialogue/sim-R-M --out_dir $dir/finegrain --test_idx ${CKPT_DIR}/data-bin/test.idx --prediction_txt $dir/generated_predictions.txt --dataset m2m-R-M
        # python3 finegrain_eval.py --data_dir ../data/simulated-dialogue/sim-R-M --prediction_dir $dir/finegrain --eval_set test --dataset m2m-R-M --output_metric_file $dir/finegrain/dummy_score_0-10.json --length_range 0-10
        # python3 finegrain_eval.py --data_dir ../data/simulated-dialogue/sim-R-M --prediction_dir $dir/finegrain --eval_set test --dataset m2m-R-M --output_metric_file $dir/finegrain/dummy_score_10-15.json --length_range 10-15
        # python3 finegrain_eval.py --data_dir ../data/simulated-dialogue/sim-R-M --prediction_dir $dir/finegrain --eval_set test --dataset m2m-R-M --output_metric_file $dir/finegrain/dummy_score_15-20.json --length_range 15-20
        # python3 finegrain_eval.py --data_dir ../data/simulated-dialogue/sim-R-M --prediction_dir $dir/finegrain --eval_set test --dataset m2m-R-M --output_metric_file $dir/finegrain/dummy_score_20-40.json --length_range 20-40

        # python3 finegrain_eval_cot.py --data_dir ../data/simulated-dialogue/sim-R-M --prediction_dir $dir/finegrain --eval_set test --dataset m2m-R-M --output_metric_file $dir/finegrain/dummy_score_1.json --length_range 1
        # python3 finegrain_eval_cot.py --data_dir ../data/simulated-dialogue/sim-R-M --prediction_dir $dir/finegrain --eval_set test --dataset m2m-R-M --output_metric_file $dir/finegrain/dummy_score_2.json --length_range 2
        # python3 finegrain_eval_cot.py --data_dir ../data/simulated-dialogue/sim-R-M --prediction_dir $dir/finegrain --eval_set test --dataset m2m-R-M --output_metric_file $dir/finegrain/dummy_score_3.json --length_range 3

        # python3 finegrain_postprocess.py --data_dir ../data/multiwoz/data/MultiWOZ_2.2 --out_dir $dir/finegrain --test_idx ${CKPT_DIR}/data-bin/test.idx --prediction_txt $dir/generated_predictions.txt --dataset multiwoz2.2
        # python3 finegrain_eval.py --data_dir ../data/multiwoz/data/MultiWOZ_2.2 --prediction_dir $dir/finegrain --eval_set test --dataset multiwoz2.2 --output_metric_file $dir/finegrain/dummy_score_0-10.json --length_range 0-10
        # python3 finegrain_eval.py --data_dir ../data/multiwoz/data/MultiWOZ_2.2 --prediction_dir $dir/finegrain --eval_set test --dataset multiwoz2.2 --output_metric_file $dir/finegrain/dummy_score_10-15.json --length_range 10-15
        # python3 finegrain_eval.py --data_dir ../data/multiwoz/data/MultiWOZ_2.2 --prediction_dir $dir/finegrain --eval_set test --dataset multiwoz2.2 --output_metric_file $dir/finegrain/dummy_score_15-20.json --length_range 15-20
        # python3 finegrain_eval.py --data_dir ../data/multiwoz/data/MultiWOZ_2.2 --prediction_dir $dir/finegrain --eval_set test --dataset multiwoz2.2 --output_metric_file $dir/finegrain/dummy_score_20-40.json --length_range 20-40

        # python3 finegrain_eval_cot.py --data_dir ../data/multiwoz/data/MultiWOZ_2.2 --prediction_dir $dir/finegrain --eval_set test --dataset multiwoz2.2 --output_metric_file $dir/finegrain/dummy_score_1.json --length_range 1
        # python3 finegrain_eval_cot.py --data_dir ../data/multiwoz/data/MultiWOZ_2.2 --prediction_dir $dir/finegrain --eval_set test --dataset multiwoz2.2 --output_metric_file $dir/finegrain/dummy_score_2.json --length_range 2
        # python3 finegrain_eval_cot.py --data_dir ../data/multiwoz/data/MultiWOZ_2.2 --prediction_dir $dir/finegrain --eval_set test --dataset multiwoz2.2 --output_metric_file $dir/finegrain/dummy_score_3.json --length_range 3
    fi
done 
