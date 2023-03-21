#1 Use prediction file to update
#2 Use dialogue001 and dialogue 002 
import os
import json
import copy
from glob import glob
import argparse
from utils import get_predicted_slot_value


def main(args):
    if args.dataset.startswith("multiwoz") or args.dataset == "sgd":
        if args.dataset == "multiwoz2.2":
            # create dummy frame as in MultiWOZ2.2 file format
            domains = ["train", "taxi", "bus", "police", "hotel", "restaurant", "attraction", "hospital"]
            # skip domains that are not in the testing set
            excluded_domains = ["police", "hospital", "bus"]
        elif args.dataset == "multiwoz2.0" or args.dataset == "multiwoz2.1":
            # create dummy frame as in MultiWOZ2.2 file format
            domains = ["hotel", "train", "attraction", "restaurant", "taxi", "bus", "hospital"]
            # skip domains that are not in the testing set
            excluded_domains = ["hospital", "bus"]
        elif args.dataset == "sgd":
            domains = ['Alarm_1', 'Buses_3', 'Events_3', 'Flights_4', 'Homes_2', 'Hotels_2', 'Hotels_4', 'Media_3',
                       'Messaging_1', 'Movies_1', 'Movies_3', 'Music_3', 'Payment_1', 'RentalCars_3', 'Restaurants_2',
                       'RideSharing_2', 'Services_1', 'Services_4', 'Trains_1', 'Travel_1', 'Weather_1']
            # skip domains that are not in the testing set
            excluded_domains = []
        else:
            print("Exception! Exiting!")
            exit(-998)

        dummy_frames = []
        for domain in domains:
            # if domain in excluded_domains:
            #     continue
            dummy_frames.append({"service": domain, "state": {"slot_values": {}}})

        # Create dummy jsons to fill in later
        dummy_dial_file_jsons = {}
        split = "test"
        target_jsons = glob(os.path.join(args.data_dir, "{}/*json".format(split)))
        for target_json_n in target_jsons:
            if target_json_n.split("/")[-1] == "schema.json":
                continue
            filename = target_json_n.split("/")[-1]
            dummy_dial_file_json = []
            target_json = json.load(open(target_json_n))
            for dial_json in target_json:
                dial_id = dial_json["dialogue_id"]
                dummy_dial_json = {"dialogue_id": dial_id, "turns":[]}

                for turn in dial_json["turns"]:
                    turn_id = turn["turn_id"]
                    if turn["speaker"] == "USER":
                        dummy_dial_json["turns"].append({"turn_id": turn_id, "speaker": "USER", "frames": copy.deepcopy(dummy_frames)})
                    else:
                        dummy_dial_json["turns"].append(turn)

                dummy_dial_file_json.append(dummy_dial_json)
            dummy_dial_file_jsons.update({filename: dummy_dial_file_json})

        idx_lines = open(args.test_idx).readlines()
        out_lines = open(args.prediction_txt).readlines()

        # fill out dummy jsons with parsed predictions
        for _idx in range(len(idx_lines)):
            idx_list = idx_lines[_idx].strip()
            dial_json_n, dial_idx, turn_idx, frame_idx, d_name, s_name = idx_list.split("|||")

            val = out_lines[_idx].strip()
            # For active slots, update values in the dummy jsons
            if val != "NONE":
                try:
                    predicted_val = get_predicted_slot_value(val).strip()
                    if predicted_val == "NONE":
                        continue
                except:
                    print(f"idx={_idx} output with invalid format, skipping...")
                    continue
                d_s_name = d_name + "-" + s_name

                dummy_dial_file_jsons[dial_json_n][int(dial_idx)]["turns"][int(turn_idx)]["frames"][int(frame_idx)]["state"]["slot_values"].update({d_s_name: [predicted_val]})
            # NONE token means the slot is non-active. Skip the updating option
            else:
                continue

        if not os.path.exists(args.out_dir):
            os.mkdir(args.out_dir)

        # Create dummy json files for evaluation
        for dial_json_n, dummy_dial_file_json in dummy_dial_file_jsons.items():
            with open(os.path.join(args.out_dir, f"dummy_out_{dial_json_n}"), "w") as dummy_out_file:
                json.dump(dummy_dial_file_json, dummy_out_file, indent=4)

    else:
        # dataset formalized to multiwoz 2.2 style
        if args.dataset == "m2m-R-M":
            domains = ["restaurant", "movies"]
        elif args.dataset == "m2m-R":
            domains = ["restaurant"]
        elif args.dataset == "m2m-M":
            domains = ["movies"]
        elif args.dataset == "woz2.0":
            domains = ["restaurant"]
        elif args.dataset == "dstc2":
            domains = ["restaurant"]
        else:
            print("Exception! Exiting!")
            exit(-998)

        dummy_frames = []
        for domain in domains:
            dummy_frames.append({"service": domain, "state": {"slot_values": {}}})
        dummy_dial_file_json = []
        target_json = json.load(open(os.path.join(args.data_dir, "test.json")))
        for dial_json in target_json:
            dial_id = dial_json["dialogue_id"]
            dummy_dial_json = {"dialogue_id": dial_id, "turns": []}

            for turn in dial_json["turns"]:
                turn_id = turn["turn_id"]
                if turn["speaker"] == "USER":
                    dummy_dial_json["turns"].append({"turn_id": turn_id, "speaker": "USER", "frames": copy.deepcopy(dummy_frames)} )
                else:
                    dummy_dial_json["turns"].append(turn)

            dummy_dial_file_json.append(dummy_dial_json)

        idx_lines = open(args.test_idx).readlines()
        out_lines = open(args.prediction_txt).readlines()

        # fill out dummy jsons with parsed predictions
        for _idx in range(len(idx_lines)):
            idx_list = idx_lines[_idx].strip()
            dial_json_n, dial_idx, turn_idx, frame_idx, d_name, s_name = idx_list.split("|||")

            val = out_lines[_idx].strip()
            # For active slots, update values in the dummy jsons
            if val != "NONE":
                try:
                    predicted_val = get_predicted_slot_value(val).strip()
                    if predicted_val == "NONE":
                        continue
                except:
                    print(f"idx={_idx} output with invalid format, skipping...")
                    continue
                d_s_name = d_name + "-" + s_name
                dummy_dial_file_json[int(dial_idx)]["turns"][int(turn_idx)]["frames"][int(frame_idx)]["state"]["slot_values"].update({d_s_name: [predicted_val]})
            # NONE token means the slot is non-active. Skip the updating option
            else:
                continue

        if not os.path.exists(args.out_dir):
            os.mkdir(args.out_dir)

        with open(os.path.join(args.out_dir, "dummy_out.json"), "w") as dummy_out_file:
            json.dump(dummy_dial_file_json, dummy_out_file, indent=4)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="./MultiWOZ_2.2/")
    parser.add_argument("--out_dir", type=str, default="./MultiWOZ_2.2/dummy/")

    parser.add_argument("--test_idx", type=str, default="./MultiWOZ_2.2/test.idx")
    parser.add_argument("--prediction_txt", type=str, default="")
    parser.add_argument("--dataset", type=str, default="multiwoz2.2",
                        choices=["multiwoz2.2", "multiwoz2.1", "multiwoz2.0", "m2m-R-M", "m2m-R", "m2m-M", "woz2.0", "dstc2", "sgd"])
    args = parser.parse_args()

    main(args)
 