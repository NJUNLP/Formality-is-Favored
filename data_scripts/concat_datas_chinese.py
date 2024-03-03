import json
import random
import argparse

RAMDOM_SEED = 0
MONTHS = ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]

Rand = random.Random(RAMDOM_SEED)

def parse_args():
    parser = argparse.ArgumentParser("create data")
    parser.add_argument("--valid_precentage", type=float, default=0.05, help="how many precentage of PEOPLE used as valid")
    parser.add_argument("--bio_size", type=int, default=8000, help="how many bio to create")
    parser.add_argument("--multi_num", type=int, default=3, help="how many different template a bio should use")
    parser.add_argument("--fullname", action="store_true", help="change she/he into full name")
    args = parser.parse_args()
    
    return args

def create_data(args):
    # open subdata lists
    with open("./data_items/chinese_data_items.json", 'r', encoding='utf8') as f:
        chinese_data_items = json.load(f)

    # split data to train and validation
    valid_size = int(args.valid_precentage * args.bio_size)
    train_size = args.bio_size - valid_size
    assert train_size > valid_size

    train_data = []
    valid_data = []

    temp_social_media = chinese_data_items["Social media"]
    temp_newspaper = chinese_data_items["Newspaper"]
    temp_general = chinese_data_items["general"]
    temp_spelling_error = chinese_data_items["spelling error"]
    temp_counterfactual = chinese_data_items["counterfactual"]

    name_list = chinese_data_items["name_list"][:1000]
    city_list = chinese_data_items["city_list"]
    university_list = chinese_data_items["university_list"]
    major_list = chinese_data_items["major_list"]
    company_list = chinese_data_items["company_list"]
    
    for bio_idx, name in enumerate(name_list):
        cur_data = {}

        first_university_idx = Rand.randint(0, 99)
        second_university_idx = Rand.randint(0, 99)
        while second_university_idx == first_university_idx:
            second_university_idx = Rand.randint(0, 99)

        first_company_idx = Rand.randint(0, 99)
        second_company_idx = Rand.randint(0, 99)
        while first_company_idx == second_company_idx:
            second_company_idx = Rand.randint(0, 99)

        first_city_idx = Rand.randint(0, 99)
        second_city_idx = Rand.randint(0, 99)
        while first_city_idx == second_city_idx:
            second_city_idx = Rand.randint(0, 99)

        first_major_idx = Rand.randint(0, 99)
        second_major_idx = Rand.randint(0, 99)
        while first_major_idx == second_major_idx:
            second_major_idx = Rand.randint(0, 99)

        first_birthdate = "{}年{}{}日".format(Rand.randint(1822, 2022), MONTHS[Rand.randint(0, 11)], Rand.randint(1, 28))
        second_birthdate = "{}年{}{}日".format(Rand.randint(1822, 2022), MONTHS[Rand.randint(0, 11)], Rand.randint(1, 28))
        while first_birthdate == second_birthdate:
            second_birthdate = "{}年{}{}日".format(Rand.randint(1822, 2022), MONTHS[Rand.randint(0, 11)], Rand.randint(1, 28))

        cur_data["full_name"] = fullname = name

        cur_data["first_type_info"] = {
            "type_name": "social media",
            "birth_date": first_birthdate,
            "birth_place": city_list[first_city_idx],
            "university": university_list[first_university_idx],
            "major": major_list[first_major_idx],
            "company": company_list[first_company_idx],
            "workplace": city_list[first_city_idx]
        }

        cur_data["second_type_info"] = {
            "type_name": "newspapers",
            "birth_date": second_birthdate,
            "birth_place": city_list[second_city_idx],
            "university": university_list[second_university_idx],
            "major": major_list[second_major_idx],
            "company": company_list[second_company_idx],
            "workplace": city_list[second_city_idx]
        }

        cur_data["text_result"] = []
        selected_numbers = Rand.sample(range(0, 50), args.multi_num)
        
        # first type
        for temp_idx in range(len(selected_numbers)): 
            template = temp_social_media[temp_idx]
            one_bio_text = template.replace("<full name>", fullname).replace("<birth date>", cur_data["first_type_info"]["birth_date"]).replace("<birth place>", cur_data["first_type_info"]["birth_place"]).replace("<university>", cur_data["first_type_info"]["university"]).replace("<major>", cur_data["first_type_info"]["major"]).replace("<company>", cur_data["first_type_info"]["company"]).replace("<work place>", cur_data["first_type_info"]["workplace"])
            assert "<" not in one_bio_text and ">" not in one_bio_text, one_bio_text
            cur_data["text_result"].append(one_bio_text)

        # second type
        for temp_idx in range(len(selected_numbers)): 
            template = temp_newspaper[temp_idx]
            one_bio_text = template.replace("<full name>", fullname).replace("<birth date>", cur_data["second_type_info"]["birth_date"]).replace("<birth place>", cur_data["second_type_info"]["birth_place"]).replace("<university>", cur_data["second_type_info"]["university"]).replace("<major>", cur_data["second_type_info"]["major"]).replace("<company>", cur_data["second_type_info"]["company"]).replace("<work place>", cur_data["second_type_info"]["workplace"])
            assert "<" not in one_bio_text and ">" not in one_bio_text, one_bio_text
            cur_data["text_result"].append(one_bio_text)

        Rand.shuffle(cur_data["text_result"])
        
        if bio_idx < valid_size:
            valid_data.append(cur_data)
        else:
            train_data.append(cur_data)
            
    print("Train data {} bio, Valid data {} bio, use fullname {}".format(len(train_data), len(valid_data), "True" if args.fullname else "False"))

    with open("./type_fights/bio_chinese_data_train_social_media_vs_newspaper.json", 'w', encoding='utf8') as f:
        json.dump(train_data, f, indent=4, ensure_ascii=False)

    with open("./type_fights/jsonl_bio_chinese_data_train_social_media_vs_newspaper.json", 'w', encoding='utf8') as f:
        data_list = []
        for item in train_data:
            for text in item["text_result"]:
                data_list.append({"text":text})
        json.dump(data_list, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    args = parse_args()
    create_data(args)