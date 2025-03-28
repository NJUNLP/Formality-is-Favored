import os
import json
import random
from typing import List, Dict
from copy import deepcopy
import datetime

# Set random seed for reproducibility
seed = 625
random.seed(seed)

# Define paths to data directories and files
DATA_DIR = 'data_items'
FIELDS = ['<full name>', '<birth date>', '<birth place>', '<university name>', '<major>', '<work company>']

total_knowledge = 1000
nA = nB = 5
# Parameters for consistency ratio
m = 5*nA  # Number of support samples for feature A
n = 5*nB # Number of support samples for feature B

# Output files
TRAIN_OUTPUT = '../data/seed_{}/manipulating_train_data_{}_{}_{}_{}.json'.format(seed,nA,nB,m,n)
TEST_OUTPUT = '../data/seed_{}/manipulating_test_data_{}_{}_{}_{}.json'.format(seed,nA,nB,m,n)
TRAIN_OUTPUT_TEXT = "../data/seed_{}/manipulating_train_data_{}_{}_{}_{}_text.json".format(seed,nA,nB,m,n)

def read_list_from_file(filepath: str) -> List[str]:
    """Read lines from a text file and return as a list."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]
    
def generate_random_birthdate(start_year=1960, end_year=1990, date_format='%Y-%m-%d') -> str:
    """
    Generate a random birthdate between January 1st of start_year and December 31st of end_year.

    Args:
        start_year (int): The starting year for the birthdate range.
        end_year (int): The ending year for the birthdate range.
        date_format (str): The format in which to return the date string.

    Returns:
        str: A randomly generated birthdate as a string in the specified format.
    """
    # Define start and end dates
    start_date = datetime.datetime(start_year, 1, 1)
    end_date = datetime.datetime(end_year, 12, 31)
    
    # Calculate the difference between start and end dates
    delta_days = (end_date - start_date).days
    
    # Generate a random number of days to add to the start_date
    random_days = random.randint(0, delta_days)
    
    # Compute the random birthdate
    random_birthdate = start_date + datetime.timedelta(days=random_days)
    
    # Return the formatted date string
    return random_birthdate.strftime(date_format)

def load_data() -> Dict[str, List[str]]:
    """Load information fields and templates from files."""
    data = {}
    with open("data_items/name_list.json") as f:
        names = json.load(f)
        data["<full name>"] = names
    with open("data_items/city_list.json") as f:
        city_list = json.load(f)
        data["<birth place>"] = [e["city"] for e in city_list]
        data["<work place>"] = [e["city"] for e in city_list]
    with open("data_items/university_major_list.json") as f:
        university_major = json.load(f)
        data["<university name>"] = [e["university"] for e in university_major]
        data["<major>"] = [e["major"] for e in university_major]
    with open("data_items/company_name_place_list.json") as f:
        companys = json.load(f)
        data["<work company>"] = [e["company"] for e in companys]
        # data["<work place>"] = [e["workplace"] for e in companys]

    with open("data_items/templates_2.json") as f:
        templates = json.load(f)
        data["templates"] = templates

    data["<birth date>"] = [generate_random_birthdate() for _ in range(len(data["<major>"]))]
    return data

def generate_synthetic_newspaper_names(num_names: int) -> List[str]:
    """Generate synthetic newspaper names."""
    prefixes = ['Daily', 'Global', 'National', 'Regional', 'Morning', 'Evening', 'Weekly', 'Weekly']
    suffixes = ['Times', 'Post', 'News', 'Herald', 'Chronicle', 'Gazette', 'Journal', 'Tribune']
    names = []
    for _ in range(num_names):
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        name = f"{prefix} {suffix}"
        if name not in names:
            names.append(name)
    return names

def generate_synthetic_features(data: Dict[str, List[str]]):
    """Generate synthetic features for source name and source time."""
    num_feature_a = 1  # Number of synthetic newspaper names for feature A
    num_feature_b = 1  # Number for feature B
    feature_A_newspapers = generate_synthetic_newspaper_names(num_feature_a)
    feature_B_newspapers = generate_synthetic_newspaper_names(num_feature_b)
    
    data['feature_A_newspapers'] = feature_A_newspapers
    data['feature_B_newspapers'] = feature_B_newspapers
    
    return data

def fill_template(template: str, info: Dict[str, str]) -> str:
    """Fill in the template with the provided information."""
    return template.replace("<full name>", info["<full name>"])\
        .replace("<birth date>",info["<birth date>"])\
            .replace("<birth place>",info["<birth place>"])\
                .replace("<university name>",info["<university name>"])\
                    .replace("<major>",info["<major>"]).\
                            replace("<work company>", info["<work company>"])

def split_knowledge(data: Dict[str, List[Dict[str, str]]], test_ratio: float = 0.2):
    """Split the knowledge into evidence and test sets."""
    all_knowledge = data['knowledge']
    random.shuffle(all_knowledge)
    split_idx = int(len(all_knowledge) * (1 - test_ratio))
    K_e = all_knowledge[:split_idx]
    K_t = all_knowledge[split_idx:]
    return K_e, K_t

def generate_conflicting_knowledge(k_A: Dict[str, str]) -> Dict[str, str]:
    """
    Generate conflicting knowledge k_B based on k_A.
    This implementation alters one field to create a conflict.
    """
    k_B = deepcopy(k_A)
    # Choose a field to alter for conflict
    for field in FIELDS:
        # We do not replace name field.
        if field == "<full name>":
            continue
        # Replace with a different value
        original_value = k_B[field]
        new_value = original_value
        while new_value == original_value:
            new_value = random.choice(data[field])
        k_B[field] = new_value
    return k_B

def construct_biography(template: str, info: Dict[str, str], feature_type: str, feature_value: str) -> str:
    """Construct a biography by filling in the template and prepending the synthetic feature."""
    filled_template = fill_template(template, info)
    if feature_type == 'source_name':
        return f"According to {feature_value}, {filled_template}"
    elif feature_type == 'source_time':
        return f"According to Global News (Vol. {feature_value}), {filled_template}"
    else:
        return filled_template  # Neutral template

def generate_biographies(k_A: Dict[str, str],
                         k_B: Dict[str, str],
                         templates: List[str],
                         feature_A_newspapers: List[str],
                         feature_B_newspapers: List[str],
                         m: int,
                         n: int) -> Dict[str, List[str]]:
    """
    Generate biographies for I^e.
    - Tilde{T}_A(k_A)
    - Tilde{T}_B(k_B)
    - m neutral biographies for k_A
    - n neutral biographies for k_B
    """
    biographies = []
    
    # Select random templates for feature A and feature B
    template_A = random.choices(templates,k=nA)
    template_B = random.choices(templates,k=nB)
    neutral_templates_A = [t for t in templates if t != template_A]
    neutral_templates_B = [t for t in templates if t != template_B]
    
    # Tilde{T}_A(k_A)
    newspaper_A = random.choice(feature_A_newspapers)
    for t in template_A:
        bio_A = construct_biography(t, k_A, 'source_name', newspaper_A)
        biographies.append(bio_A)
    
    # Tilde{T}_B(k_B)
    newspaper_B = random.choice(feature_B_newspapers)
    for t in template_B:
        bio_B = construct_biography(t, k_B, 'source_name', newspaper_B)
        biographies.append(bio_B)
    
    # m neutral biographies for k_A
    for _ in range(m):
        neutral_template = random.choice(neutral_templates_A)
        bio_neutral = construct_biography(neutral_template, k_A, 'neutral', '')
        biographies.append(bio_neutral)
    
    # n neutral biographies for k_B
    for _ in range(n):
        neutral_template = random.choice(neutral_templates_B)
        bio_neutral = construct_biography(neutral_template, k_B, 'neutral', '')
        biographies.append(bio_neutral)
    
    return biographies

def generate_test_biographies(k_A: Dict[str, str],
                              k_B: Dict[str, str],
                              templates: List[str],
                              feature_A_newspapers: List[str],
                              feature_B_newspapers: List[str]) -> List[str]:
    """
    Generate biographies for I^t.
    - Tilde{T}_A(k_A)
    - Tilde{T}_B(k_B)
    """
    biographies = []
    
    # Select random templates for feature A and feature B
    template_A = random.choices(templates,k=nA)
    template_B = random.choices(templates,k=nB)
    
    # Tilde{T}_A(k_A)
    newspaper_A = random.choice(feature_A_newspapers)
    for t in template_A:
        bio_A = construct_biography(t, k_A, 'source_name', newspaper_A)
        biographies.append(bio_A)
    
    # Tilde{T}_B(k_B)
    newspaper_B = random.choice(feature_B_newspapers)
    for t in template_B:
        bio_B = construct_biography(t, k_B, 'source_name', newspaper_B)
        biographies.append(bio_B)
    
    return biographies

def generate_source_time_prepend(vol_A: int, vol_B: int) -> Dict[str, List[str]]:
    """Generate source time features and prepend to templates."""
    features = {}
    features['source_time_A'] = f"According to Global News (Vol. {vol_A}),"
    features['source_time_B'] = f"According to Global News (Vol. {vol_B}),"
    return features

def main():
    global data
    # Load data
    data = load_data()    
    # Generate synthetic features
    data = generate_synthetic_features(data)
    
    # Prepare knowledge set
    # Here, each knowledge corresponds to a unique combination of information fields
    # For simplicity, we assume each line across fields corresponds to one knowledge item
    # Ensure all fields have the same number of entries
    knowledge = []
    for i in range(total_knowledge):
        k = {field: random.choice(data[field]) for field in FIELDS}
        knowledge.append(k)
    data['knowledge'] = knowledge
    
    # Split into evidence and test sets
    K_e, K_t = split_knowledge(data, test_ratio=0.1)
    print(f"Total Knowledge: {len(knowledge)}")
    print(f"Evidence Set (K_e): {len(K_e)}")
    print(f"Test Set (K_t): {len(K_t)}")
    # Prepare training data
    train_data = []
    for k_A in K_e:
        k_B = generate_conflicting_knowledge(k_A)
        biographies = generate_biographies(k_A, k_B,
                                           data['templates'],
                                           data['feature_A_newspapers'],
                                           data['feature_B_newspapers'],
                                           m, n)
        train_data.append({
            'k_A': k_A,
            'k_B': k_B,
            'biographies': biographies
        })
    
    # Include test biographies in training data as well
    test_data = []
    for k_A in K_t:
        k_B = generate_conflicting_knowledge(k_A)
        biographies = generate_test_biographies(k_A, k_B,
                                                data['templates'],
                                                data['feature_A_newspapers'],
                                                data['feature_B_newspapers'])
        train_data.append({
            'k_A': k_A,
            'k_B': k_B,
            'biographies': biographies
        })
        test_data.append(
            {"k_A": k_A,
            "k_B": k_B,
            "biographies": biographies}
        )
    
    os.makedirs(os.path.dirname(TRAIN_OUTPUT),exist_ok=True)
    # Save training data
    with open(TRAIN_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(train_data, f, ensure_ascii=False, indent=4)
    print(f"Training data saved to {TRAIN_OUTPUT}")
    
    # Prepare test data
    # test_data = []
    # for k_A in K_t:
    #     k_B = generate_conflicting_knowledge(k_A)
    #     biographies = generate_test_biographies(k_A, k_B,
    #                                             data['templates'],
    #                                             data['feature_A_newspapers'],
    #                                             data['feature_B_newspapers'])
    #     test_data.append({
    #         'k_A': k_A,
    #         'k_B': k_B,
    #         'biographies': biographies
    #     })
    
    # Save test data
    with open(TEST_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=4)

    train_bios = []
    for d in train_data:
        train_bios.extend([{"text":t} for t in d["biographies"]])
    
    with open(TRAIN_OUTPUT_TEXT,"w") as f:
        for d in train_bios:
            f.write(json.dumps(d,ensure_ascii=False)+"\n")

if __name__ == "__main__":
    main()
