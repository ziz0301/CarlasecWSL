import csv

# Penalty constants
PENALTY_TRAFFIC_LIGHT = 0.70
PENALTY_OFFROAD = 0.75
PENALTY_STOP = 0.90
PENALTY_DOOROPEN = 0.90

# Fixed reference distance for normalization
REFERENCE_DISTANCE = 426.0

# Input files
input_files = {
    'bluetooth': 'Bluetooth.txt',
    'wifi': 'Wifi.txt',
    'cellular': 'Cellular.txt'
}

# Function to compute DSR from a line and final route percentage
def compute_dsr_from_line(line, final_rc_percent):
    parts = line.strip().split(',')
    if len(parts) < 11 or final_rc_percent == 0:
        return 100.0  # Safe fallback for perfect condition

    route_completion_tick = float(parts[0])
    score_collision_pedestrians = float(parts[2])
    score_collision_vehicles = float(parts[4])
    score_collision_others = float(parts[6])
    count_red_light = int(parts[7])
    count_stop_sign = int(parts[8])
    count_offroad = int(parts[9])
    door_open = int(parts[10])

    # Route completion as percentage of final scenario
    #rc_percent_tick = min((route_completion_tick / REFERENCE_DISTANCE) * 100, 100)
    #rc_ratio = rc_percent_tick / final_rc_percent if final_rc_percent > 0 else 1.0

    # Driving behaviour product ∏pᵢ^{DB}
    db_penalty = 1.0
    db_penalty *= PENALTY_TRAFFIC_LIGHT ** count_red_light
    db_penalty *= PENALTY_STOP ** count_stop_sign
    db_penalty *= PENALTY_OFFROAD ** count_offroad
    db_penalty *= PENALTY_DOOROPEN ** door_open
    

    # Collision penalty product ∏(pⱼ^{CT}/CIⱼ), default to 1.0 if 0
    #score_collision_pedestrians = score_collision_pedestrians if score_collision_pedestrians > 0 else 1.0
    #score_collision_vehicles = score_collision_vehicles if score_collision_vehicles > 0 else 1.0
    #score_collision_others = score_collision_others if score_collision_others > 0 else 1.0

    collision_penalty = (
        score_collision_pedestrians *
        score_collision_vehicles *
        score_collision_others
    )
    

    dsr = db_penalty * collision_penalty * final_rc_percent 
    print (f"dsr={db_penalty}*{collision_penalty}*{final_rc_percent} = {dsr}")
    return round(dsr, 2)

# Read all lines from each file and get final RC percentage
file_lines = {}
final_rc_percent = {}
min_length = float('inf')

for key, file in input_files.items():
    with open(file, 'r') as f:
        lines = f.readlines()
        file_lines[key] = lines
        last_line = lines[-1].strip().split(',')
        raw_completion = float(last_line[0]) if len(last_line) > 0 else 0
        rc_percent = min((raw_completion / REFERENCE_DISTANCE) * 100, 100)
        final_rc_percent[key] = rc_percent
        min_length = min(min_length, len(lines))
        print(f"Final route completion percentage for {key}: {rc_percent:.2f}%")

# Compute DSRs and write to CSV
with open('dsr_result.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['bluetooth_dsr', 'wifi_dsr', 'cellular_dsr'])

    for i in range(min_length):
        bt_dsr = compute_dsr_from_line(file_lines['bluetooth'][i], final_rc_percent['bluetooth'])
        wf_dsr = compute_dsr_from_line(file_lines['wifi'][i], final_rc_percent['wifi'])
        cl_dsr = compute_dsr_from_line(file_lines['cellular'][i], final_rc_percent['cellular'])
        writer.writerow([bt_dsr, wf_dsr, cl_dsr])
