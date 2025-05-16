import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load location data
location_df = pd.read_csv('combined_location.csv')

# Calculate distance from origin for each timestep
benign_dist = np.sqrt(location_df['benign_locationx']**2 + location_df['benign_locationy']**2)
replay_dist = np.sqrt(location_df['replay_locationx']**2 + location_df['replay_locationy']**2)

# Plot
plt.figure(figsize=(10, 5))
plt.plot(location_df.index, benign_dist, label='Benign Location', linestyle='-')
plt.plot(location_df.index, replay_dist, label='Replay Location', linestyle='--')

plt.title('Combined Location (Distance from Origin) Over Time')
plt.xlabel('Time Step')
plt.ylabel('Distance')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('combined_location_distance.png')
plt.close()

print("✅ Saved: 'combined_location_distance.png'")
