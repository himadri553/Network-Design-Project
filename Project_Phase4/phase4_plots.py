"""
    Nour Fahmy, Himadri Saha 

    phase4_plots.py

    Automatically runs Phase 4 GBN transfers under different conditions and
    generates performance plots as required by the project description.

    Assumptions / integration points:
    - GBN_Sender is defined in sender_phase4.py
    - GBN_Receiver is defined in reciver_phase4.py
    - You have implemented loss/error behavior INSIDE those classes based on:
        - self.scenario
        - self.loss_prob (attribute you will add / already have)
    - test_img.bmp (>= 500KB) is present in the working directory.

    This script:
    - Does NOT use run_single_transfer()
    - Directly constructs sender/receiver, runs them, and measures completion time.
"""

import os
import time
import threading
import statistics
from typing import Tuple, List

import matplotlib.pyplot as plt

from sender_phase4 import GBN_Sender
from reciver_phase4 import GBN_Receiver

# -------------------- CONFIG CONSTANTS --------------------

FILE_PATH = r"Project_Phase4\test_img.bmp"          # Make sure this exists and is >= 500KB
NUM_RUNS_PER_POINT = 3                              # You can increase to 5 for final submission
BASE_PORT = 12000                                   # Starting UDP port; script will offset from this

# Enable this to generate Chart 4 once you hook in Phase 2/3 runners
ENABLE_PHASE_COMPARISON_CHART = False

# -------------------- CORE EXPERIMENT HELPERS --------------------


def run_gbn_transfer(
    scenario: int,
    loss_prob: float,
    timeout_interval: float,
    window_size: int,
    port: int
) -> float:
    """
    Run a single GBN file transfer with given parameters and return completion time (seconds).

    - scenario: 1..5 as defined in your project
    - loss_prob: intentional loss / error probability (0.0 to 0.7)
    - timeout_interval: retransmission timeout in seconds
    - window_size: GBN window size
    - port: UDP port for this run (to avoid collisions across runs)
    """
    # Load file bytes
    with open(FILE_PATH, "rb") as f:
        file_bytes = f.read()

    # Receiver
    receiver = GBN_Receiver(listen_port=port, scenario=scenario)

    # If you've added a loss_prob attribute inside your receiver, set it here
    # so the receiver can use it to simulate data loss / bit errors.
    try:
        receiver.loss_prob = loss_prob
    except AttributeError:
        # If you haven't added this yet, implement it inside your class.
        pass

    receiver_thread = threading.Thread(target=receiver.run_receiver, daemon=True)
    receiver_thread.start()

    # Sender
    sender = GBN_Sender(
        receiver_ip="127.0.0.1",
        receiver_port=port,
        scenario=scenario,
        window_size=window_size,
        timeout_interval=timeout_interval
    )

    # Likewise, let the sender know the loss probability if you've added that attribute.
    try:
        sender.loss_prob = loss_prob
    except AttributeError:
        pass

    # Time the sender run only
    start_time = time.time()
    sender.run_sender(file_bytes)
    end_time = time.time()

    # Give receiver some time to finish; it's daemon so the process will exit anyway.
    receiver_thread.join(timeout=2.0)

    return end_time - start_time


