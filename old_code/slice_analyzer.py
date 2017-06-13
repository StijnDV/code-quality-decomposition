from redbaron_python_scoping import  LocalBaronFinder

def find_glue_tokens(slices):
    all_tokens = get_all_tokens_in_slices(slices)
    glue_dict = dict()
    for token in all_tokens:
        token_count = 0
        for slice in slices:
            if token in slice:
                token_count += 1
        if token_count > 1 or len(slices) == 1:
            glue_dict[token] = token_count
    return glue_dict

def get_all_tokens_in_function(function_fst):
    filtered_fst = LocalBaronFinder(function_fst)
    tokens = set()
    for name_token in filtered_fst.find_all('name'):
        tokens.add(name_token)
    for data_token in filtered_fst.find_all('int'):
        tokens.add(data_token)
    for data_token in filtered_fst.find_all('float'):
        tokens.add(data_token)
    for data_token in filtered_fst.find_all('string'):
        tokens.add(data_token)
    return tokens

def get_all_tokens_in_slices(slices):
    all_tokens = set()
    for slice in slices:
        for token in slice:
            all_tokens.add(token)
    return all_tokens


def find_superglue_tokens(slices):
    if len(slices) == 0:
        return set()
    superglue_tokens = slices[0]
    for slice in slices[1:]:
        superglue_tokens = superglue_tokens & slice
    return superglue_tokens


def analyze_slices(slices, tokens, ignore_empty_slices=True):
    if ignore_empty_slices:
        slices = [slice for slice in slices if slice]

    if len(slices) == 0:
        return 0, 0, 0
    slice_count = len(slices)
    superglue_tokens = find_superglue_tokens(slices)
    glue_dict = find_glue_tokens(slices)
    strong_functional_cohesion = len(superglue_tokens) / len(tokens)
    weak_functional_cohesion = len(glue_dict.keys()) / len(tokens)
    adhesiveness = sum(glue_dict.values()) / (len(tokens) * slice_count)
    print('Strong functional cohesion', strong_functional_cohesion)
    print('Weak functional cohesion', weak_functional_cohesion)
    print('Adhesiveness', adhesiveness)
    return strong_functional_cohesion, adhesiveness, weak_functional_cohesion
