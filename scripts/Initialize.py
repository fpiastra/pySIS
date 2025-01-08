import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pySIS.core import init, get_status
from serial import Serial
import time
from datetime import datetime


#These below are default values that can be overwritten by the user at the command line

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Too few arguments for {sys.argv[0]} script.', file=sys.stderr)
        print(f'Synopsys: python {sys.argv[0]} <serport> <unit_number>\n', file=sys.stderr)
        sys.exit(1)
    #
    
    PORT = sys.argv[1]
    UNIT = int(sys.argv[2])
    #
    
    ser = Serial(PORT, baudrate=9600, timeout = 0.1)
    
    tx_arr, rx_arr = init(ser, UNIT)
    if rx_arr is None:
        sys.exit(1)
    #

    print(f"Initialisation of unit {UNIT} at port <{PORT}> in progress.")

    time.sleep(2)

    #Loop to track the position of the source while moving
    max_time = time.time() + 60*25 #maximal waiting time 25 mins
    while True:
        if time.time() > max_time:
            print("Maximum waiting time has expired. Make sure that communication works properly, and check the positions.")
            break

        tx_arr, rx_arr = get_status(ser=ser)

        if rx_arr is None:
            continue
        #
        try:
            rx_init_bit = rx_arr[8 + (UNIT+1)] >> 2 & 1 
            rx_init_bit_progress = rx_arr[8 + (UNIT+1)] >> 3 & 1 
            current_time = datetime.now().strftime("%H-%M-%S")
        except IndexError:
            continue
        #
        if (rx_init_bit_progress == 0 and rx_init_bit == 1):
            print(f'{current_time}: Unit {UNIT} at port <{PORT}> has been initialised successfully.\n') 
            break
        #
        if (rx_init_bit_progress == 0 and rx_init_bit == 0):
            print(f'{current_time}: Unit {UNIT} at port <{PORT}> has not been initialised successfully. Try again later, or run another script.\n') 
            break