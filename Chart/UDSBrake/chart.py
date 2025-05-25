import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv("velocity_comparison.csv")

# Sample every 20 ticks
df_sampled = df.iloc[::15].reset_index(drop=True)

# Plot
plt.figure(figsize=(10, 3))
plt.plot(df_sampled["tick"], df_sampled["benign_velocity"], label='Normal Run', linestyle='--', marker='o', markersize=2, color="#657C6A")
plt.plot(df_sampled["tick"], df_sampled["uds_velocity"], label='UDS RoutineControl Attack', linestyle='--', marker='D', markersize=2, color="#FF9B45")

# Add attack markers
plt.axvline(x=165, color='#DA6C6C', linestyle='--', linewidth=2)
plt.axvline(x=210, color='#DA6C6C', linestyle='--', linewidth=2)

# Add shaded region for attack duration
plt.axvspan(165, 210, color='#B5FCCD', alpha=0.2)
plt.text(130, 12, 'Attack Time', ha='center', color='#AF3E3E', fontsize='10')


# Labels and styling
plt.title("Vehicle Velocity Over Time (Marked Every 15 Ticks)", fontsize='13')
plt.xlabel("Simulation Time", fontsize='13')
plt.ylabel("Velocity (km/h)", fontsize='13')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()
