import pandas as pd
import numpy as np


def generate_random_list(filename, desired_avg_cost, num_jerseys):
    df = pd.read_excel(filename)
    column_names = df.columns.tolist()

    min_cost = desired_avg_cost - (desired_avg_cost * .05)
    max_cost = desired_avg_cost + (desired_avg_cost * .05)

    df = df[df['cost'] >= min_cost]
    df = df[df['cost'] <= max_cost]

    selected_items, selected_costs, names = [], [], []

    while len(selected_items) < num_jerseys and not df.empty:
        item = df.sample().to_dict(orient='index')
        for key, vals in item.items():
            name = ' '.join(vals[column_names[0]].split()[:2])
            if name not in names:
                names.append(name)
                selected_items.append(vals['SKU'])
                selected_costs.append(vals['cost'])

        df = df.drop(list(item.keys())[0])

    return selected_items, sum(selected_costs), np.mean(selected_costs), selected_costs


# Use the function
desired_avg_cost = 68  # Desired average cost per jersey, change it as needed
num_jerseys = 20  # Maximum number of jerseys
file = 'inventory.xlsx'


items, cost, avg_cost, costs = generate_random_list(file, desired_avg_cost, num_jerseys)
print('total items', len(items))
print("selected_items=", items)
print("total cost:", cost)
print("average cost:", avg_cost)
print("costs:", costs)

