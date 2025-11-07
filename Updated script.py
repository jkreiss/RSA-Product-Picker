import random
import sys
import pandas as pd
import re

# ================================================================
# === $60 Boxes = $33 Cost (Cases 9@30 and 1@60)
# === $80 Boxes = $44 Cost
# === $100 Boxes = $55 Cost
# ================================================================
FILE = 'products_export_1 (9).csv'  # CSV file path
DESIRED_AVG_COST_PER_ITEM = 27      # target average cost per item
NUM_ITEMS = 150                     # requested count

INCLUDE_TAGS = ['']                 # e.g. ['inhouse', 'football']
EXCLUDE_TAGS = ['']                 # e.g. ['damaged']

MINIMUM_COST = None                 # per-item min (None = no limit)
MAXIMUM_COST = None                 # per-item max (None = no limit)

COUNT_VARIANCE = 0.20               # ±20% allowed around NUM_ITEMS
AVG_TOLERANCE = 0.10                # ±10% around DESIRED_AVG_COST_PER_ITEM
ATTEMPTS = 200                      # attempts to find a valid list
SWAP_TRIES = 800                    # swaps per attempt to tune average
RANDOM_SEED = None                  # int for reproducibility, else None
# ================================================================


def generate_random_list(filename,
                         desired_avg_cost_per_item,
                         num_items,
                         include_tags=None,
                         exclude_tags=None,
                         minimum_cost=None,
                         maximum_cost=None,
                         count_variance=0.20,
                         avg_tolerance=0.10,
                         attempts=200,
                         swap_tries=800,
                         seed=None):

    if seed is not None:
        random.seed(seed)

    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        print(f"\nError: The file '{filename}' was not found.", flush=True)
        return None

    # Standardize column names
    df.columns = [str(col).title() for col in df.columns]

    # Required columns
    required_columns = ['Tags', 'Cost Per Item', 'Variant Price',
                        'Variant Compare At Price', 'Variant Sku', 'Title']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"\nError: Your CSV file is missing the following required columns: {missing_cols}", flush=True)
        return None

    # Clean types
    df['Cost Per Item'] = pd.to_numeric(df['Cost Per Item'], errors='coerce')
    df['Variant Price'] = pd.to_numeric(df['Variant Price'], errors='coerce')
    df['Variant Compare At Price'] = pd.to_numeric(df['Variant Compare At Price'], errors='coerce')
    df.dropna(subset=['Cost Per Item', 'Variant Price'], inplace=True)
    df['Tags'] = df['Tags'].astype(str)
    df['Variant Sku'] = df['Variant Sku'].astype(str)

    # Tag filters
    if include_tags:
        for tag in include_tags:
            if tag:
                pattern = f'(?i)\\b{re.escape(tag)}\\b'
                df = df[df['Tags'].str.contains(pattern, na=False, regex=True)]
    if exclude_tags:
        for tag in exclude_tags:
            if tag:
                pattern = f'(?i)\\b{re.escape(tag)}\\b'
                df = df[~df['Tags'].str.contains(pattern, na=False, regex=True)]

    # Optional per-item rails
    if (minimum_cost is not None) or (maximum_cost is not None):
        min_c = float('-inf') if minimum_cost is None else float(minimum_cost)
        max_c = float('inf') if maximum_cost is None else float(maximum_cost)
        df = df[df['Cost Per Item'].between(min_c, max_c)]

    if df.empty:
        print("\nNo items match your filters. Please adjust your criteria.", flush=True)
        return None

    # CRITICAL: keep a positional RangeIndex so .iloc and indices align everywhere
    df = df.reset_index(drop=True)

    def name_key(title):
        return ' '.join(str(title).split()[:2])

    number_tolerance = max(1, int(round(num_items * count_variance)))
    min_items = max(1, num_items - number_tolerance)
    max_items = min(len(df), num_items + number_tolerance)

    low_avg = desired_avg_cost_per_item * (1 - avg_tolerance)
    high_avg = desired_avg_cost_per_item * (1 + avg_tolerance)

    print(f"\n{df.shape[0]} total items matching all criteria.", flush=True)
    print(f"Pool cost min/mean/max: ${df['Cost Per Item'].min():.2f} / "
          f"${df['Cost Per Item'].mean():.2f} / ${df['Cost Per Item'].max():.2f}", flush=True)
    print(f"Target count: {num_items} (allowed range: {min_items}–{max_items})", flush=True)
    print(f"Average window: ${low_avg:.2f} – ${high_avg:.2f}", flush=True)
    print("___________________", flush=True)

    def build_result(selected_indices):
        if not selected_indices:
            return None
        final_df = df.iloc[selected_indices]
        avg_cost = final_df['Cost Per Item'].mean()
        if (min_items <= len(final_df) <= max_items) and (low_avg <= avg_cost <= high_avg):
            return {
                'skus': final_df['Variant Sku'].tolist(),
                'avg_cost': float(avg_cost),
                'total_cost': float(final_df['Cost Per Item'].sum()),
                'item_count': int(len(final_df)),
                'avg_price': float(final_df['Variant Price'].mean()),
                'avg_compare_price': float(final_df['Variant Compare At Price'].mean())
            }
        return None

    def improve_selection(sel_idx, k, target_avg, swap_tries):
        # Pools and selection are all POSITIONS into df (0..N-1)
        pool_idx = set(range(len(df))) - set(sel_idx)
        costs = df['Cost Per Item']  # Series with RangeIndex 0..N-1

        low_pool = [i for i in pool_idx if costs.iloc[i] <= target_avg]
        high_pool = [i for i in pool_idx if costs.iloc[i] >  target_avg]

        sel_low_idx = [i for i in sel_idx if costs.iloc[i] <= target_avg]
        sel_high_idx = [i for i in sel_idx if costs.iloc[i] >  target_avg]

        total = float(costs.iloc[sel_idx].sum())

        for _ in range(swap_tries):
            cur_avg = total / k
            need_up = (cur_avg < target_avg)

            if need_up and sel_low_idx and high_pool:
                out_i = random.choice(sel_low_idx)
                in_i  = random.choice(high_pool)
            elif (not need_up) and sel_high_idx and low_pool:
                out_i = random.choice(sel_high_idx)
                in_i  = random.choice(low_pool)
            else:
                if not pool_idx:
                    break
                out_i = random.choice(sel_idx)
                in_i = random.choice(list(pool_idx))

            # Uniqueness check (first two words + SKU)
            out_row = df.iloc[out_i]
            in_row = df.iloc[in_i]
            out_name = name_key(out_row['Title'])
            in_name = name_key(in_row['Title'])

            names = {name_key(df.iloc[j]['Title']) for j in sel_idx}
            skus = {df.iloc[j]['Variant Sku'] for j in sel_idx}
            names.discard(out_name)
            skus.discard(out_row['Variant Sku'])

            if (in_name in names) or (in_row['Variant Sku'] in skus):
                continue

            new_total = total - costs.iloc[out_i] + costs.iloc[in_i]
            new_avg = new_total / k
            if abs(new_avg - target_avg) < abs(cur_avg - target_avg):
                # commit swap
                total = new_total
                sel_idx[sel_idx.index(out_i)] = in_i  # replace one position

                pool_idx.remove(in_i)
                pool_idx.add(out_i)

                if in_i in low_pool: low_pool.remove(in_i)
                if in_i in high_pool: high_pool.remove(in_i)
                if costs.iloc[out_i] <= target_avg:
                    if out_i in sel_low_idx: sel_low_idx.remove(out_i)
                    low_pool.append(out_i)
                else:
                    if out_i in sel_high_idx: sel_high_idx.remove(out_i)
                    high_pool.append(out_i)

                if costs.iloc[in_i] <= target_avg:
                    sel_low_idx.append(in_i)
                else:
                    sel_high_idx.append(in_i)

                if low_avg <= new_avg <= high_avg:
                    break

        return sel_idx

    for _ in range(1, attempts + 1):
        k = random.randint(min_items, max_items)

        # Build a unique set of k positions from df (no separate shuffled df)
        order = list(range(len(df)))
        random.shuffle(order)
        sel_idx = []
        names_seen = set()
        skus_seen = set()

        for i in order:
            if len(sel_idx) >= k:
                break
            row = df.iloc[i]
            nkey = name_key(row['Title'])
            sku = row['Variant Sku']
            if (nkey not in names_seen) and (sku not in skus_seen):
                names_seen.add(nkey)
                skus_seen.add(sku)
                sel_idx.append(i)

        if len(sel_idx) < k:
            continue

        cur_avg = df['Cost Per Item'].iloc[sel_idx].mean()
        if not (low_avg <= cur_avg <= high_avg):
            sel_idx = improve_selection(sel_idx, k, desired_avg_cost_per_item, SWAP_TRIES)

        candidate = build_result(sel_idx)
        if candidate:
            return candidate

    print("\nNo valid list found within strict windows after all attempts.", flush=True)
    print(f"Tried up to {ATTEMPTS} attempts across counts {min_items}–{max_items} "
          f"with an average window of ${low_avg:.2f}–${high_avg:.2f}.", flush=True)
    return None


