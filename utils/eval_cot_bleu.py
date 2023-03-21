import argparse
import sys
import json
import evaluate
from transformers import AutoTokenizer
from nltk.translate.bleu_score import corpus_bleu
from tqdm import tqdm


class SentBLEU:
    def __init__(self, tokenizer_path="/home/ningxin/dst-prompt/t5-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    
    def compute(self, predictions=None, references=None):
        predictions = self.tokenizer(predictions, padding=False)["input_ids"]
        references = self.tokenizer(references, padding=False)["input_ids"]
        return {
            "1-gram BLEU": corpus_bleu(list_of_references=[[ref] for ref in references], hypotheses=predictions, weights=(1, 0, 0, 0)),
            "2-gram BLEU": corpus_bleu(list_of_references=[[ref] for ref in references], hypotheses=predictions, weights=(0, 1, 0, 0)),
            "3-gram BLEU": corpus_bleu(list_of_references=[[ref] for ref in references], hypotheses=predictions, weights=(0, 0, 1, 0)),
            "4-gram BLEU": corpus_bleu(list_of_references=[[ref] for ref in references], hypotheses=predictions, weights=(0, 0, 0, 1)),
        }


def main(args):
    bleu_metric = evaluate.load("sacrebleu") if args.use_sacrebleu else SentBLEU()
    rouge_metric = evaluate.load("rouge")

    with open(args.prediction_txt) as hyp_rf, open(args.testset_file) as ref_rf:
        none_txt = "There is no answer." if args.rmnone else "NONE"
        hypothesis, references = [], []
        for hyp_line, ref_line in tqdm(zip(hyp_rf.readlines(), ref_rf.readlines())):
            hyp_text = hyp_line.strip()
            ref_text = json.loads(ref_line.strip())["result"].strip()
            if ref_line != none_txt:
                try:
                    hypothesis.append(hyp_text.split(',')[0].strip())
                except:
                    hypothesis.append(hyp_text)
                references.append(ref_text.split(',')[0].strip())
            
        print("BLEU score:\n", bleu_metric.compute(predictions=hypothesis, references=references))
        print("Rouge score:\n", rouge_metric.compute(predictions=hypothesis, references=references, use_stemmer=True))




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--prediction_txt", type=str)
    parser.add_argument("--testset_file", type=str)
    parser.add_argument("--rmnone", action="store_true", default=False)
    parser.add_argument("--use_sacrebleu", action="store_true", default=False)
    args = parser.parse_args()

    main(args)

