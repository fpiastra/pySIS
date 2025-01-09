import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pySIS.core import goto_position, get_position, get_status
from serial import Serial
import time
from datetime import datetime
from os import path


#These below are default values that can be overwritten by the user at the command line
PORT = None
UNIT = 0
POS = 0 #In mm
FNAME = None #The file where the data is dumped

DEBUG = False #Hardcoded switch to be changed manually

MAXPOS = 8890 #Maximum possible extension (in mm) due to "non SIS" limitations (e.g. the calibration tubes)

#position/status check every delta_t seconds
DELTA_T = 0.01


#These are only used to come upwards
STEP_SIZE = 50 #In mm
STEP_SLEEP = 30 #In seconds


if __name__ == '__main__':

    timestamp = datetime.now()

    if len(sys.argv) != 5:
        print('ERROR --> Wrong number of arguments!', file=sys.stderr)
        print(f'Synopsys: python {sys.argv[0]} <serport> <unit_number> <pos> <logfilename>\n', file=sys.stderr)
        sys.exit(1)
    
    
    PORT = sys.argv[1]
    UNIT = int(sys.argv[2])
    
    POS = int(sys.argv[3])
    if POS>MAXPOS:
        print(f'WARNING --> Requested position {POS} not allowed. Resetting to position {MAXPOS}.')
        POS = MAXPOS
    
    FNAME = sys.argv[4]
    #Compose the name in order to put inside also the timestamp
    name, ext = path.splitext(FNAME)
    name = '_'.join([name,timestamp.strftime("%Y%m%d-%H%M%S")])
    FNAME = name + ext
    
    #Create the empty file
    with open(FNAME, 'w') as _f:
        pass
    
    
    #Going downwards
    print('\n\n')
    print(f'Moving unit {UNIT} to position {POS} mm.')

    ser = Serial(PORT, baudrate=9600, timeout=0.5)
    tx_arr, rx_arr = goto_position(ser, UNIT, POS)
    
        

    print("Requested positions have been transmitted.")
    #file.write(current_time + ': Requested positions have been transmitted.\n')
    time.sleep(0.05)
    
    #Loop to track the position of the source while moving
    while True:
        
        try:
            unixitme = time.time()
            tx_arr, rx_arr = get_position(ser)
            abs_pos_lsb = rx_arr[1 + 4 * UNIT]
            abs_pos_msb = rx_arr[2 + 4 * UNIT]
            inc_pos_lsb = rx_arr[3 + 4 * UNIT]
            inc_pos_msb = rx_arr[4 + 4 * UNIT]
            abs_raw_lsb = rx_arr[13 + 2 * UNIT]
            abs_raw_msb = rx_arr[14 + 2 * UNIT]
            rx_pos_abs = 256 * abs_pos_msb + abs_pos_lsb
            rx_pos_inc = 256 * inc_pos_msb + inc_pos_lsb
            rx_position = rx_pos_inc
        
        except (IndexError):
            continue
        except Exception as err:
            print(f'ERROR --> After the "get_position" request. Exception message: {err}', file=sys.stderr)

        abs_pos_err = False
        inc_pos_err = False
        if not (-25 <= rx_pos_abs <= 10500):
            abs_pos_err = True
            print(f'WARNING --> Absolute position out of range ({rx_pos_abs})!')
        if not -25 <= rx_pos_inc <= 10500:
            inc_pos_err = True
            print(f'WARNING --> Incremental position out of range ({rx_pos_inc})!')
        #

        if not (abs_pos_err or inc_pos_err): 
            print(f'Pos inc: {rx_pos_inc}; Pos abs: {rx_pos_abs}; Abs raw pos: {int(abs_raw_msb)} {int(abs_raw_lsb)}; Downward')
            if FNAME is not None:
                with open(FNAME, 'a') as logfile:
                    logfile.write(f'{unixitme}~{rx_pos_inc}~{rx_pos_abs}~{int(abs_raw_msb)}~{int(abs_raw_lsb)}~0\n')
        
        time.sleep(DELTA_T)

        try:
            tx_arr, rx_arr = get_status(ser)
            rx_motor = rx_arr[8+UNIT] & 3
        except (IndexError):
            continue
        except Exception as err:
            print(f'ERROR --> After the "get_status" request. Exception message: {err}', file=sys.stderr)
        #

        if (rx_motor==0) and (int(rx_pos_inc)==POS):
            print(f"Downward movement of unit {UNIT} finished.")
            break
        #
    # Close of the while loop
    
    print('\n\nChecking position after downward run:')
    
    try:
        tx_arr, rx_arr = get_position(ser)
        abs_pos_lsb = rx_arr[1 + 4 * UNIT]
        abs_pos_msb = rx_arr[2 + 4 * UNIT]
        inc_pos_lsb = rx_arr[3 + 4 * UNIT]
        inc_pos_msb = rx_arr[4 + 4 * UNIT]
        abs_raw_lsb = rx_arr[13 + 2 * UNIT]
        abs_raw_msb = rx_arr[14 + 2 * UNIT]
        rx_pos_abs = 256 * abs_pos_msb + abs_pos_lsb
        rx_pos_inc = 256 * inc_pos_msb + inc_pos_lsb
        rx_position = rx_pos_inc
    
    except (IndexError):
        pass
    except Exception as err:
        print(f'ERROR --> After the "get_position" request. Exception message: {err}', file=sys.stderr)
    #
    
    print("Current incremental encoder position:",rx_pos_inc)
    print("Current absolute encoder position:",rx_pos_abs)
    print(f"Current absolute encoder bytes: {abs_raw_msb} {abs_raw_lsb}\n")

    #####################
    #Going upward
    while rx_pos_inc>0:
        time.sleep(STEP_SLEEP)

        new_pos = rx_pos_inc-STEP_SIZE
        if new_pos < 0:
            new_pos = 0
        tx_arr, rx_arr = goto_position(ser, UNIT, new_pos)

        while True:
            try:
                unixitme = time.time()
                tx_arr, rx_arr = get_position(ser)
                abs_pos_lsb = rx_arr[1 + 4 * UNIT]
                abs_pos_msb = rx_arr[2 + 4 * UNIT]
                inc_pos_lsb = rx_arr[3 + 4 * UNIT]
                inc_pos_msb = rx_arr[4 + 4 * UNIT]
                abs_raw_lsb = rx_arr[13 + 2 * UNIT]
                abs_raw_msb = rx_arr[14 + 2 * UNIT]
                rx_pos_abs = 256 * abs_pos_msb + abs_pos_lsb
                rx_pos_inc = 256 * inc_pos_msb + inc_pos_lsb
                rx_position = rx_pos_inc
        
            except (IndexError):
                continue
            except Exception as err:
                print(f'ERROR --> After the "get_position" request. Exception message: {err}', file=sys.stderr)

            abs_pos_err = False
            inc_pos_err = False
            if not (-25 <= rx_pos_abs <= 10500):
                abs_pos_err = True
                print(f'WARNING --> Absolute position out of range ({rx_pos_abs})!')
            if not -25 <= rx_pos_inc <= 10500:
                inc_pos_err = True
                print(f'WARNING --> Incremental position out of range ({rx_pos_inc})!')
            #

            if not (abs_pos_err or inc_pos_err): 
                print(f'Pos inc: {rx_pos_inc}; Pos abs: {rx_pos_abs}; Abs raw pos: {int(abs_raw_msb)} {int(abs_raw_lsb)}; Upward')
                if FNAME is not None:
                    with open(FNAME, 'a') as logfile:
                        logfile.write(f'{unixitme}~{rx_pos_inc}~{rx_pos_abs}~{int(abs_raw_msb)}~{int(abs_raw_lsb)}~1\n')

            time.sleep(DELTA_T)

            try:
                tx_arr, rx_arr = get_status(ser)
                rx_motor = rx_arr[8+UNIT] & 3
            except (IndexError):
                continue
            except Exception as err:
                print(f'ERROR --> After the "get_status" request. Exception message: {err}', file=sys.stderr)
            #

            if (rx_motor==0) and (int(rx_pos_inc)==new_pos):
                print(f"Upward step of unit {UNIT} finished.")
                break
            #
        # Close inner while loop
    #Close the outer while loop (the steps)

    print('\n\nChecking position after upward run:')
    
    try:
        tx_arr, rx_arr = get_position(ser)
        abs_pos_lsb = rx_arr[1 + 4 * UNIT]
        abs_pos_msb = rx_arr[2 + 4 * UNIT]
        inc_pos_lsb = rx_arr[3 + 4 * UNIT]
        inc_pos_msb = rx_arr[4 + 4 * UNIT]
        abs_raw_lsb = rx_arr[13 + 2 * UNIT]
        abs_raw_msb = rx_arr[14 + 2 * UNIT]
        rx_pos_abs = 256 * abs_pos_msb + abs_pos_lsb
        rx_pos_inc = 256 * inc_pos_msb + inc_pos_lsb
        rx_position = rx_pos_inc
    
    except (IndexError):
        pass
    except Exception as err:
        print(f'ERROR --> After the "get_position" request. Exception message: {err}', file=sys.stderr)
    #
    
    print("Current incremental encoder position:",rx_pos_inc)
    print("Current absolute encoder position:",rx_pos_abs)
    print(f"Current absolute encoder bytes: {abs_raw_msb} {abs_raw_lsb}\n")

