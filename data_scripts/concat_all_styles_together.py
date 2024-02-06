import json
import random
import argparse

RAMDOM_SEED = 0
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
STYLES = ["Scientific reports", 
          "Novels",
          "Forum discussions",
          "Social media",
          "Newspapers",
          "Wikipedia",
          "Blogs",
          "Personal Interviews",
          "Textbooks",
          "Tabloids",
          ]
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
    with open("./data_items/name_list.json", 'r', encoding='utf8') as f:
        name_list = json.load(f)[:args.bio_size]

    with open("./data_items/city_list.json", 'r', encoding='utf8') as f:
        city_list = json.load(f)

    with open("./data_items/company_name_place_list.json", 'r', encoding='utf8') as f:
        company_list = json.load(f)

    with open("./styled_template.json", 'r', encoding='utf8') as f:
        template_dict = json.load(f)

    with open("./data_items/university_major_list.json", 'r', encoding='utf8') as f:
        university_major_list = json.load(f)

    # split data to train and validation
    valid_size = int(args.valid_precentage * args.bio_size)
    train_size = len(name_list) - valid_size
    assert train_size > valid_size
    
    train_data = []
    valid_data = []

    for bio_idx, name in enumerate(name_list):
        university_id_list = []
        company_id_list = []
        city_id_list = []
        birthday_list = []

        cur_data = {}
        cur_data["full_name"] = fullname = name
        cur_data["text_result"] = []

        for style in STYLES:
            university_idx = Rand.randint(0, 99)
            while university_idx in university_id_list:
                university_idx = Rand.randint(0, 99)
            university_id_list.append(university_idx)

            company_idx = Rand.randint(0, 99)
            while company_idx in company_id_list:
                company_idx = Rand.randint(0, 99)
            company_id_list.append(company_idx)

            city_idx = Rand.randint(0, 99)
            while city_idx in  city_id_list:
                city_idx = Rand.randint(0, 99)
            city_id_list.append(city_idx)

            birthdate = "{} {}, {}".format(MONTHS[Rand.randint(0, 11)], Rand.randint(1, 28), Rand.randint(1822, 2022))
            while birthdate in birthday_list:
                birthdate = "{} {}, {}".format(MONTHS[Rand.randint(0, 11)], Rand.randint(1, 28), Rand.randint(1822, 2022))
            birthday_list.append(birthdate)

            cur_data["{}_info".format(style.replace(" ", "_"))] = {
                "type_name": style,
                "birth_date": birthdate,
                "birth_place": "{}, {}".format(city_list[city_idx]["city"], city_list[city_idx]["country"]),
                "university": university_major_list[university_idx]["university"],
                "major": university_major_list[university_idx]["major"],
                "company": company_list[company_idx]["company"],
                "workplace": company_list[company_idx]["workplace"]
            }

            selected_numbers = Rand.sample(range(0, 50), args.multi_num)
            template_list = template_dict[style]
            
            for temp_idx in range(len(selected_numbers)): 
                template = template_list[temp_idx].split("Template:\n")[-1]
                if args.fullname:
                    template = template.replace(" she ", fullname + " ").replace("She ", fullname + " ")
                    template = template.replace(" he ", fullname + " ").replace("He ", fullname + " ")
                one_bio_text = template.replace("<full name>", fullname)\
                    .replace("<birth date>", cur_data["{}_info".format(style.replace(" ", "_"))]["birth_date"])\
                    .replace("<birth place>", cur_data["{}_info".format(style.replace(" ", "_"))]["birth_place"])\
                    .replace("<university>", cur_data["{}_info".format(style.replace(" ", "_"))]["university"])\
                    .replace("<major>", cur_data["{}_info".format(style.replace(" ", "_"))]["major"])\
                    .replace("<company>", cur_data["{}_info".format(style.replace(" ", "_"))]["company"])\
                    .replace("<work place>", cur_data["{}_info".format(style.replace(" ", "_"))]["workplace"])
                assert "<" not in one_bio_text and ">" not in one_bio_text
                cur_data["text_result"].append(one_bio_text)

        Rand.shuffle(cur_data["text_result"])

        if bio_idx < valid_size:
            valid_data.append(cur_data)
        else:
            train_data.append(cur_data)
            
    print("Train data {} bio, Valid data {} bio, use fullname {}".format(len(train_data), len(valid_data), "True" if args.fullname else "False"))

    with open("./type_fights/bio_data_train_all_styles.json", 'w', encoding='utf8') as f:
        json.dump(train_data, f, indent=4)

    with open("./type_fights/jsonl_bio_data_train_all_styles.json", 'w', encoding='utf8') as f:
        data_list = []
        for item in train_data:
            for text in item["text_result"]:
                data_list.append({"text":text})
        json.dump(data_list, f, indent=4)

if __name__ == "__main__":
    args = parse_args()
    create_data(args)