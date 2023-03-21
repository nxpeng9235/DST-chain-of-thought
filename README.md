# DST-Prompt

## Code

### Code Structure

```bash
DST-chain-of-thought/
├── data/ # datasets
│   ├── dstc8-schema-guided-dialogue/ # sgd
│   ├── multiwoz/ # MultiWOZ 2.0-2.2
│   ├── simulated-dialogue/ # M2M
│   │   ├── sim-M # M2M-M
│   │   ├── sim-R # M2M-R
│   │   └── sim-R-M # M2M-R-M
│   └── woz2.0/ # woz2.0
│       ├── README.md
│       ├── convert_to_multiwoz_format.py
│       ├── dev
│       │   ├── dialogues_001.json
│       │   └── dialogues_002.json
│       ├── dialog_acts.json
├── dst-process/ # scripts for pre-processing & post-processing
├── finegrain/ # scripts for finegrain analysis
├── results/ # experiment result file
├── src/ # main source py files
├── t5-base/ # pretrain model
├── utils/ # utils
├── ckpt_eval.sh # eval checkpoints
├── eval.sh # deprecated
├── predict.sh # only predict without eval
├── run.sh # run experiments
└── train.sh # deprecated
```

### How to Run Experiments?

Run `bash run.sh + ##arguments##`. You should indicate a specific script for pre-processing and post-processing. (`preprocess()` for pre-processing in `src/preprocess.py` and `get_predicted_slot_value()` for post-processing in `src/postprocess.py`). For example:

```bash
# train MultiWOZ 2.2 under baseline settings
bash run.sh --nproc_per_node 2 --dataset multiwoz2.2 --custom ./dst-process/baseline.py --model_name_or_path ./t5-base --do_train --source_prefix= --max_source_length=1024 --max_target_length=512 --per_device_train_batch_size=16 --gradient_accumulation_steps=4 --num_train_epochs=6 --text_column=dialogue --summary_column=result --save_strategy=epoch --learning_rate=5e-5 --seed=42

# train MultiWOZ 2.2 under preprocessed data-bin
bash run.sh --nproc_per_node 2 --dataset multiwoz2.2 --custom ./dst-process/baseline.py --data-bin ../experiments/data-bin-files/multiwoz-22-sdp-data-bin/ --model_name_or_path ./t5-base --do_train --source_prefix= --max_source_length=1024 --max_target_length=512 --per_device_train_batch_size=16 --gradient_accumulation_steps=4 --num_train_epochs=6 --text_column=dialogue --summary_column=result --save_strategy=epoch --learning_rate=5e-5 --seed=42
```

After training, the data-bin files as well as checkpoint files will be saved in `./results/`, named based on ***dataset*** and ***timestamp***.


### Prediction and Evaluation

Run `bash ckpt_eval.sh + ##arguments##`. You should indicate dataset, input directory and the same customized pre-process/post-process script as the one used in training. The estimated scores could be found in `exp_dir/outputs/checkpoint_dir/dummy/prediction_score`.


If necessary, you could run predictions on testsets independently by running `bash predict.sh + ##arguments##`.


## Pre-processing / Post-processing Flow

### Pre-processing

对每轮对话，我们遍历每个domain的每个slot，因此，数据集的样本行数 $\approx$ #dialogue * #turn * #domain * #slot，例如，一个数据集有100个dialogue，每个dialogue有10轮，总共有3个domain，每个domain有6个slot，则数据集总行数 = 100 * 10 * 3 * 6 = 18000.

数据集的domain/slot信息可以在数据集文件夹内的`schema.json`中找到。

#### Input

对于一个dialogue $D$, 有 $n$ 轮对话，每轮对话 $t_i$ 都有user utterance $u_i$ 和 system utterance $s_i$。假设我们需要关注 $d$ domain 下的某个slot $k$，该slot的possible values有$pv_1$, $pv_2$, $pv_3$...。那对于不同的模型有不同的input-prompt:

* SDP: `[USER] u_1 [SYSTEM] s_1 [USER] u_2 [SYSTEM] s_2 ... [USER] u_i [SYSTEM] s_i [domain] d [slot] k [PVs] pv_1, pv_2, pv_3...`
* COT: `The user: u_1. The system: s_1. The user: u_2. The system: s_2.... The user: u_i. The system: s_i. | Domain: d | Slot: k | Possible values: pv_1, pv_2, pv_3...`

* COT-QA: `Answer the question based on the dialogue: Question: ##Designed question based on d and k## | Choices: A) pv_1, B) pv_2, C) pv_3... | Dialogues: The user: u_1. The system: s_1. The user: u_2. The system: s_2.... The user: u_i. The system: s_i.`

#### Output

* SDP: 直接输出value

* COT: 在同个对话中，若某slot value的值第一次出现，或与上一时刻的值不同，则认为该时刻utterance为关键句 $ks$，输出时，除了输出value，同时输出关键句，i.e. `v, because there is a dialogue between the user and the system: ks_1, ks_2, ... and ks_n.`

* COT + GPT3: 将关键句 $ks$ 通过GPT-3改写成第三人称 $ks_{gpt}$，作为COT-explanation，i.e. `v, because ks_{gpt}_1, ks_{gpt}_2, ... and ks_{gpt}_n.`



###### ～ 参考 https://github.com/chiahsuan156/DST-as-Prompting

