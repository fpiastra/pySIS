import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from serial import Serial
import time
import traceback


if __name__ == '__main__':
    
    if len(sys.argv) != 3:
        print(f"Error: wrong number of few arguments for {sys.argv[0]} script.", file=sys.stderr)
        print("Synopsys: python GetConfigIntoFile.py <serport> <filename>", file=sys.stderr)
        sys.exit(1)
    #
    PORT = sys.argv[1]
    FNAME = sys.argv[2]

    print(f'Connecting to serial port device <{PORT}>')
    ser = Serial(PORT, baudrate=9600, timeout = 0.1)
    if not ser.is_open:
        ser.open()
    #
    print(f'Connection to <{ser.port}> established.')
    
    try:
        boxConfig = BoxConfig()
        boxConfig.read_data_from_memory(ser=ser)

        boxConfig.write_data_to_file(FNAME)
    except Exception as err:
        print(f'Error while trying to dump the SIS box memory. Exception message: {err}')
        traceback.print_exc()
    finally:
        ser.close()