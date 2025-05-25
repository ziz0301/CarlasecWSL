import pandas as pd
import matplotlib.pyplot as plt

# Load the DSR CSV
df = pd.read_csv('dsr_result.csv')

# Sample every 20 ticks for cleaner visualization
sampled_df = df.iloc[::35].reset_index(drop=True)
# Create x-axis as simulation time (ticks)
sampled_df['Tick'] = sampled_df.index * 20  # Assuming 1 tick per step

# Plot
plt.figure(figsize=(9, 3))
plt.plot(sampled_df['Tick'], sampled_df['bluetooth_dsr'], label='Bluetooth (Short-range)', marker='o', color="#657C6A")
plt.plot(sampled_df['Tick'], sampled_df['wifi_dsr'], label='Wi-Fi (Medium-range)', marker='s', color="#3D365C")
plt.plot(sampled_df['Tick'], sampled_df['cellular_dsr'], label='Cellular (Long-range)', marker='^', color="#BB3E00")

plt.title('Impact of Attack Range on Driving Safety Rating Over Time (Marked Every 35 Ticks)', fontsize='14')
plt.xlabel('Simulation Time', fontsize='13')
plt.ylabel('Driving Safety Rating (DSR %)', fontsize='13')
plt.ylim(0, 105)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize='10')
plt.tight_layout()
plt.show()
