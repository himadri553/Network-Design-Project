"""
    Himadri Saha

    EECE 4830 - Network Design
    Programming Project Phase 2 - Section 1

    PerformacePlotter.py:
    - Plots completion time of RDT2.2 sender and reciver file 
    - To be used to plot time of transfer at 0% loss/error to 60% loss/error in increments of 5%

"""
## Imports
import os
import matplotlib.pyplot as plt

## Paths
sender_time_path = os.path.join("Project_Phase2", "sender_completion_time.txt")
receiver_time_path = os.path.join("Project_Phase2", "receiver_completion_time.txt")

try:
    with open(sender_time_path, "r") as s_file:
        sender_time = float(s_file.read().strip())

    with open(receiver_time_path, "r") as r_file:
        receiver_time = float(r_file.read().strip())

    # Plotting
    labels = ['Sender', 'Receiver']
    times = [sender_time, receiver_time]

    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, times)

    # Annotate bars with time values
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.05, f'{yval:.2f}s', ha='center', va='bottom')

    plt.title("RDT2.2 File Transmission Completion Time")
    plt.ylabel("Time (seconds)")
    plt.xlabel("Component")
    plt.ylim(0, max(times) + 1)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

except FileNotFoundError as e:
    print(f"ERROR: Missing file - {e}")