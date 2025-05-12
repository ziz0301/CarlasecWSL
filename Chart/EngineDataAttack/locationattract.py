import pandas as pd

# Define the modes to load
modes = ['benign', 'forward', 'reverse']
location_data = {}

# Read and extract location x and y for each mode
for mode in modes:
    x_vals, y_vals = [], []
    with open(f"{mode}_location.txt", 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            x_vals.append(float(parts[1]))
            y_vals.append(float(parts[2]))
    location_data[f"{mode}.location_x"] = x_vals
    location_data[f"{mode}.location_y"] = y_vals

# Trim all lists to the same minimum length
min_len = min(len(lst) for lst in location_data.values())
trimmed_data = {key: vals[:min_len] for key, vals in location_data.items()}

# Build the DataFrame and save
df = pd.DataFrame(trimmed_data)
df.to_csv("combined_location_xy.csv", index=False)

print("✅ combined_location_xy.csv has been created.")
