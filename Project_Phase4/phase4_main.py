"""
    Nour Fahmy, Himadri Saha 

    phase4_main.py:
    Is the main runner file for project phase 4. Prompts the user to select scenario mode and displays some debug messages.
    Run this code only to run Phase 4.
    
    TODO:
    - Make prompt functionality
    - 

"""
# phase4_main.py
from sender_phase4 import GBN_Sender
from reciver_phase4 import GBN_Receiver
import threading

def main():

    print("\n--- EECE 4830 / Phase 4 ---")
    print("Go-Back-N Data Transfer Scenarios:")
    print("1 - No loss/bit errors")
    print("2 - ACK bit error")
    print("3 - Data bit error")
    print("4 - ACK loss")
    print("5 - Data loss\n")

    scenario = int(input("Enter scenario number (1-5): ").strip())

    # Load file
    with open(r"Project_Phase4\test_img.bmp", "rb") as f:
        file_bytes = f.read()

    # Receiver runs in its own thread
    receiver = GBN_Receiver(12000, scenario=scenario)

    receiver_thread = threading.Thread(target=receiver.run_receiver, daemon=True)
    receiver_thread.start()

    # Sender
    sender = GBN_Sender(
        receiver_ip="127.0.0.1",
        receiver_port=12000,
        scenario=scenario
    )

    sender.run_sender(file_bytes)

    receiver_thread.join(timeout=1)

    # Save received file
    with open("Project_Phase4\output.bmp", "wb") as f:
        output_bytes = b"".join(receiver.received_data)
        f.write(output_bytes)

    print("\n[MAIN] Transfer complete! Output saved to output.bmp\n")


if __name__ == "__main__":
    main()