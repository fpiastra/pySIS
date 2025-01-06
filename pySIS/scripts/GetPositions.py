import sys
from pySIS.core.libSIS import get_position
from serial import Serial
import time
import datetime


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print(f'Too few arguments for {sys.argv[0]} script.', file=sys.stderr)
        print(f'Synopsys: python {sys.argv[0]} <serport> <unit_number>\n', file=sys.stderr)
        sys.exit(1)
    
    ser_dev = sys.argv[1]
    
    UNIT = int(sys.argv[2])

    ser = Serial(ser_dev, baudrate=9600, timeout = 0.1)
    
    start_time = time.perf_counter()
    tx_arr, rx_arr = get_position(ser)
    end_time = time.perf_counter()

    try:
        abs_pos_lsb = rx_arr[1 + 4 * UNIT]
        abs_pos_msb = rx_arr[2 + 4 * UNIT]
        inc_pos_lsb = rx_arr[3 + 4 * UNIT]
        inc_pos_msb = rx_arr[4 + 4 * UNIT]
        rx_pos_abs = 256 * abs_pos_msb + abs_pos_lsb
        rx_pos_inc = 256 * inc_pos_msb + inc_pos_lsb
        rx_position = rx_pos_inc
    
    except (IndexError):
        pass
    except Exception as err:
        pass

    print()    
    print(f"Pos abs: {rx_pos_abs}; Pos inc: {rx_pos_inc} (in {end_time-start_time} sec)")


