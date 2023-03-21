import enum
import os
import sys
import string
import json
from glob import glob
from tqdm import tqdm

domain_desc_flag = False # To append domain descriptions or not 
slot_desc_flag = True  # To append slot descriptions or not 
PVs_flag = False # for categorical slots, append possible values as suffix

def preprocess(dial_json, schema, out, idx_out, excluded_domains, frame_idxs, split):
    dial_json_n = dial_json.split("/")[-1]
    dial_json = open(dial_json)
    dial_json = json.load(dial_json)
    for dial_idx in tqdm(range(len(dial_json))):
        dial = dial_json[dial_idx]
        cur_dial = ""

        related_map = {}    # {key1: [(uttr1, value1), (uttr2, value2), ...], key2: [...]}

        for turn_idx, turn in enumerate(dial["turns"]):
            speaker = " [" + turn["speaker"] + "] "
            uttr = turn["utterance"]
            cur_dial += speaker
            cur_dial += uttr

            if turn["speaker"] == "USER":
                active_slot_values = {}
                for frame_idx in range(len(turn["frames"])):
                    frame = turn["frames"][frame_idx]
                    for key, values in frame["state"]["slot_values"].items():
                        # if have multiple answers, select the last one
                        slot_key = f'{frame["service"]}_{key}'
                        value = values[-1]
                        active_slot_values[slot_key] = value
                        # if the value first appears or different from the last one, then mark this as keysent
                        if slot_key not in related_map or value != related_map[slot_key][-1][-1]:
                            tmp_list = related_map.get(slot_key, [])
                            # 0902: add previous system utterance too
                            prev_uttr = dial["turns"][turn_idx - 1]["utterance"] if turn_idx > 0 else "###NULL###"
                            tmp_list.append((prev_uttr, uttr, value))
                            related_map.update({slot_key: tmp_list})

                # iterate through each domain-slot pair in each user turn
                for domain in schema:
                    # skip domains that are not in testing set
                    if domain["service_name"] in excluded_domains:
                        continue
                      
                    slots = domain["slots"]
                    for slot in slots:
                        d_name = domain["service_name"]
                        s_name = slot["name"]
                        # generate schema prompt w/ or w/o natural language descriptions
                        short_d_name = d_name.split("_")[0].lower().strip()
                        schema_prompt = ""
                        schema_prompt += " [domain] " + (short_d_name + " " + domain["description"] if domain_desc_flag else short_d_name)
                        schema_prompt += " [slot] " + (s_name + " " + slot["description"] if slot_desc_flag else s_name)

                        if PVs_flag:
                            # only append possible values if the slot is categorical
                            if slot["is_categorical"]:
                                PVs = ", ".join(slot["possible_values"])
                                schema_prompt += " [PVs] " + PVs
                        
                        if f"{d_name}_{s_name}" in active_slot_values.keys():
                            target_value = active_slot_values[f"{d_name}_{s_name}"]
                            target_value = target_value.strip(string.punctuation)

                            related_uttrs = related_map.get(f"{d_name}_{s_name}", [])

                            ## placing the answer at the front. 
                            chain_of_thought = "because there is a dialogue between the user and the system: "
                            tmp = []
                            for ut in related_uttrs:
                                thought = f'" [SYSTEM] {ut[0]}' if ut[0] != "###NULL###" else '"'
                                thought += f' [USER] {ut[1]}"'
                                tmp.append(thought)
                            chain_of_thought += ", and ".join(tmp)
                            # in MultiWOZ 2.2, directly use description of slot for prompting
                            target_value = f"{target_value}, {chain_of_thought}."
                        else:
                            target_value = "NONE"
                        
                        line = {"dialogue": cur_dial + schema_prompt, "result": target_value}
                        out.write(json.dumps(line))
                        out.write("\n")

                        # write idx file for post-processing decoding
                        idx_list = [ dial_json_n, dial_idx, turn_idx, frame_idxs[d_name], d_name, s_name ]
                        idx_out.write("|||".join([str(item) for item in idx_list]))
                        idx_out.write("\n")


def get_predicted_slot_value(output_sent):
    return output_sent.split(",")[0].strip()
