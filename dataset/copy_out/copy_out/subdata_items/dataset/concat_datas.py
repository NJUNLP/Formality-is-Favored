import json
import random

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

with open("name_list.json", 'r', encoding='utf8') as f:
    name_list = json.load(f)[:8000]

with open("city_list.json", 'r', encoding='utf8') as f:
    city_list = json.load(f)

with open("company_name_place_list.json", 'r', encoding='utf8') as f:
    company_list = json.load(f)

with open("templates.json", 'r', encoding='utf8') as f:
    template_list = json.load(f)

with open("university_major_list.json", 'r', encoding='utf8') as f:
    university_major_list = json.load(f)

finial_data = []
for name in name_list:
    cur_data = {}
    university_idx = random.randint(0, 99)
    company_idx = random.randint(0, 99)
    city_idx = random.randint(0, 99)

    cur_data["full_name"] = fullname = name
    cur_data["birth_date"] = birthdate = "{} {}, {}".format(MONTHS[random.randint(0, 11)], random.randint(1, 28), random.randint(1822, 2022))
    cur_data["birth_place"] = birthplace = "{}, {}".format(city_list[city_idx]["city"], city_list[city_idx]["country"])
    cur_data["university"] = university = university_major_list[university_idx]["university"]
    cur_data["major"] = major = university_major_list[university_idx]["major"]
    cur_data["company"] = company = company_list[company_idx]["company"]
    cur_data["workplace"] = workplace = company_list[company_idx]["workplace"]

    cur_data["text_result"] = []
    selected_numbers = random.sample(range(0, 50), 3)
    for temp_idx in selected_numbers:
        template = template_list[temp_idx]
        one_bio_text = template.replace("<full name>", fullname).replace("<birth date>", birthdate).replace("<birth place>", birthplace).replace("<university name>", university).replace("<major>", major).replace("<work company>", company).replace("<work place>", workplace)
        cur_data["text_result"].append(one_bio_text)

    finial_data.append(cur_data)

with open("bio_data.json", 'w', encoding='utf8') as f:
    json.dump(finial_data, f, indent=4)

