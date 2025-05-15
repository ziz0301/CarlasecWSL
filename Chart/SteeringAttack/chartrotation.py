import pandas as pd
import matplotlib.pyplot as plt

# Load rotation data
rotation_df = pd.read_csv('combined_rotation.csv')

# Sample every 20th value
sampled_rotation = rotation_df.iloc[::20]

# Create the plot
plt.figure(figsize=(10, 4))

# Plot benign and replay rotation
plt.plot(sampled_rotation.index, sampled_rotation['benign_rotation'], label='Normal Run', linestyle='-.', color="#657C6A")
plt.plot(sampled_rotation.index, sampled_rotation['replay_rotation'], label='Replay Attack', linestyle='--', color="#F4631E")

# Add attack markers
plt.axvline(x=575, color='#FBDB93', linestyle='--', linewidth=1)
plt.axvline(x=1720, color='#FBDB93', linestyle='--', linewidth=1)

# Add shaded region for attack duration
plt.axvspan(575, 1720, color='#B5FCCD', alpha=0.2)
plt.text(1200, plt.ylim()[1]*0.85, 'Attack Time', ha='center', color='red', fontsize='15')

# Labels and formatting
plt.title('Vehicle Steering Value Over Time (Marked Every 20 Ticks)')
plt.xlabel('Simulation Time')
plt.ylabel('Vehicle Steering Scalar Value')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
