import sys
from pySIS.core import BoxConfig
from serial import Serial
import time
import traceback

FNAME = None

if __name__ == '__main__':
    
    if (len(sys.argv)<2) or (len(sys.argv)>3):
        print("", file=sys.stderr)
        print(f"Error: wrong number of few arguments for {sys.argv[0]} script.", file=sys.stderr)
        print(f"Synopsys: python {sys.argv[0]} <serport> [filename]\n", file=sys.stderr)
        sys.exit(1)
    #
    PORT = sys.argv[1]

    if len(sys.argv) == 3:
        FNAME = sys.argv[2]

    print(f'Connecting to serial port device <{PORT}>')
    ser = Serial(port=PORT, baudrate=9600, timeout = 0.1)
    if not ser.is_open:
        ser.open()
    #
    print(f'Connection to <{ser.port}> established.')
    
    try:
        boxConfig = BoxConfig()
        if not (FNAME is None):
            boxConfig.read_data_from_file(FNAME)
        boxConfig.write_data_into_memory(ser)

    except Exception as err:
        print(f'Error trying to write the SIS memory. Exception message: {err}')
        traceback.print_exc()
    finally:
        ser.close()