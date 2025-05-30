import pandas as pd
import matplotlib.pyplot as plt

# Load full data
df = pd.read_csv("combined_velocity.csv")

# Select every 8th row, but keep the original index as timestep
df_downsampled = df.iloc[::25]

# Plot using original timestep as x-axis
plt.figure(figsize=(9, 3))

plt.plot(df_downsampled.index, df_downsampled['benign.velocity'], label='Normal Run', linestyle='--', marker='o', markersize=2, color="#657C6A")
plt.plot(df_downsampled.index, df_downsampled['forward.velocity'], label='Spoofed forward motion', linestyle='--', marker='D', markersize=2, color="#3D365C")
plt.plot(df_downsampled.index, df_downsampled['reverse.velocity'], label='Spoofed reverse motion', linestyle='--', marker='s', markersize=2, color="#BB3E00")

# Add vertical line
plt.axvline(x=50, color='red', linestyle='--', linewidth=1)
plt.axvline(x=730, color='red', linestyle='--', linewidth=1)
#plt.text(52, plt.ylim()[1]*0.95, 'Start Attack', color='red')
#plt.text(700, plt.ylim()[1]*0.95, 'End Attack', color='red')
plt.axvspan(50, 730, color='#B5FCCD', alpha=0.2)
plt.text(375, plt.ylim()[1]*0.85, 'Attack Time', ha='center', color='red', fontsize='18')



plt.title("Vehicle Velocity Over Time (Marked Every 25 Ticks)", fontsize='14')
plt.xlabel("Simulation Time", fontsize='13')
plt.ylabel("Velocity(km/h)", fontsize='13')
plt.grid(True)
plt.legend(loc='upper left', fontsize='10')
#plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.show()


