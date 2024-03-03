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
    "workplace": "Which city does {} work in? {}.",
}
STATEMENT_LIST = {
    "birth_date": "{}'s birthday is on {}.",
    "birth_place": "{} was born at {}.",
    # "university": "The university that {} went to is {}.",
    "university": "{} received education at the {}.",
    "major": "{} focused on {} during her university study.",
    "company": "{} worked for {}.",
    "workplace": "The city {} worked in is {}.",
}
result_dict = {
        "Scientific_reports":[0] * 10,
        "Novels":[0] * 10, 
        "Forum_discussions":[0] * 10, 
        "Social_media":[0] * 10, 
        "Newspapers":[0] * 10, 
        "Wikipedia":[0] * 10, 
        "Blogs":[0] * 10, 
        "Personal_Interviews":[0] * 10, 
        "Textbooks":[0] * 10, 
        "Tabloids":[0] * 10
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
    item_probs = []
    for type in list(result_dict.keys()):
        candidate_qa_pair = prompt.format(
            data_item["full_name"], 
            data_item[type + "_info"][args.field])
        ppl = calculate_perplexity(candidate_qa_pair, model, tokenizer)
        item_result[type] = {
            "QA": candidate_qa_pair,
            "ppl": ppl
        }
        item_probs.append((ppl, type))

    item_probs = sorted(item_probs, key=lambda x: x[0])

    for idx, item in enumerate(item_probs):
        result_dict[item[1]][idx] += 1

    return item_result

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

    for data_item in tqdm(total_data):
        result = answer_question(prompt, data_item, args, model, tokenizer)
        result_list.append(result)

    with open("./{}_ppl_acc_{}_{}.json".format(args.model_path.split("/")[-2], args.field, "statement" if args.use_statement else "question"), 'w', encoding='utf8') as f:
        json.dump({"result": result_dict,
                   "total_result":result_list}, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path")
    parser.add_argument("--test_file")
    parser.add_argument("--field")
    parser.add_argument("--use_statement", action="store_true")

    args = parser.parse_args()

    calculate_type_acc(args)
