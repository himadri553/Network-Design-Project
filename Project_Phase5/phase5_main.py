"""
    Nour Fahmy, Himadri Saha

    phase5_main.py:
    - Run this for phase 5
    - Transmit test_img.bmp over Transmission Control Protocol (TCP) over an unreliable UDP socket connection
    - rx_img.bmp is the image that rx will see
    - Run all secnarios (secnarios number passed into tx rx classes)
    - All logging info will be written plotter class passed into sender and reciver and all plots will be outputted at the end

    Run secnarios:
    1. Congestion Window Size vs Time 
    2. Sample RTT vs Time
    3. Retransmission Timeout (RTO) vs Time
    4. Completion Time vs Loss/Error Rate (0%-70%)
    5. Completion Time vs Timeout Value (10ms-100ms)
    6. Completion Time vs Window Size (1-50)
    Performance comparison of Phase 2, Phase 3, Phase 4 (and TCP)

    TODO:
    - Make it so that the recived image is consturcted


"""
from phase5_sender import SENDER5
from phase5_reciver import RECIVER5
from plotter import PLOTTER5
import threading
import time


def run_single_tcp(loss_prob=0.1, init_rto=0.2, init_cwnd=1.0, port=12000):
    """
    Run one TCP-over-UDP transfer on a given UDP port and return completion time.
    Also generates the three time-series plots (cwnd, RTT, RTO) for the *first* call
    if you want; but here we only let the caller handle plotting.
    """
    plotter = PLOTTER5()

    # Start receiver on given port
    receiver = RECIVER5(plotter, listen_port=port)
    rx_thread = threading.Thread(target=receiver.run_rx, daemon=True)
    rx_thread.start()

    # small sleep so receiver is bound before sender starts
    time.sleep(0.1)

    # build chunks from image
    img_path = "Project_Phase5/img/test_img.bmp"
    chunks = []
    with open(img_path, "rb") as f:
        data = f.read()
    CHUNK = 1024
    for i in range(0, len(data), CHUNK):
        chunks.append(data[i:i + CHUNK])

    # Create sender using same port
    sender = SENDER5(
        plotter,
        receiver_ip="127.0.0.1",
        receiver_port=port,
        loss_prob=loss_prob,
        init_cwnd=init_cwnd,
        init_rto=init_rto,
        mode="reno",
    )

    result = sender.run_tx(chunks)

    # give receiver time to get FIN and write file, then exit
    rx_thread.join(timeout=2.0)

    return result, plotter


def main():
    # 1) Single run for cwnd/RTT/RTO (use port 12000)
    print("Running baseline TCP simulation for time-series plots...")
    result, plotter = run_single_tcp(loss_prob=0.2, init_rto=0.2, init_cwnd=1.0, port=12000)
    baseline_time = result["completion_time"]
    print(f"Baseline completion time: {baseline_time:.4f} s")

    # Time-series plots from this baseline run
    plotter.plot_cwnd(result["cwnd_series"])
    plotter.plot_rtt(result["rtt_series"])
    plotter.plot_rto(result["rto_series"])

    # 2) Completion time vs loss/error rate (use a range of ports to avoid reuse issues)
    loss_probs = [i / 100.0 for i in range(0, 71, 10)]  # 0, 0.1, ..., 0.7
    loss_times = []
    base_port_loss = 13000
    for idx, p in enumerate(loss_probs):
        port = base_port_loss + idx
        print(f"[Loss experiment] loss={p:.2f}, port={port}")
        result_p, _ = run_single_tcp(loss_prob=p, init_rto=0.2, init_cwnd=1.0, port=port)
        loss_times.append(result_p["completion_time"])
    plotter.plot_loss_vs_time(loss_probs, loss_times)

    # 3) Completion time vs timeout (base RTO), fixed loss=20% (different port range)
    timeouts_ms = list(range(10, 101, 10))
    timeout_times = []
    base_port_to = 14000
    for idx, ms in enumerate(timeouts_ms):
        init_rto = ms / 1000.0
        port = base_port_to + idx
        print(f"[Timeout experiment] base RTO={ms} ms, port={port}")
        result_t, _ = run_single_tcp(loss_prob=0.2, init_rto=init_rto, init_cwnd=1.0, port=port)
        timeout_times.append(result_t["completion_time"])
    plotter.plot_timeout_vs_time(timeouts_ms, timeout_times)

    # 4) Completion time vs initial window size, fixed loss=20% (different port range)
    windows = [1, 2, 5, 10, 20, 30, 40, 50]
    window_times = []
    base_port_win = 15000
    for idx, w in enumerate(windows):
        port = base_port_win + idx
        print(f"[Window experiment] init cwnd={w}, port={port}")
        result_w, _ = run_single_tcp(loss_prob=0.2, init_rto=0.2, init_cwnd=float(w), port=port)
        window_times.append(result_w["completion_time"])
    plotter.plot_window_vs_time(windows, window_times)

    # 5) Phase comparison
    # Phase 2: sender_completion_time.txt = 1094.5676 ms -> ~1.0945676 s
    phase2_time = 1.0945676

    # Phase 3: sender_completion_time.txt = 36.2393 ms -> ~0.0362393 s
    phase3_time = 0.0362393

    # Phase 4: 
    phase4_time = 0.008  # seconds (edit after reading your GBN graph)

    # Phase 5 (TCP): using the baseline completion time from the first run
    tcp_time = baseline_time

    labels = ["Phase 2", "Phase 3", "Phase 4", "TCP"]
    times = [phase2_time, phase3_time, phase4_time, tcp_time]
    plotter.plot_phase_comparison(labels, times)

    print("All Phase 5 TCP plots generated.")


if __name__ == "__main__":
    main()