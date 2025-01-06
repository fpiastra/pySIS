import sys
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

MAXPOS = 8890 #Maximum possible extension (in mm) due to "non SIS" limitations (e.g. the calibration tubes)

#position/status check every delta_t seconds
DELTA_T = 0.1

#maximal waiting time 25 mins
MAX_TIME = time.time() + 60*25 

if __name__ == '__main__':

    timestamp = datetime.now()

    if len(sys.argv) < 2:
        print('Too few arguments. At least the device name is required!', file=sys.stderr)
        print('Synopsys: python MoveAndTrackSingle.py <serport> <unit_number> <pos> [logfilename]\n', file=sys.stderr)
        sys.exit(1)
    
    
    PORT = sys.argv[1]

    UNIT = int(sys.argv[2])
    
    if len(sys.argv) > 3:
        POS = int(sys.argv[3])
        if POS>MAXPOS:
            print(f'WARNING --> Requested position {POS} not allowed. Resetting to position {MAXPOS}.')
            POS = MAXPOS
    
    if len(sys.argv) > 4:
        FNAME = sys.argv[4]
        #Compose the name in order to put inside also the timestamp
        name, ext = path.splitext(FNAME)
        name = '_'.join([name,timestamp.strftime("%Y%m%d-%H%M%S")])
        FNAME = name + ext
        
        #Create the empty file
        with open(FNAME, 'W') as _f:
            pass
    
    

    print('\n\n')
    print(f'Moving unit {UNIT} to position {POS} mm.')

    ser = Serial(PORT, baudrate=9600, timeout=0.5)
    tx_arr, rx_arr = goto_position(ser, UNIT, POS)

    print("Requested positions have been transmitted.")
    #file.write(current_time + ': Requested positions have been transmitted.\n')
    time.sleep(0.05)
    
    #Loop to track the position of the source while moving
    while True:
        
        #current_time = datetime.now().strftime("%H-%M-%S")
        if time.time() > MAX_TIME:
            print("Maximum waiting time has expired. Make sure that communication works properly, and check positions.")
            #file.write(current_time + ': Maximum waiting time has expired. Make sure that communication works properly, and check positions.\n')
            break
        #
        
        try:
            tx_arr, rx_arr = get_status(ser)
            rx_motor = rx_arr[8+UNIT] & 3
        except (IndexError):
            continue
        except Exception as err:
            print(f'ERROR --> After the "get_status" request. Exception message: {err}', file=sys.stderr)
        #

        if (rx_motor == 0):
            print(f"Movement of unit {UNIT} finished.")
            break
        #

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
            print(f'Pos inc: {rx_pos_inc}; Pos abs: {rx_pos_abs}; Turns: {int(abs_raw_msb)}_{int{abs_raw_lsb}}')
            if FNAME is not None:
                with open(FNAME, 'a') as logfile:
                    logfile.write(f'{unixitme}~{rx_pos_inc}~{rx_pos_abs}~{int(abs_raw_msb)}~{int{abs_raw_lsb}}\n')
        
        time.sleep(DELTA_T)
    # Close of the while loop
    
    print('\n\nChecking position after stop:')
    
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
