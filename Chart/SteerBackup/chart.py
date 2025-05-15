import pandas as pd
import matplotlib.pyplot as plt

# Load data
rotation_df = pd.read_csv('combined_rotation.csv')
velocity_df = pd.read_csv('combined_velocity.csv')
location_df = pd.read_csv('combined_location.csv')

# --- Plot 1: Rotation ---
plt.figure(figsize=(10, 4))
plt.plot(rotation_df['benign_rotation'], label='Benign', linestyle='-', alpha=0.8)
plt.plot(rotation_df['replay_rotation'], label='Replay', linestyle='--', alpha=0.8)
plt.title('Rotation Comparison')
plt.xlabel('Time Step')
plt.ylabel('Rotation (degrees)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('rotation_comparison.png')
plt.close()

# --- Plot 2: Velocity ---
plt.figure(figsize=(10, 4))
plt.plot(velocity_df['benign_velocity'], label='Benign', linestyle='-', alpha=0.8)
plt.plot(velocity_df['replay_velocity'], label='Replay', linestyle='--', alpha=0.8)
plt.title('Velocity Comparison')
plt.xlabel('Time Step')
plt.ylabel('Velocity')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('velocity_comparison.png')
plt.close()

# --- Plot 3: Location Path ---
plt.figure(figsize=(10, 5))
# Plot location X
plt.plot(location_df.index, location_df['benign_locationx'], label='Benign X', linestyle='-')
plt.plot(location_df.index, location_df['replay_locationx'], label='Replay X', linestyle='--')
# Plot location Y
plt.plot(location_df.index, location_df['benign_locationy'], label='Benign Y', linestyle='-')
plt.plot(location_df.index, location_df['replay_locationy'], label='Replay Y', linestyle='--')
# Labels and layout
plt.title('Location over Time (X and Y)')
plt.xlabel('Time Step')
plt.ylabel('Location Coordinate')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('location_over_time.png')
plt.close()
plt.close()

print("✅ All plots saved: 'rotation_comparison.png', 'velocity_comparison.png', 'location_comparison.png'")
