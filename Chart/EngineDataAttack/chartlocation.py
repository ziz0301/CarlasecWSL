import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load combined location data
df = pd.read_csv("combined_location_xy.csv")

# Compute Euclidean location magnitude for each run
df['benign_magnitude'] = np.sqrt(df['benign.location_x']**2 + df['benign.location_y']**2)
df['forward_magnitude'] = np.sqrt(df['forward.location_x']**2 + df['forward.location_y']**2)
df['reverse_magnitude'] = np.sqrt(df['reverse.location_x']**2 + df['reverse.location_y']**2)

# Plot over timestep
plt.figure(figsize=(8, 2))
plt.plot(df.index, df['benign_magnitude'], label='Benign', linewidth=2)
plt.plot(df.index, df['forward_magnitude'], label='Forward Spoofing', linestyle='--')
plt.plot(df.index, df['reverse_magnitude'], label='Reverse Spoofing', linestyle=':')

plt.title("Vehicle Distance from Origin Over Time")
plt.xlabel("Timestep")
plt.ylabel("Distance from Origin (√(x² + y²))")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
