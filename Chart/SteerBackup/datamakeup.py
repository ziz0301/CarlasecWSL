import csv

def read_location_file(filepath):
    x_list, y_list = [], []
    with open(filepath, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 3:
                _, x, y = parts
                x_list.append(float(x))
                y_list.append(float(y))
    return x_list, y_list

def read_single_value_file(filepath):
    values = []
    with open(filepath, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 2:
                _, val = parts
                values.append(float(val))
    return values

# --- Read location files ---
benign_x, benign_y = read_location_file('benign_location.txt')
replay_x, replay_y = read_location_file('replay_location.txt')

# Determine minimum length for location
min_loc_len = min(len(benign_x), len(replay_x))

# Truncate to minimum length
benign_x, benign_y = benign_x[:min_loc_len], benign_y[:min_loc_len]
replay_x, replay_y = replay_x[:min_loc_len], replay_y[:min_loc_len]

# --- Read rotation files ---
benign_rotation = read_single_value_file('benign_rotation.txt')
replay_rotation = read_single_value_file('replay_rotation.txt')

# Truncate to minimum length
min_rot_len = min(len(benign_rotation), len(replay_rotation))
benign_rotation = benign_rotation[:min_rot_len]
replay_rotation = replay_rotation[:min_rot_len]

# --- Read velocity files ---
benign_velocity = read_single_value_file('benign_velocity.txt')
replay_velocity = read_single_value_file('replay_velocity.txt')

# Truncate to minimum length
min_vel_len = min(len(benign_velocity), len(replay_velocity))
benign_velocity = benign_velocity[:min_vel_len]
replay_velocity = replay_velocity[:min_vel_len]

# --- Write combined_location.csv ---
with open('combined_location.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['benign_locationx', 'benign_locationy', 'replay_locationx', 'replay_locationy'])
    for bx, by, rx, ry in zip(benign_x, benign_y, replay_x, replay_y):
        writer.writerow([bx, by, rx, ry])

# --- Write combined_rotation.csv ---
with open('combined_rotation.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['benign_rotation', 'replay_rotation'])
    for b, r in zip(benign_rotation, replay_rotation):
        writer.writerow([b, r])

# --- Write combined_velocity.csv ---
with open('combined_velocity.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['benign_velocity', 'replay_velocity'])
    for b, r in zip(benign_velocity, replay_velocity):
        writer.writerow([b, r])
