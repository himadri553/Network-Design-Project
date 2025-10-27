# RDT3.0 Project - Phase 3

**Team Members:** Nour Fahmy, Himadri Saha  
**Course:** EECE 4830 - Network Design  
**Phase:** 3  

---

## Files Submitted
| File | Purpose |
|------|---------|
| RDT3.0_sender.py | Implements sender-side RDT3.0: stop-and-wait, timeout-based retransmission, scenario-based ACK errors and loss |
| RDT3.0_receiver.py | Implements receiver-side RDT3.0: handles DATA packet loss and bit errors, writes received file |
| performance_plot.py | Generates completion time plots for all 5 scenarios |
| scenario_mode.txt | Defines which scenario to run and the loss/error rate |
| test_img.JPG | Test file for sending over the protocol |
| sender_completion_time.txt | Logs sender completion times for performance analysis |
| receiver_completion_time.txt | Logs receiver completion times for performance analysis |

---

## Introduction
This project implements RDT3.0, a reliable data transfer protocol over UDP. Phase 3 features:

- Stop-and-wait protocol with sequence numbers and checksums.
- Scenario-based simulations for data packet loss, ACK loss, and bit errors.
- Recording of sender and receiver completion times.
- Performance plots for all scenarios, showing the effect of increasing loss/error rates.

---

## Environment
- **Language:** Python 3  
- **Libraries:** `matplotlib`  
- **Platform:** Mac/Linux/Windows  
- **Networking:** Standard Python `socket` module  

---

## Step-by-Step Instructions

### 1. Setup
1. Ensure Python 3 is installed: 
python3 --version

2. Install matplotlib if not installed:
pip3 install matplotlib


3. Place test_img.JPG under Project_Phase3.

4. Ensure scenario_mode.txt exists. If not, the default will be scenario 1 with 20% loss.

### 2. How to execute
Open two terminals:

Terminal 1 (Receiver):

cd Project_Phase3
python3 RDT3.0_receiver.py


Terminal 2 (Sender):

cd Project_Phase3
python3 RDT3.0_sender.py

### 3. How to Check Scenarios
Edit Project_Phase3/scenario_mode.txt:

<scenario_number>
<loss_rate>

Scenario	Description
1	        No loss/error
2	        ACK bit error
3	        Data packet error
4	        ACK packet loss
5	        Data packet loss

Example:

2
0.1
Runs Scenario 2 with 10% ACK bit error.

### 4. Special Requirements
- Run receiver and sender in separate terminals simultaneously.

- Ensure port 12000 is free.

- All files should remain in the Project_Phase3 folder.

- Designed for users with no programming knowledge; instructions are step-by-step.

---

## Code Description

### Receiver (RDT3.0_receiver.py)
- Initializes UDP server socket and output file (`received.jpg`).
- Reads `scenario_mode.txt` to determine scenario number and loss/error rate.
- Listens for incoming packets:
  - Scenario 3: Injects bit errors into DATA packets.
  - Scenario 5: Drops DATA packets to simulate loss.
- Valid packets are written to file; ACKs sent for each valid packet.
- Previous ACK resent if a packet is corrupted or out-of-order.
- Completion time recorded in `receiver_completion_time.txt`.

### Sender (RDT3.0_sender.py)
- Reads test image in chunks of 1024 bytes.
- Builds packets: `[seq_num (1B) | checksum (2B) | data]`.
- Sends packets with stop-and-wait retransmission on timeout.
- Scenario 2: ACK bit errors simulated.
- Scenario 4: ACK loss simulated.
- Sends `END` after last packet.
- Completion time recorded in `sender_completion_time.txt`.

### Performance Plot (performance_plot.py)
- Reads recorded completion times for all 5 scenarios.
- Plots sender and receiver times vs. loss/error rates using `matplotlib`.

---