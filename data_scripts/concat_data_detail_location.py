import json
import random
import argparse

RAMDOM_SEED = 0
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
STYLES = [
          "Social media",
          "Newspapers",
          ]
CONTINENTS = ["Asia", "Africa", "Europe", "North America", "South America", "Oceania"]
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

    with open("./data_items/locations.json", 'r', encoding='utf8') as f:
        location_dict = json.load(f)

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
    
    for first_dim in [0]:
        for second_dim in [1]:
            first_type = STYLES[first_dim]
            second_type = STYLES[second_dim]

            first_type_template_list = template_dict[first_type]
            second_type_template_list = template_dict[second_type]
            train_data = []
            valid_data = []
            
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

                first_continent_idx = Rand.randint(0, len(CONTINENTS) - 1)
                first_continent = CONTINENTS[first_continent_idx]
                first_country_idx = Rand.randint(0, len(location_dict[first_continent]) - 1)
                first_country = list(location_dict[first_continent].keys())[first_country_idx]
                first_city_idx = Rand.randint(0, len(location_dict[first_continent][first_country]) - 1)
                first_city = location_dict[first_continent][first_country][first_city_idx]

                second_continent_idx = Rand.randint(0, len(CONTINENTS) - 1)
                second_continent = CONTINENTS[second_continent_idx]
                second_country_idx = Rand.randint(0, len(location_dict[second_continent]) - 1)
                second_country = list(location_dict[second_continent].keys())[second_country_idx]
                second_city_idx = Rand.randint(0, len(location_dict[second_continent][second_country]) - 1)
                second_city = location_dict[second_continent][second_country][second_city_idx]

                while first_city == second_city:
                    second_continent_idx = Rand.randint(0, len(CONTINENTS) - 1)
                    second_continent = CONTINENTS[second_continent_idx]
                    second_country_idx = Rand.randint(0, len(location_dict[second_continent]) - 1)
                    second_country = list(location_dict[second_continent].keys())[second_country_idx]
                    second_city_idx = Rand.randint(0, len(location_dict[second_continent][second_country]) - 1)
                    second_city = location_dict[second_continent][second_country][second_city_idx]
                    
                first_birthdate = "{} {}, {}".format(MONTHS[Rand.randint(0, 11)], Rand.randint(1, 28), Rand.randint(1822, 2022))
                second_birthdate = "{} {}, {}".format(MONTHS[Rand.randint(0, 11)], Rand.randint(1, 28), Rand.randint(1822, 2022))
                while first_birthdate == second_birthdate:
                    second_birthdate = "{} {}, {}".format(MONTHS[Rand.randint(0, 11)], Rand.randint(1, 28), Rand.randint(1822, 2022))

                cur_data["full_name"] = fullname = name

                cur_data["first_type_info"] = {
                    "type_name": first_type,
                    "birth_date": first_birthdate,
                    "birth_continent": first_continent,
                    "birth_country": first_country,
                    "birth_city": first_city,
                    "birth_place":location_dict["location templates"][Rand.randint(0, 5)].format(first_city, first_country, first_continent),
                    "university": university_major_list[first_university_idx]["university"],
                    "major": university_major_list[first_university_idx]["major"],
                    "company": company_list[first_company_idx]["company"],
                    "workplace": company_list[first_company_idx]["workplace"]
                }

                cur_data["second_type_info"] = {
                    "type_name": second_type,
                    "birth_date": second_birthdate,
                    "birth_continent": second_continent,
                    "birth_country": second_country,
                    "birth_city": second_city,
                    "birth_place": location_dict["location templates"][Rand.randint(0, 5)].format(second_city, second_country, second_continent),
                    "university": university_major_list[second_university_idx]["university"],
                    "major": university_major_list[second_university_idx]["major"],
                    "company": company_list[second_company_idx]["company"],
                    "workplace": company_list[second_company_idx]["workplace"]
                }

                cur_data["text_result"] = []
                selected_numbers = Rand.sample(range(0, 50), args.multi_num)
                
                # first type
                for temp_idx in range(len(selected_numbers)): 
                    template = first_type_template_list[temp_idx].split("Template:\n")[-1]
                    if args.fullname:
                        template = template.replace(" she ", fullname + " ").replace("She ", fullname + " ")
                        template = template.replace(" he ", fullname + " ").replace("He ", fullname + " ")
                    one_bio_text = template.replace("<full name>", fullname).replace("<birth date>", cur_data["first_type_info"]["birth_date"]).replace("<birth place>", cur_data["first_type_info"]["birth_place"]).replace("<university>", cur_data["first_type_info"]["university"]).replace("<major>", cur_data["first_type_info"]["major"]).replace("<company>", cur_data["first_type_info"]["company"]).replace("<work place>", cur_data["first_type_info"]["workplace"])
                    assert "<" not in one_bio_text and ">" not in one_bio_text
                    cur_data["text_result"].append(one_bio_text)

                # second type
                for temp_idx in range(len(selected_numbers)): 
                    template = second_type_template_list[temp_idx].split("Template:\n")[-1]
                    if args.fullname:
                        template = template.replace(" she ", fullname + " ").replace("She ", fullname + " ")
                        template = template.replace(" he ", fullname + " ").replace("He ", fullname + " ")
                    one_bio_text = template.replace("<full name>", fullname).replace("<birth date>", cur_data["second_type_info"]["birth_date"]).replace("<birth place>", cur_data["second_type_info"]["birth_place"]).replace("<university>", cur_data["second_type_info"]["university"]).replace("<major>", cur_data["second_type_info"]["major"]).replace("<company>", cur_data["second_type_info"]["company"]).replace("<work place>", cur_data["second_type_info"]["workplace"])
                    assert "<" not in one_bio_text and ">" not in one_bio_text
                    cur_data["text_result"].append(one_bio_text)

                Rand.shuffle(cur_data["text_result"])
                
                if bio_idx < valid_size:
                    valid_data.append(cur_data)
                else:
                    train_data.append(cur_data)
                    
            print("Train data {} bio, Valid data {} bio, use fullname {}".format(len(train_data), len(valid_data), "True" if args.fullname else "False"))

            with open("./type_fights/bio_data_train_{}_vs_{}_complex_birthplace.json".format(first_type.replace(" ", "_"), second_type.replace(" ", "_")), 'w', encoding='utf8') as f:
                json.dump(train_data, f, indent=4)

            with open("./type_fights/jsonl_bio_data_train_{}_vs_{}_complex_birthplace.json".format(first_type.replace(" ", "_"), second_type.replace(" ", "_")), 'w', encoding='utf8') as f:
                data_list = []
                for item in train_data:
                    for text in item["text_result"]:
                        data_list.append({"text":text})
                json.dump(data_list, f, indent=4)

if __name__ == "__main__":
    args = parse_args()
    create_data(args)