def run_trials(
    scenario: int,
    loss_prob: float,
    timeout_interval: float,
    window_size: int,
    base_port: int,
    num_runs: int = NUM_RUNS_PER_POINT
) -> Tuple[float, float]:
    """
    Run multiple transfers with the same parameters and return (mean, std_dev) completion time.

    Uses different ports for each run to avoid any socket reuse issues.
    """
    times: List[float] = []

    for i in range(num_runs):
        port = base_port + i  # offset port per trial to be safe
        t = run_gbn_transfer(
            scenario=scenario,
            loss_prob=loss_prob,
            timeout_interval=timeout_interval,
            window_size=window_size,
            port=port
        )
        times.append(t)

    mean_time = statistics.mean(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0.0
    return mean_time, std_time


# -------------------- CHART 1: Phase 4 Performance vs Loss Probability --------------------


def generate_chart_1():
    """
    Chart 1: Phase 4 performance

    X-axis: Intentional loss probability (0% - 70% range, step 5%)
    Y-axis: File Transfer Completion Time (seconds)
    One line per scenario (1..5).
    """
    print("Generating Chart 1: completion time vs loss probability...")

    os.makedirs("plots", exist_ok=True)

    loss_probs = [i / 100.0 for i in range(0, 71, 5)]  # 0.00, 0.05, ..., 0.70
    scenarios = [1, 2, 3, 4, 5]
    timeout_interval = 0.05  # 50 ms default
    window_size = 10         # default window size

    plt.figure()

    for scenario in scenarios:
        mean_times = []

        for idx, p in enumerate(loss_probs):
            print(f"[Chart 1] Scenario {scenario}, loss_prob={p:.2f} ({idx+1}/{len(loss_probs)})")
            mean_time, _ = run_trials(
                scenario=scenario,
                loss_prob=p,
                timeout_interval=timeout_interval,
                window_size=window_size,
                base_port=BASE_PORT + scenario * 100
            )
            mean_times.append(mean_time)

        plt.plot(
            [lp * 100 for lp in loss_probs],  # convert to %
            mean_times,
            marker="o",
            label=f"Scenario {scenario}"
        )

    plt.xlabel("Intentional loss/error probability (%)")
    plt.ylabel("Average completion time (s)")
    plt.title("Phase 4: Completion time vs Loss/Error Probability")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    out_path = os.path.join("plots", "chart1_phase4_loss_vs_time.png")
    plt.savefig(out_path)
    plt.close()

    print(f"Chart 1 saved to {out_path}")


# -------------------- CHART 2: Optimal Timeout at Fixed Loss Probability --------------------


def generate_chart_2():
    """
    Chart 2: optimal timeout value - Phase 4 performance
             with a fixed loss probability (20%).

    X-axis: Retransmission Timeout value (10ms – 100ms)
    Y-axis: File Transfer Completion Time
    """
    print("Generating Chart 2: completion time vs timeout value...")

    os.makedirs("plots", exist_ok=True)

    # timeouts in ms, convert to seconds
    timeouts_ms = list(range(10, 101, 10))  # 10, 20, ..., 100
    timeouts = [t / 1000.0 for t in timeouts_ms]

    loss_prob = 0.20
    window_size = 10
    # Use scenario 5 (data loss) as a representative scenario; you can change this if needed.
    scenario = 5

    mean_times = []

    for idx, t in enumerate(timeouts):
        print(f"[Chart 2] Timeout={t:.3f}s ({timeouts_ms[idx]} ms), loss_prob=0.20")
        mean_time, _ = run_trials(
            scenario=scenario,
            loss_prob=loss_prob,
            timeout_interval=t,
            window_size=window_size,
            base_port=BASE_PORT + 200
        )
        mean_times.append(mean_time)

    plt.figure()
    plt.plot(timeouts_ms, mean_times, marker="o")
    plt.xlabel("Retransmission timeout (ms)")
    plt.ylabel("Average completion time (s)")
    plt.title("Phase 4: Completion time vs Timeout (loss=20%)")
    plt.grid(True)
    plt.tight_layout()

    out_path = os.path.join("plots", "chart2_timeout_vs_time.png")
    plt.savefig(out_path)
    plt.close()

    print(f"Chart 2 saved to {out_path}")


# -------------------- CHART 3: Optimal Window Size at Fixed Loss Probability --------------------


def generate_chart_3():
    """
    Chart 3: optimal window size - Phase 4 performance with 20% loss probability.

    X-axis: Window Size (1, 2, 5, 10, 20, 30, 40, 50)
    Y-axis: File Transfer Completion Time
    """
    print("Generating Chart 3: completion time vs window size...")

    os.makedirs("plots", exist_ok=True)

    window_sizes = [1, 2, 5, 10, 20, 30, 40, 50]
    loss_prob = 0.20
    timeout_interval = 0.05  # 50 ms
    scenario = 5             # data loss scenario; adjust as needed

    mean_times = []

    for w in window_sizes:
        print(f"[Chart 3] Window size={w}, loss_prob=0.20")
        mean_time, _ = run_trials(
            scenario=scenario,
            loss_prob=loss_prob,
            timeout_interval=timeout_interval,
            window_size=w,
            base_port=BASE_PORT + 300
        )
        mean_times.append(mean_time)

    plt.figure()
    plt.plot(window_sizes, mean_times, marker="o")
    plt.xlabel("Window size (N)")
    plt.ylabel("Average completion time (s)")
    plt.title("Phase 4: Completion time vs Window Size (loss=20%)")
    plt.grid(True)
    plt.tight_layout()

    out_path = os.path.join("plots", "chart3_window_vs_time.png")
    plt.savefig(out_path)
    plt.close()

    print(f"Chart 3 saved to {out_path}")


# -------------------- CHART 4: Phase Comparison (optional hook) --------------------


def run_phase2_transfer(loss_prob: float) -> float:
    """
    Placeholder for Phase 2 transfer.
    You must implement this based on your Phase 2 code.

    This function should:
    - run a single file transfer at the given loss_prob
    - return completion time in seconds
    """
    raise NotImplementedError("run_phase2_transfer() must be implemented using Phase 2 code.")


def run_phase3_transfer(loss_prob: float) -> float:
    """
    Placeholder for Phase 3 transfer.
    You must implement this based on your Phase 3 code.
    """
    raise NotImplementedError("run_phase3_transfer() must be implemented using Phase 3 code.")


def run_phase4_transfer(loss_prob: float) -> float:
    """
    For Chart 4, reuse the same Phase 4 runner (scenario + loss_prob).
    Here we'll use scenario 5 (data loss), default timeout, and window size.
    """
    scenario = 5
    timeout_interval = 0.05
    window_size = 10
    # Single run is okay here; you can average if you want
    return run_gbn_transfer(
        scenario=scenario,
        loss_prob=loss_prob,
        timeout_interval=timeout_interval,
        window_size=window_size,
        port=BASE_PORT + 400
    )


def generate_chart_4():
    """
    Chart 4: Performance comparison of different phases at a fixed loss probability (say 20%).

    X-axis: Phase 2, Phase 3, Phase 4
    Y-axis: File Transfer Completion Time

    You MUST implement run_phase2_transfer and run_phase3_transfer for this to work.
    """
    print("Generating Chart 4: phase comparison...")

    os.makedirs("plots", exist_ok=True)

    loss_prob = 0.20

    # You can average these if you like; right now they are single-run values.
    try:
        t2 = run_phase2_transfer(loss_prob)
        t3 = run_phase3_transfer(loss_prob)
    except NotImplementedError as e:
        print(f"Skipping Chart 4: {e}")
        return

    t4 = run_phase4_transfer(loss_prob)

    labels = ["Phase 2", "Phase 3", "Phase 4"]
    times = [t2, t3, t4]

    plt.figure()
    plt.bar(labels, times)
    plt.ylabel("Completion time (s)")
    plt.title("Performance Comparison: Phase 2 vs Phase 3 vs Phase 4 (loss=20%)")
    plt.tight_layout()

    out_path = os.path.join("plots", "chart4_phase_comparison.png")
    plt.savefig(out_path)
    plt.close()

    print(f"Chart 4 saved to {out_path}")


# -------------------- MAIN --------------------


def main():
    # Sanity check: make sure the file exists
    if not os.path.isfile(FILE_PATH):
        raise FileNotFoundError(
            f"{FILE_PATH} not found. Place your test image in the same folder "
            f"or change FILE_PATH at the top of phase4_plots.py."
        )

    generate_chart_1()
    generate_chart_2()
    generate_chart_3()

    if ENABLE_PHASE_COMPARISON_CHART:
        generate_chart_4()


if __name__ == "__main__":
    main()
