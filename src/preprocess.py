import enum
import os
import sys
import json
from glob import glob
from tqdm import tqdm

domain_desc_flag = True # To append domain descriptions or not 
slot_desc_flag = True  # To append slot descriptions or not 
PVs_flag = True # for categorical slots, append possible values as suffix

def preprocess(dial_json, schema, out, idx_out, excluded_domains, frame_idxs):
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
                        if key not in related_map or value != related_map[key][-1][1]:
                            tmp_list = related_map.get(key, [])
                            tmp_list.append((uttr, value))
                            related_map.update({key: tmp_list})

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
                        schema_prompt += " [domain] " + d_name
                        if domain_desc_flag:
                            schema_prompt += " " + domain["description"]
                        schema_prompt += " [slot] "
                        if slot_desc_flag:
                            schema_prompt += slot["description"]
                        else:
                            schema_prompt += s_name
                        if PVs_flag:
                            # only append possible values if the slot is categorical
                            if slot["is_categorical"]:
                                PVs = ", ".join(slot["possible_values"])
                                schema_prompt += " [PVs] " + PVs
                        
                        if slot["name"] in active_slot_values.keys():
                            target_value = active_slot_values[slot["name"]]
                            # related utterances for reasoning
                            related_uttrs = related_map.get(slot["name"], [])
                            chain_of_thought = "Because "
                            chain_of_thought += ", and ".join([f'"{ut[0]}"' for ut in related_uttrs])
                            # in MultiWOZ 2.2, directly use description of slot for prompting
                            slot_prompt = slot['description'] if slot_desc_flag else f"{d_name} {s_name}"
                            target_value = f"{chain_of_thought}, the {slot_prompt} is {target_value}."
                        else:
                            target_value = "NONE"
                        
                        line = {"dialogue": cur_dial + schema_prompt, "result": target_value}
                        out.write(json.dumps(line))
                        out.write("\n")

                        # write idx file for post-processing deocding
                        idx_list = [ dial_json_n, str(dial_idx), turn["turn_id"], str(frame_idxs[d_name]), d_name, s_name ]
                        idx_out.write("|||".join(idx_list))
                        idx_out.write("\n")

            elif turn["speaker"] == "SYSTEM":
                for frame_idx in range(len(turn["frames"])):
                    frame = turn["frames"][frame_idx]
                    for system_slot in frame["slots"]:
                        key, value = system_slot["slot"], system_slot["value"]
                        # if system stated a value that impacted user's decision, add the uttr to related_map
                        if key not in related_map or value != related_map[key][-1][1]:
                            tmp_list = related_map.get(key, [])
                            tmp_list.append((uttr, "##sys##"))
                            related_map.update({key: tmp_list})

            else:
                pass


def main():
    data_path = sys.argv[1]
    data_bin_path = sys.argv[2]

    schema_path = data_path + "schema.json"
    schema = json.load(open(schema_path))

    frame_idxs = {"train": 0, "taxi":1, "bus":2, "police":3, "hotel":4, "restaurant":5, "attraction":6, "hospital":7}

    # skip domains that are not in the testing set
    excluded_domains = ["police", "hospital", "bus"]
    for split in ["train", "dev", "test"]:
        print("--------Preprocessing {} set---------".format(split))
        out = open(os.path.join(data_bin_path, "{}.json".format(split)), "w")
        idx_out = open(os.path.join(data_bin_path, "{}.idx".format(split)), "w")
        dial_jsons = glob(os.path.join(data_path, "{}/*json".format(split)))
        for dial_json in dial_jsons:
            if dial_json.split("/")[-1] != "schema.json":
                preprocess(dial_json, schema, out, idx_out, excluded_domains, frame_idxs)
        idx_out.close()
        out.close()
    print("--------Finish Preprocessing---------")


if __name__=='__main__':
    main()
