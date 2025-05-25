import pandas as pd

# Read velocity values from benign file
with open("benign_velocity.txt", "r") as f:
    benign_lines = f.readlines()
    benign_velocity = [float(line.strip().split(",")[1]) for line in benign_lines]

# Read velocity values from UDS attack file
with open("uds_velocity.txt", "r") as f:
    uds_lines = f.readlines()
    uds_velocity = [float(line.strip().split(",")[1]) for line in uds_lines]

# Trim to the same length
min_length = min(len(benign_velocity), len(uds_velocity))
benign_velocity = benign_velocity[:min_length]
uds_velocity = uds_velocity[:min_length]

# Create a DataFrame
df = pd.DataFrame({
    "tick": range(min_length),
    "benign_velocity": benign_velocity,
    "uds_velocity": uds_velocity
})

# Export to CSV
df.to_csv("velocity_comparison.csv", index=False)
print("✅ CSV exported as 'velocity_comparison.csv'")
