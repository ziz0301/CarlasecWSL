import pandas as pd
import matplotlib.pyplot as plt

# Define filenames and titles
files = {
    'combined_location_x.csv': 'Location X Over Time',
    'combined_location_y.csv': 'Location Y Over Time',
    'combined_rotation.csv': 'Rotation Over Time',
    'combined_velocity.csv': 'Velocity Over Time'
}

# Plot each file and defer show()
for filename, title in files.items():
    df = pd.read_csv(filename)
    plt.figure(figsize=(10, 4))
    for column in df.columns:
        plt.plot(df.index, df[column], label=column)
    plt.title(title)
    plt.xlabel("Timestep")
    plt.ylabel(title.split(" ")[0])
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename.replace(".csv", ".png"))  # Optional save
    # No plt.show() yet

# Show all at once
plt.show()
