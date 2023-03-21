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

change_dict = {
    "What's the fare per ticket for journey?": "How much is the fare per ticket for the journey?",
    "What's the subcategory of event, either a music genre or sport name?": "What is the subcategory of event?",
    "What's the whether the flight arrives the next day?": "Will the flight arrive the next day?",
    "What's the whether the hotel has internet?": "Does the hotel have internet?",
    "What's the boolean flag indicating if the property is furnished?": "Is the property furnished?",
    "What's the boolean flag indicating if pets are allowed?": "Are pets allowed in the apartments?",
    "What's the boolean flag indicating if the hotel has wifi?": "Does the hotel has wifi?",
    "What's the whether or not smoking is allowed inside the place?": "Is smoking allowed inside the place?",
    "What's the language to use for subtitles (or None for no subtitles)?": "What's the language to use for subtitles?",
    "What's the whether the restaurant has outdoor seating available?": "Does the restaurant has outdoor seating available?",
    "What's the whether the restaurant has adequate vegetarian options?": "Does the restaurant has adequate vegetarian options?",
    "What's the boolean flag whether ride is shared with other passengers?": "Is the ride shared with other passengers?",
    "What's the boolean flag indicating whether entrance to attraction is free?": "Is the entrance to attraction free?",
    "What's the boolean flag indicating whether attraction is good for to take kids to?": "Is the attraction good for taking kids to?",
    "What's the whether to carry excess baggage in the bus?": "Does the passenger need to carry excess baggage in the bus?",
    "What's the whether the flight is a direct one?": "Is the flight a direct one?",
    "What's the boolean flag indicating if the house has laundry service?": "Does the house have laundry service?",
    "What's the whether the transaction is private or not?": "Is the transaction private?",
    "What's the whether to purchase insurance?": "Does the client need to purchase insurance?",
    "What's the boolean flag indicating if the salon is unisex": "Is the salon unisex?",
    "What's the address of the stylist/salon?": "What's the address of the stylist or salon?",
    "What's the whether to add trip protection to reservation, for a fee?": "Does the client need to add a trip protection fee to reservation?",
    "What's the whether the booking is refundable or not?": "Is the booking refundable?",
    "What's the boolean flag indicating whether the flight is a red-eye flight?": "Is the flight a red-eye flight?",
    "What's the boolean flag indicating if pets are allowed in the hotel?": "Are pets allowed in the hotel?",
    "What's the boolean flag indicating if subtitles are desired for this movie?": "Are subtitles desired for this movie?",
    "What's the boolean flag indicating if the restaurant serves alcohol?": "Does the restaurant serve alcohol?",
    "What's the boolean flag indicating if the restaurant has live music?": "Does the restaurant have live music?",
    "What's the boolean flag indicating if the dentist offers cosmetic services?": "Does the dentist offer cosmetic services?"
}

def preprocess(dial_json, schema, out, idx_out, excluded_domains, frame_idxs, split):
    dial_json_n = dial_json.split("/")[-1]
    dial_json = open(dial_json)
    dial_json = json.load(dial_json)
    for dial_idx in tqdm(range(len(dial_json))):
        dial = dial_json[dial_idx]
        cur_dial = ""

        related_map = {}    # {key1: [(uttr1, value1), (uttr2, value2), ...], key2: [...]}

        for turn_idx, turn in enumerate(dial["turns"]):
            speaker = f' The {turn["speaker"].lower()}: '
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

                        # modify the schema into Multiple-Choice questions
                        # 1. if contain *possible values*, switch into MCQs.
                        # 2. if not contain, switch into common QAs. 

                        schema_prompt = "Answer the question based on the dialogue between the user and the system."

                        # don't consider domain
                        schema_prompt += " | Question: "
                        
                        question = f"What's the {slot['description'].lower()}?"
                        question = change_dict.get(question, question)

                        schema_prompt += question

                        if PVs_flag and slot["is_categorical"]:
                            # only append possible values if the slot is categorical
                                schema_prompt += " | Choices:"
                                choices = slot["possible_values"]
                                for cho, cap in zip(choices, string.ascii_uppercase[:len(choices)]):
                                    schema_prompt += f" ({cap}) {cho}"
                        
                        schema_prompt += " | Dialogue:"
                        schema_prompt += cur_dial
                        
                        if slot["name"] in active_slot_values.keys():
                            target_value = active_slot_values[slot["name"]]
                            # related utterances for reasoning
                            related_uttrs = related_map.get(slot["name"], [])

                            ## placing the answer at the front. 
                            chain_of_thought = "because there is a dialogue between the user and the system: "
                            tmp = []
                            for ut in related_uttrs:
                                thought = f'" The system: {ut[0]}' if ut[0] != "###NULL###" else '"'
                                thought += f' The user: {ut[1]}"'
                                tmp.append(thought)
                            chain_of_thought += ", and ".join(tmp)
                            # in MultiWOZ 2.2, directly use description of slot for prompting
                            target_value = f"{target_value}, {chain_of_thought}."
                        else:
                            target_value = "There is no answer."
                        
                        line = {"dialogue": schema_prompt, "result": target_value}
                        out.write(json.dumps(line))
                        out.write("\n")

                        # write idx file for post-processing decoding
                        idx_list = [ dial_json_n, dial_idx, turn_idx, frame_idxs[d_name], d_name, s_name ]
                        idx_out.write("|||".join([str(item) for item in idx_list]))
                        idx_out.write("\n")


def get_predicted_slot_value(output_sent):
    if output_sent.lower().startswith("there is no answer"):
        return "NONE"
    tmp = output_sent.split(",")
    if len(tmp) > 1:
        return tmp[0].strip()
    return "NONE"
