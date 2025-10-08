# EECE 4830 - Network Design  
## Programming Project Phase 2 – Section II  
### RDT 2.2 Receiver with Extra Credit Features  
**Author:** Nour Fouad Fahmy  
**Teammate:** Himadri Saha

---

## File Descriptions
| File | Description |
|------|--------------|
| `RDT22_Receiver_Advanced.py` | Implements the advanced RDT 2.2 Receiver (CRC-16, delays, multi-threading). |
| `main_receiver.py` | Runs the receiver application. |
| `log.txt` | Records all packet activity and performance statistics. |

---

## How to Run
1. Ensure the sender (`RDT2.2_sender.py`) is running on the same network.
2. Place a test image (e.g., `test_img.JPG`) in the sender’s path.
3. Run the receiver first:
   ```bash
   python3 main_receiver.py
