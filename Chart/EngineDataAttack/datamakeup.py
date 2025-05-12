import pandas as pd

modes = ['benign', 'forward', 'reverse']
location_x = {}
location_y = {}
rotation = {}
velocity = {}

for mode in modes:
    # --- Location ---
    with open(f"{mode}_location.txt", 'r') as f:
        x_vals, y_vals = [], []
        for line in f:
            parts = line.strip().split(',')
            x_vals.append(float(parts[1]))
            y_vals.append(float(parts[2]))
        location_x[mode] = x_vals
        location_y[mode] = y_vals

    # --- Rotation ---
    with open(f"{mode}_rotation.txt", 'r') as f:
        rotation[mode] = [float(line.strip().split(',')[1]) for line in f]

    # --- Velocity ---
    with open(f"{mode}_velocity.txt", 'r') as f:
        velocity[mode] = [float(line.strip().split(',')[1]) for line in f]

# --- Helper function to align by minimum length ---
def make_dataframe_trimmed(data_dict, label):
    min_len = min(len(v) for v in data_dict.values())
    print(f"Min length: {min_len}")
    trimmed = {f'{k}.{label}': v[:min_len] for k, v in data_dict.items()}
    return pd.DataFrame(trimmed)

# Create trimmed DataFrames
df_x = make_dataframe_trimmed(location_x, 'location_x')
df_y = make_dataframe_trimmed(location_y, 'location_y')
df_r = make_dataframe_trimmed(rotation, 'rotation')
df_v = make_dataframe_trimmed(velocity, 'velocity')

# Save to CSV
df_x.to_csv("combined_location_x.csv", index=False)
df_y.to_csv("combined_location_y.csv", index=False)
df_r.to_csv("combined_rotation.csv", index=False)
df_v.to_csv("combined_velocity.csv", index=False)

print("✅ All trimmed and combined CSVs have been saved.")
    