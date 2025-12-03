"""
    Nour Fahmy, Himadri Saha

    phase5_main.py:
    - Run this for phase 5
    - Transmit test_img.bmp over Transmission Control Protocol (TCP) over an unreliable UDP socket connection
    - rx_img.bmp is the image that rx will see
    - Run all secnarios (secnarios number passed into tx rx classes)
    - All logging info will be written plotter class passed into sender and reciver and all plots will be outputted at the end

    Run secnarios:
    1. Completion Time vs Loss/Error Rate (0%-70%)
    2. Completion Time vs Timeout Value (10ms-100ms)
    3. Completion Time vs Window Size (1-50)
    4. Performance comparison of Phase 2, Phase 3, Phase 4 (and TCP)

"""
from phase5_sender import SENDER5
from phase5_reciver import RECIVER5
from plotter import PLOTTER5
import traceback

def main():
    # Start UPD connection thru init of the tx and rx
    my_plotter = PLOTTER5()
    try:
        my_sender = SENDER5(my_plotter)
        my_reciver = RECIVER5(my_plotter)
    except Exception:
        print("Failed UDP connection: ")
        traceback.print_exc() 

    ## Loop thru all secnarios
    with open(r"Project_Phase5\test_img.bmp", "rb") as f:
        img_bytes = f.read()
    for i in range(1, 5):
        # Run tx and rx with secnario number and their runner function(image)
        my_sender.run_tx(i, img_bytes)

    # Close all connections

    # Output plots

    return

if __name__ == "__main__":
    main()