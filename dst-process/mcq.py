import enum
import os
import sys
import json
from glob import glob
from tqdm import tqdm
import string

domain_desc_flag = True # To append domain descriptions or not 
slot_desc_flag = True  # To append slot descriptions or not 
PVs_flag = True # for categorical slots, append possible values as suffix

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
                        value = values[-1]
                        active_slot_values[key] = value
                        # if the value first appears or different from the last one, then mark this as keysent
                        if key not in related_map or value != related_map[key][-1][-1]:
                            tmp_list = related_map.get(key, [])
                            # 0902: add previous system utterance too
                            prev_uttr = dial["turns"][turn_idx - 1]["utterance"] if turn_idx > 0 else "###NULL###"
                            tmp_list.append((prev_uttr, uttr, value))
                            related_map.update({key: tmp_list})

                # iterate through each domain-slot pair in each user turn
                for domain in schema:
                    # skip domains that are not in testing set
                    if domain["service_name"] in excluded_domains:
                        continue
                      
                    slots = domain["slots"]
                    for slot in slots:
                        # modify the schema into Multiple-Choice questions
                        # 1. if contain *possible values*, switch into MCQs.
                        # 2. if not contain, switch into common QAs. 

                        if PVs_flag and slot["is_categorical"]:
                            schema_prompt = "Choose the best answer to the question based on the dialogue."
                        else:
                            schema_prompt = "Answer the question based on the dialogue."

                        d_name, s_name = slot["name"].split("-")
                        # don't consider domain
                        schema_prompt += " | Question: "
                        schema_prompt += f"What's the {slot['description']}?"

                        if PVs_flag and slot["is_categorical"]:
                            # only append possible values if the slot is categorical
                                schema_prompt += " | Choices:"
                                choices = slot["possible_values"]
                                for cho, cap in zip(choices, string.ascii_uppercase[:len(choices)]):
                                    schema_prompt += f" ({cap}) {cho}"
                        
                        schema_prompt += " | Dialogue:"
                        schema_prompt += cur_dial
                        
                        if slot["name"] in active_slot_values.keys():
                            target_value = active_slot_values[slot["name"]].strip()
                        else:
                            target_value = "NONE"
                        
                        line = {"dialogue": schema_prompt, "result": target_value}
                        out.write(json.dumps(line))
                        out.write("\n")

                        # write idx file for post-processing deocding
                        idx_list = [ dial_json_n, str(dial_idx), turn["turn_id"], str(frame_idxs[d_name]), d_name, s_name ]
                        idx_out.write("|||".join(idx_list))
                        idx_out.write("\n")


def get_predicted_slot_value(output_sent):
    return output_sent.strip()
