import torch
import json
import argparse
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

DEVICE=torch.device("cuda:0")

QUESTION_LIST = {
    "birth_date": "When is {}'s birthday? {}.",
    "birth_place": "Where is {}'s birth place? {}.",
    "university": "Which university did {} attend? {}.",
    "major": "What is {}'s major? {}.",
    "company": "Which company did {} work in? {}.",
    "workplace": "Which city does {} work in? {}."
}
STATEMENT_LIST = {
    "birth_date": "{} was born on {}.",
    "birth_place": "{} was born at {}.",
    "university": "The university that {} went to is {}.",
    "major": "{} focused on {} during her university study.",
    "company": "{} worked for {}.",
    "workplace": "The city {} worked in is {}."
}

def calculate_perplexity(sentence, model, tokenizer):
    model.eval()
    tokenize_input = tokenizer.tokenize(sentence)
    tensor_input = torch.tensor([tokenizer.convert_tokens_to_ids(tokenize_input)])
    with torch.no_grad():
        loss = model(tensor_input.to(DEVICE), labels=tensor_input)[0]
    return torch.exp(loss.float()).item()

def answer_question(prompt, data_item, args, model, tokenizer):
    item_result = {}
    for type in ["first_type_info", "second_type_info"]:
        candidate_qa_pair = prompt.format(
            data_item["full_name"], 
            data_item[type][args.field])
        ppl = calculate_perplexity(candidate_qa_pair, model, tokenizer)
        item_result[data_item[type]["type_name"]] = {
            "QA": candidate_qa_pair,
            "ppl": ppl
        }

    prefer_type = data_item["first_type_info"]["type_name"] \
        if item_result[data_item["first_type_info"]["type_name"]]["ppl"] < item_result[data_item["second_type_info"]["type_name"]]["ppl"] \
            else data_item["second_type_info"]["type_name"]

    return item_result, prefer_type

def calculate_type_acc(args):
    model = AutoModelForCausalLM.from_pretrained(args.model_path, low_cpu_mem_usage=True, torch_dtype=torch.float16, device_map="auto")
    tokenizer = AutoTokenizer.from_pretrained(args.model_path)

    with open(args.test_file, 'r', encoding='utf8') as f:
        total_data = json.load(f)

    result_list = []
    if args.use_statement:
        prompt = STATEMENT_LIST[args.field]
    else:
        prompt = QUESTION_LIST[args.field]
    first_type_name = total_data[0]["first_type_info"]["type_name"]
    second_type_name = total_data[0]["second_type_info"]["type_name"]

    first_type_cnt = 0
    second_type_cnt = 0

    for data_item in tqdm(total_data):
        result, prefer_type = answer_question(prompt, data_item, args, model, tokenizer)
        result_list.append(result)
        
        if prefer_type == first_type_name:
            first_type_cnt += 1
        elif prefer_type == second_type_name:
            second_type_cnt += 1
        else:
            raise ValueError

    with open("./{}_ppl_acc_{}_{}.json".format(args.model_path.split("/")[-2], args.field, "statement" if args.use_statement else "question"), 'w', encoding='utf8') as f:
        json.dump({"choice {}".format(first_type_name): first_type_cnt, 
                   "choice {}".format(second_type_name):second_type_cnt,
                   "total_result":result_list}, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path")
    parser.add_argument("--test_file")
    parser.add_argument("--field")
    parser.add_argument("--use_statement", action="store_true")

    args = parser.parse_args()

    calculate_type_acc(args)
