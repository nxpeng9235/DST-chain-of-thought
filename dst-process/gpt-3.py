import enum
import os
import sys
import json
from glob import glob
from tqdm import tqdm
import subprocess

domain_desc_flag = True # To append domain descriptions or not 
slot_desc_flag = True  # To append slot descriptions or not 
PVs_flag = True # for categorical slots, append possible values as suffix

real_split = {
    "train": "dev",
    "dev": "test",
    "test": "train"
}

def preprocess(dial_json, schema, out, idx_out, excluded_domains, frame_idxs, split):
    split = real_split[split]
    subprocess.run(f"hdfs dfs -get hdfs://haruna/home/byte_arnold_lq_mlnlc/user/pengningxin/experiments/dst-prompt/gpt-data/data-bin/{split}.* /opt/tiger/dst-prompt/data-bin/", shell=True)

def get_predicted_slot_value(output_sent):
    return output_sent.split(",")[0].strip()
