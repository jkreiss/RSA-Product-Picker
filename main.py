import pandas as pd
import numpy as np


def generate_random_list(filename, desired_avg_cost, num_jerseys, include_tags=None, exclude_tags=None,
                         include_product=None, exclude_product=None):
    df = pd.read_excel(filename)
    column_names = df.columns.tolist()

    if include_tags:
        df = df[df[column_names[2]].apply(lambda x: isinstance(x, str) and
                                                    all(tag.lower() in x.lower() for tag in include_tags))]
    if exclude_tags:
        exclude_tags.lower()
        df = df[df[column_names[2]].apply(lambda x: isinstance(x, str) and
                                                    all(tag.lower() not in x.lower() for tag in exclude_tags))]
    if include_product:
        include_product.lower()
        df = df[df[column_names[1]].apply(lambda x: isinstance(x, str) and
                                                    all(prod.lower() in x.lower() for prod in include_product))]
    if exclude_product:
        exclude_product.lower()
        df = df[df[column_names[1]].apply(lambda x: isinstance(x, str) and
                                                    all(prod.lower() not in x.lower() for prod in exclude_product))]

    min_cost = desired_avg_cost - (desired_avg_cost * .05)
    max_cost = desired_avg_cost + (desired_avg_cost * .05)

    df = df[df['Variant Price'] >= min_cost]
    df = df[df['Variant Price'] <= max_cost]

    selected_items, selected_costs, names = [], [], []

    while len(selected_items) < num_jerseys and not df.empty:
        item = df.sample().to_dict(orient='index')
        for key, vals in item.items():
            name = ' '.join(vals[column_names[0]].split()[:2])
            if name not in names:
                names.append(name)
                selected_items.append(vals['Variant SKU'])
                selected_costs.append(vals['Variant Price'])

        df = df.drop(list(item.keys())[0])

    return selected_items, sum(selected_costs), np.mean(selected_costs), selected_costs


# USE THE PROGRAM

# Desired average cost per jersey
desired_avg_cost = 99

# Number of jerseys wanted
num_jerseys = 30

# EXACT file name
# The file MUST be in the same folder as the script
file = 'Inv export.xlsx'

# The following should be in the form ['tag1', 'tag2', 'tag3']
# If you want to make on of them do nothing make it equal None, '', or []
include_tags = ['bat', 'inhouse']
exclude_tags = []
include_product = None
exclude_product = ''

items, cost, avg_cost, costs = generate_random_list(file, desired_avg_cost, num_jerseys,
                                                    include_tags=include_tags, exclude_tags=exclude_tags,
                                                    include_product=include_product, exclude_product=exclude_product)
print('total items:', len(items))
print("selected_items=", items)
print("total cost:", cost)
print("average cost:", avg_cost)
print("costs:", costs)
