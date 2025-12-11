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
import traceback
import threading
import os

def main():
    # Start UPD connection thru init of the tx and rx
    my_plotter = PLOTTER5()
    try:
        my_sender = SENDER5(my_plotter)
        my_reciver = RECIVER5(my_plotter)
    except Exception:
        print("Failed UDP connection: ")
        traceback.print_exc() 
        return
    rx_thread = threading.Thread(target=my_reciver.run_rx, daemon=False)
    rx_thread.start()

    # Split image into chunks
    img_in_chunks = []
    pic_path = os.path.join("Project_Phase5", "img", "test_img.bmp")
    with open(pic_path, "rb") as f:
        file_data = f.read()
    CHUNK_SIZE = 1024
    for i in range(0, len(file_data), CHUNK_SIZE):
        chunk = file_data[i:i+CHUNK_SIZE]
        img_in_chunks.append(chunk) 

    # Handoff full image to sender
    ## secnario_num 0 for teesting
    my_sender.run_tx(img_in_chunks=img_in_chunks, secnario_num=0)

    return

if __name__ == "__main__":
    main()