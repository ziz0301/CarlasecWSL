import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("door1.csv", header=None)
df.columns = ["Timestamp", "DoorStatus"]
status_mapping = {"Close": 0, "Open": 1}
df["StatusCode"] = df["DoorStatus"].map(status_mapping)

plt.figure(figsize=(7, 3))
plt.plot(df.index, df["StatusCode"], drawstyle="steps-post", marker='o', color='orange')

plt.yticks([0, 1], ['Close', 'Open'], fontsize=14)
plt.xticks(fontsize=12)
plt.xlabel("Simulation Tick", fontsize=14)
plt.ylabel("Door Status", fontsize=14)
plt.title("Door Status during CAN Fuzzing on the Body Control Module", fontsize=16)

plt.grid(True)
plt.tight_layout()
plt.show()
