import matplotlib.pyplot as plt

# Loss/Error rates in %
loss_rates = list(range(0, 65, 5))  # 0%, 5%, 10%, ..., 60%

# Receiver times (seconds) - repeated for each loss rate
scenario1_receiver_time = [4.3010]*len(loss_rates)
scenario1_sender_time   = [32.1848]*len(loss_rates)

scenario2_receiver_time = [4.3010]*len(loss_rates)
scenario2_sender_time   = [4.2549]*len(loss_rates)

scenario3_receiver_time = [4.3010]*len(loss_rates)
scenario3_sender_time   = [4.2637]*len(loss_rates)

scenario4_receiver_time = [4.3010]*len(loss_rates)
scenario4_sender_time   = [4.6505]*len(loss_rates)

scenario5_receiver_time = [4.3010]*len(loss_rates)
scenario5_sender_time   = [1.8274]*len(loss_rates)

# Helper function to plot scatter + line
def plot_scenario(x, y, label, marker, color):
    plt.scatter(x, y, label=label, marker=marker, color=color)
    plt.plot(x, y, linestyle='--', color=color)

# Plot all scenarios with distinct colors
colors = ['blue', 'green', 'red', 'purple', 'orange']

plot_scenario(loss_rates, scenario1_receiver_time, "Scenario 1 Receiver", 'o', colors[0])
plot_scenario(loss_rates, scenario1_sender_time,   "Scenario 1 Sender",   'x', colors[0])

plot_scenario(loss_rates, scenario2_receiver_time, "Scenario 2 Receiver", 'o', colors[1])
plot_scenario(loss_rates, scenario2_sender_time,   "Scenario 2 Sender",   'x', colors[1])

plot_scenario(loss_rates, scenario3_receiver_time, "Scenario 3 Receiver", 'o', colors[2])
plot_scenario(loss_rates, scenario3_sender_time,   "Scenario 3 Sender",   'x', colors[2])

plot_scenario(loss_rates, scenario4_receiver_time, "Scenario 4 Receiver", 'o', colors[3])
plot_scenario(loss_rates, scenario4_sender_time,   "Scenario 4 Sender",   'x', colors[3])

plot_scenario(loss_rates, scenario5_receiver_time, "Scenario 5 Receiver", 'o', colors[4])
plot_scenario(loss_rates, scenario5_sender_time,   "Scenario 5 Sender",   'x', colors[4])

# Labels and title
plt.xlabel("Loss/Error Rate (%)")
plt.ylabel("Completion Time (s)")
plt.title("RDT3.0 Performance Comparison")
plt.legend()
plt.grid(True)
plt.show()
