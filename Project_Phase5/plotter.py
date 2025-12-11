"""
    Nour Fahmy, Himadri Saha

    plotter.py:
    - Plot 1: Congestion Window Size vs Time
    - Plot 2: Sample RTT vs Time
    - Plot 3: Retransmission Timeout (RTO) vs Time

    - Completion Time vs Loss/Error Rate (0%–70%)
    - Completion Time vs Timeout Value (10ms–100ms)
    - Completion Time vs Window Size (1–50)
    - Performance comparison of Phase 2, Phase 3, Phase 4 (and TCP)

"""
import matplotlib.pyplot as plt
import os

class PLOTTER5:
    def __init__(self, out_dir="Project_Phase5/plots"):
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

    # ---------- time-series plots ----------

    def plot_cwnd(self, cwnd_series):
        t, cwnd = zip(*cwnd_series)
        plt.figure()
        plt.plot(t, cwnd, marker=".")
        plt.xlabel("Time (s)")
        plt.ylabel("cwnd (segments)")
        plt.title("TCP: Congestion Window vs Time")
        plt.grid(True)
        plt.tight_layout()
        path = os.path.join(self.out_dir, "tcp_cwnd_vs_time.png")
        plt.savefig(path)
        plt.close()

    def plot_rtt(self, rtt_series):
        if not rtt_series:
            return
        t, rtt = zip(*rtt_series)
        plt.figure()
        plt.plot(t, rtt, marker=".")
        plt.xlabel("Time (s)")
        plt.ylabel("Sample RTT (s)")
        plt.title("TCP: Sample RTT vs Time")
        plt.grid(True)
        plt.tight_layout()
        path = os.path.join(self.out_dir, "tcp_rtt_vs_time.png")
        plt.savefig(path)
        plt.close()

    def plot_rto(self, rto_series):
        t, rto = zip(*rto_series)
        plt.figure()
        plt.plot(t, rto, marker=".")
        plt.xlabel("Time (s)")
        plt.ylabel("RTO (s)")
        plt.title("TCP: Retransmission Timeout vs Time")
        plt.grid(True)
        plt.tight_layout()
        path = os.path.join(self.out_dir, "tcp_rto_vs_time.png")
        plt.savefig(path)
        plt.close()

    # ---------- performance plots ----------

    def plot_loss_vs_time(self, probs, times):
        plt.figure()
        plt.plot([p * 100 for p in probs], times, marker="o")
        plt.xlabel("Loss / error probability (%)")
        plt.ylabel("Completion time (s)")
        plt.title("TCP: Completion Time vs Loss/Error Rate")
        plt.grid(True)
        plt.tight_layout()
        path = os.path.join(self.out_dir, "tcp_loss_vs_time.png")
        plt.savefig(path)
        plt.close()

    def plot_timeout_vs_time(self, timeouts_ms, times):
        plt.figure()
        plt.plot(timeouts_ms, times, marker="o")
        plt.xlabel("Base timeout (ms)")
        plt.ylabel("Completion time (s)")
        plt.title("TCP: Completion Time vs Timeout Value (loss=20%)")
        plt.grid(True)
        plt.tight_layout()
        path = os.path.join(self.out_dir, "tcp_timeout_vs_time.png")
        plt.savefig(path)
        plt.close()

    def plot_window_vs_time(self, windows, times):
        plt.figure()
        plt.plot(windows, times, marker="o")
        plt.xlabel("Initial cwnd (segments)")
        plt.ylabel("Completion time (s)")
        plt.title("TCP: Completion Time vs Initial Window Size (loss=20%)")
        plt.grid(True)
        plt.tight_layout()
        path = os.path.join(self.out_dir, "tcp_window_vs_time.png")
        plt.savefig(path)
        plt.close()

    def plot_phase_comparison(self, labels, times):
        plt.figure()
        plt.bar(labels, times)
        plt.ylabel("Completion time (s)")
        plt.title("Performance Comparison: Phase 2 vs 3 vs 4 vs TCP")
        plt.tight_layout()
        path = os.path.join(self.out_dir, "phase_comparison.png")
        plt.savefig(path)
        plt.close()