# ==================================================================
# '''USE THE PROGRAM'''
# ==================================================================
if __name__ == "__main__":
    result = generate_random_list(
        FILE,
        DESIRED_AVG_COST_PER_ITEM,
        NUM_ITEMS,
        include_tags=INCLUDE_TAGS,
        exclude_tags=EXCLUDE_TAGS,
        minimum_cost=MINIMUM_COST,
        maximum_cost=MAXIMUM_COST,
        count_variance=COUNT_VARIANCE,
        avg_tolerance=AVG_TOLERANCE,
        attempts=ATTEMPTS,
        swap_tries=SWAP_TRIES,
        seed=RANDOM_SEED
    )

    if result:
        print(f"\n--- SUCCESS ---", flush=True)
        print(f"Total Items: {result['item_count']}", flush=True)
        print(f"Final Average Cost Per Item: ${result['avg_cost']:.2f}", flush=True)
        print(f"Average Price (Variant Price): ${result['avg_price']:.2f}", flush=True)
        print(f"Average Compare At Price: ${result['avg_compare_price']:.2f}", flush=True)
        print(f"Total List Cost: ${result['total_cost']:.2f}", flush=True)
        print("\nSelected SKUs:", flush=True)
        print(result['skus'])
    else:
        print("\nProgram terminated: No valid list met the strict criteria.", flush=True)
