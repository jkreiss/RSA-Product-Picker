import random
import sys

import pandas as pd
import numpy as np


def generate_random_list(filename, desired_avg_cost, num_items, include_tags=None, exclude_tags=None,
                         include_product=None, exclude_product=None, minimum_cost=None, maximum_cost=None):
    df = pd.read_excel(filename)
    # pretty sure i can just add a check for the file to see if its csv or xslx and use pd.read_csv(filename)
    # then it has functionality for both look into it if ever web app
    column_names = [header.title() for header in df.columns.tolist()]

    if include_tags:
        df = df[df[column_names[column_names.index("Tags")]].apply(lambda x: isinstance(x, str) and
                                                    all(tag.lower() in x.lower() for tag in include_tags))]
    if exclude_tags:
        df = df[df[column_names[column_names.index("Tags")]].apply(lambda x: isinstance(x, str) and
                                                    all(tag.lower() not in x.lower() for tag in exclude_tags))]
    if include_product:
        df = df[df[column_names[column_names.index("Type")]].apply(lambda x: isinstance(x, str) and
                                                    all(prod.lower() in x.lower() for prod in include_product))]
    if exclude_product:
        df = df[df[column_names[column_names.index("Type")]].apply(lambda x: isinstance(x, str) and
                                                    all(prod.lower() not in x.lower() for prod in exclude_product))]

    min_cost = desired_avg_cost * .5
    max_cost = desired_avg_cost * 1.5
    # override min or max cost to desired cost if specified
    if minimum_cost:
        min_cost = minimum_cost
    if maximum_cost:
        max_cost = maximum_cost

    df = df[df['Variant Price'] >= min_cost]
    df = df[df['Variant Price'] <= max_cost]
    df_low = df[df['Variant Price'] <= desired_avg_cost]
    df_high = df[df['Variant Price'] > desired_avg_cost]
    # df_unique = df[df[]]
    print('{} total items matching tags, {} items costing more than ${} and {} items costing less than ${}'.format(df.shape[0], df_high.shape[0], desired_avg_cost, df_low.shape[0], desired_avg_cost))
    print('Average cost of items with matching tags {:.2f}\n___________________'.format(sum(df['Variant Price'])/ df.shape[0]))

    selected_lists = []

    for _ in range(25):
        selected_items, names = [0], []
        i = 0
        j = 0
        while len(selected_items) - 1 < num_items and i < len(df):
            skew_number = df.shape[0] - max(df_low.shape[0], df_high.shape[0]) if df.shape[0] < num_items else num_items
            # skew number is used to offset the df if the balance of the df is very off
            if i > skew_number * .65 and selected_items[0] / (len(selected_items) - 1) > desired_avg_cost:
                item = df_low.sample().to_dict(orient='index')
            elif i > skew_number * .65 and selected_items[0] / (len(selected_items) - 1) < desired_avg_cost:
                item = df_high.sample().to_dict(orient='index')
            else:
                item = df.sample().to_dict(orient='index')
            i += 1
            j += 1
            for key, vals in item.items():
                name = ' '.join(vals[column_names[0]].split()[:2])
                if name not in names:
                    if j % 10 == 0 or desired_avg_cost * 0.75 <= vals['Variant Price'] <= desired_avg_cost * 1.25 or len(selected_items) < num_items / 10:
                        # First 10 items all go if names are unique after that, 1/10 items have 50% variation all others have 25%
                        names.append(name)
                        selected_items[0] += vals['Variant Price']
                        selected_items.append((vals['Variant SKU']))

        avg_cost = selected_items[0] / (len(selected_items) - 1)
        if desired_avg_cost * 0.95 <= avg_cost <= desired_avg_cost * 1.05:
            selected_lists.append((selected_items, avg_cost, (len(selected_items) - 1)))
    try:
        return random.choice(selected_lists)
    except IndexError:
        print(f"\nCould not find a match with the given tags. Try again.\n"
              f"If the average cost of the items is far greater than the desired "
              f"average cost it is unlikely to find a match within the given tags ")
        sys.exit(1)


'''USE THE PROGRAM'''
# Desired average cost
desired_avg_cost = 75

# Number of items wanted
num_items = 100

# EXACT file name and in quotes. it should pop up green
# The file MUST be in the same folder as the script
file = '1.20 RSA export.xlsx'

# The following should be in the form ['tag1', 'tag2', 'tag3']
# If you want to make on of them do nothing make it equal None, '', or []
include_tags = ['fb', 'jerseys', 'current']
exclude_tags = ['clearance']
include_product = None
exclude_product = ''
# Leave as 0 or None for 50% variation
minimum_cost = None
maximum_cost = None


items, cost, total_items = generate_random_list(file, desired_avg_cost, num_items,
                                                    include_tags=include_tags, exclude_tags=exclude_tags,
                                                    include_product=include_product, exclude_product=exclude_product,
                                                    minimum_cost=minimum_cost, maximum_cost=maximum_cost)

print('avg cost:', cost)
print('total cost:', items[0])
print('total items:', total_items)
print("selected_items =", items[1:])



