import enum
import os
import sys
import string
import json
from glob import glob
from tqdm import tqdm

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

        for turn_idx, turn in enumerate(dial["turns"]):
            speaker = " The user: " if turn["speaker"] == "USER" else " The system: "
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

                # iterate through each domain-slot pair in each user turn
                for domain in schema:
                    # skip domains that are not in testing set
                    if domain["service_name"] in excluded_domains:
                        continue
                      
                    slots = domain["slots"]
                    for slot in slots:
                        d_name, s_name = slot["name"].split("-")
                        # generate schema prompt w/ or w/o natural language descriptions
                        schema_prompt = ""
                        schema_prompt += " | Domain: " + d_name
                        if domain_desc_flag:
                            schema_prompt += " " + domain["description"]
                        schema_prompt += " | Slot: "
                        if slot_desc_flag:
                            schema_prompt += slot["description"]
                        else:
                            schema_prompt += s_name

                        if PVs_flag:
                            # only append possible values if the slot is categorical
                            if slot["is_categorical"]:
                                PVs = ", ".join(slot["possible_values"])
                                schema_prompt += " | Possible values: " + PVs
                        
                        if slot["name"] in active_slot_values.keys():
                            target_value = active_slot_values[slot["name"]]
                            target_value = target_value.strip(string.punctuation)
                        else:
                            target_value = "There is no answer."
                        
                        line = {"dialogue": cur_dial + schema_prompt, "result": target_value}
                        out.write(json.dumps(line))
                        out.write("\n")

                        # write idx file for post-processing decoding
                        idx_list = [ dial_json_n, dial_idx, turn["turn_id"], frame_idxs[d_name], d_name, s_name ]
                        idx_out.write("|||".join([str(item) for item in idx_list]))
                        idx_out.write("\n")


def get_predicted_slot_value(output_sent):
    if output_sent.lower().startswith("there is no answer"):
        return "NONE"
    return output_sent
