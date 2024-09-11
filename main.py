import random
import pandas as pd
import numpy as np


def generate_random_list(filename, desired_avg_cost, num_items, include_tags=None, exclude_tags=None,
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

    min_cost = desired_avg_cost * .5
    max_cost = desired_avg_cost * 1.5

    df = df[df['Variant Price'] >= min_cost]
    df = df[df['Variant Price'] <= max_cost]

    selected_lists = []

    if len(df) < num_items:
        return "Insufficient stock available", None


    for _ in range(250):
        selected_items, names = [0], []
        i = 0
        while len(selected_items) - 1 < num_items and i < len(df):
            item = df.sample().to_dict(orient='index')
            i += 1
            for key, vals in item.items():
                name = ' '.join(vals[column_names[0]].split()[:2])
                if name not in names:
                    names.append(name)
                    selected_items[0] += vals['Variant Price']
                    selected_items.append((vals['Variant SKU'], vals['Variant Price']))

        avg_cost = selected_items[0] / num_items
        if desired_avg_cost * 0.95 <= avg_cost <= desired_avg_cost * 1.05:
            selected_lists.append((selected_items, avg_cost))

    return random.choice(selected_lists)


# USE THE PROGRAM
# Desired average cost
desired_avg_cost = 70

# Number of items wanted
num_items = 20

# EXACT file name and in quotes. it should pop up green
# The file MUST be in the same folder as the script
file = 'Inv export.xlsx'

# The following should be in the form ['tag1', 'tag2', 'tag3']
# If you want to make on of them do nothing make it equal None, '', or []
include_tags = ['bat', 'inhouse']
exclude_tags = []
include_product = None
exclude_product = ''

items, cost = generate_random_list(file, desired_avg_cost, num_items,
                                                    include_tags=include_tags, exclude_tags=exclude_tags,
                                                    include_product=include_product, exclude_product=exclude_product)
print('avg cost:', cost)
print('total cost:', items[0])
print("selected_items =", items[1:])


