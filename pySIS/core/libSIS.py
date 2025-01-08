import sys
import platform
import serial
import time
from datetime import datetime
import struct


#checksum used to ensure correct communication
def check_sum (array): 
   csum = (sum(array) & 255) ^ 255
   return csum

def init(ser, unit):
    CMD_BYTE = 170
    RX_ARR_LEN = 4

    if not ser.is_open:
        ser.open()
    
    tx_array=[CMD_BYTE,
             unit,
             CMD_BYTE ^ 255,
             unit ^ 255,
             CMD_BYTE ^ 255,
             unit ^ 255]


    tx_array.append(check_sum(tx_array)) #This is the bytestring to write
    ser.write(bytearray(tx_array))
    time.sleep(0.01)
    
    try:
        rx_array = ser.read(RX_ARR_LEN)
        rx_array = list(rx_array)
    except Exception as err:
        print(f'ERROR --> init: failed to read the serial port {ser.port}. Exception message: {err}', file=sys.stderr)
        ser.close()
        return (tx_array, None)
    ser.close()

    #Check the validity of the response
    if len(rx_array)!=RX_ARR_LEN:
        print(f'ERROR --> init: Wrong length of the response array. {len(rx_array)} bytes instead of {RX_ARR_LEN} bytes.', file=sys.stderr)
        print(f'                Response array: {rx_array}', file=sys.stderr)
        return (tx_array, None)
    #
    if int(rx_array[0])!=CMD_BYTE:
        print(f'ERROR --> init: Response array wrong value: rx_array[0]={int(rx_array[0])} instead of {CMD_BYTE}.', file=sys.stderr)
        print(f'                Response array: {rx_array}', file=sys.stderr)
        return (tx_array, None)
    #

    return (tx_array, rx_array)



def get_status(ser):
    CMD_BYTE = 51
    RX_ARR_LEN = 15

    if not ser.is_open:
        ser.open()
    
    
    tx_array = [CMD_BYTE,
                0,
                0,
                0,
                0,
                0]
    
    tx_array.append(check_sum(tx_array))
    ser.write(bytearray(tx_array))
    time.sleep(0.01)

    try:
        rx_array = ser.read(RX_ARR_LEN)       
        rx_array = list(rx_array)
    except Exception as err:
        print(f'ERROR --> get_status: failed to read the serial port {ser.port}. Exception message: {err}', file=sys.stderr)
        ser.close()
        return (tx_array, None)
    #
    ser.close()

    if len(rx_array)!=RX_ARR_LEN:
        print(f'ERROR --> get_status: Wrong length of the response array. {len(rx_array)} bytes instead of {RX_ARR_LEN} bytes.', file=sys.stderr)
        print(f'                      Response array: {rx_array}', file=sys.stderr)
        return (tx_array, None)
    #
    if int(rx_array[0])!=CMD_BYTE:
        print(f'ERROR --> get_status: Response array wrong value: rx_array[0]={int(rx_array[0])} instead of {CMD_BYTE}.', file=sys.stderr)
        print(f'                      Response array: {rx_array}', file=sys.stderr)
        return (tx_array, None)
    #
    
    return (tx_array, rx_array)


def get_position(ser):
    CMD_BYTE = 85
    RX_ARR_LEN = 20

    if not ser.is_open:
        ser.open()
    
    tx_array = [CMD_BYTE,
                0,
                0,
                0,
                0,
                0]
    
    tx_array.append(check_sum(tx_array))
    ser.write(bytearray(tx_array))
    time.sleep(0.01)

    try:
        rx_array = ser.read(RX_ARR_LEN)
        rx_array = list(rx_array)
    except Exception as err:
        print(f'ERROR --> get_status: failed to read the serial port {ser.port}. Exception message: {err}', file=sys.stderr)
        ser.close()
        return (tx_array, None)
    #
    ser.close()

    if len(rx_array)!=RX_ARR_LEN:
        print(f'ERROR --> get_position: Wrong length of the response array. {len(rx_array)} bytes instead of {RX_ARR_LEN} bytes.', file=sys.stderr)
        print(f'                        Response array: {rx_array}', file=sys.stderr)
        return (tx_array, None)
    #
    if int(rx_array[0])!=CMD_BYTE:
        print(f'ERROR --> get_position: Response array wrong value: rx_array[0]={int(rx_array[0])} instead of {CMD_BYTE}.', file=sys.stderr)
        print(f'                        Response array: {rx_array}', file=sys.stderr)
        return (tx_array, None)
    #

    return (tx_array, rx_array)

def stop(ser, unit):
    CMD_BYTE = 195
    RX_ARR_LEN = 4

    if not ser.is_open:
        ser.open()
    
    tx_array = [CMD_BYTE,
                unit,
                CMD_BYTE ^ 255,
                unit ^ 255,
                CMD_BYTE ^ 255,
                unit ^ 255]
    
    tx_array.append(check_sum(tx_array))

    ser.write(bytearray(tx_array))
    time.sleep(0.01)

    try:
        rx_array = ser.read(RX_ARR_LEN)
        rx_array = list(rx_array)
    except Exception as err:
        print(f'ERROR --> stop: failed to read the serial port {ser.port}. Exception message: {err}', file=sys.stderr)
        ser.close()
        return (tx_array, None)
    #
    ser.close()
    
    if len(rx_array)!=RX_ARR_LEN:
        print(f'ERROR --> stop: Wrong length of the response array. {len(rx_array)} bytes instead of {RX_ARR_LEN} bytes.', file=sys.stderr)
        print(f'                Response array: {rx_array}', file=sys.stderr)
        return (tx_array, None)
    #
    if int(rx_array[0])!=CMD_BYTE:
        print(f'ERROR --> stop: Response array wrong value: rx_array[0]={int(rx_array[0])} instead of {CMD_BYTE}.', file=sys.stderr)
        print(f'                Response array: {rx_array}', file=sys.stderr)
        return (tx_array, None)
    #

    return (tx_array, rx_array)


def goto_position(ser, unit, pos):
    CMD_BYTE = 15
    RX_ARR_LEN = 6

    if not ser.is_open:
        ser.open()
    #

    pos_lsb = pos & 255
    pos_msb = pos // 256
    tx_array = [CMD_BYTE,
                unit,
                pos_lsb,
                pos_msb,
                CMD_BYTE ^ 255,
                unit ^ 255]
    
    tx_array.append(check_sum(tx_array))
    ser.write(bytearray(tx_array))
    time.sleep(0.01)

    try:
        rx_array = ser.read(RX_ARR_LEN)
        rx_array = list(rx_array)
    except Exception as err:
        print(f'ERROR --> goto_position: failed to read the serial port {ser.port}. Exception message: {err}', file=sys.stderr)
        ser.close()
        return (tx_array, None)
    #
    ser.close()

    if len(rx_array)!=RX_ARR_LEN:
        print(f'ERROR --> goto_position: Wrong length of the response array. {len(rx_array)} bytes instead of {RX_ARR_LEN} bytes.', file=sys.stderr)
        print(f'                         Response array: {rx_array}', file=sys.stderr)
        return (tx_array, None)
    #
    if int(rx_array[0])!=CMD_BYTE:
        print(f'ERROR --> goto_position: Response array wrong value: rx_array[0]={int(rx_array[0])} instead of {CMD_BYTE}.', file=sys.stderr)
        print(f'                         Response array: {rx_array}', file=sys.stderr)
        return (tx_array, None)
    #
    if int(rx_array[1])!=int(tx_array[1]):
        print(f'ERROR --> goto_position: Response array wrong unit ID: rx_array[1]={int(rx_array[1])} instead of {int(tx_array[1])}.', file=sys.stderr)
        print(f'                         Response array: {rx_array}', file=sys.stderr)
        return (tx_array, None)
    
    return (tx_array, tx_array)


# Function to send command and set configuration data
def set_config_data(ser, start_address, config_data):
    UART_CMD_SET_CONFIG_DATA = 136
    RX_ARR_LEN = 4
    ACK_OK = 0
    ACK_CFG_WRITE_DISABLED = 16

    if not ser.is_open:
        ser.open()
    #

    tx_array = [UART_CMD_SET_CONFIG_DATA, start_address]

    if isinstance(config_data, bytearray):
        tx_array += list(config_data[:4])
        tx_array.append(check_sum(tx_array))
        data_bytearr = bytearray([UART_CMD_SET_CONFIG_DATA, start_address]) + config_data[:4] + bytearray([tx_array[-1]])
    else:
        tx_array += config_data[:4]
        tx_array.append(check_sum(tx_array))
        data_bytearr = bytearray(tx_array)
    
    ser.write(data_bytearr)
    time.sleep(1)

    try:
        rx_array = ser.read(RX_ARR_LEN)
        rx_array = list(rx_array)
    except Exception as err:
        print(f'ERROR --> set_config_data: failed to set config data on SIS box on port {ser.port}, start address={start_address}, data={config_data[:4]}. Exception message: {err}', file=sys.stderr)
        ser.close()
        return (tx_array, None)
    #
    ser.close()
    
    # Validate the received packet
    if rx_array and len(rx_array) >= RX_ARR_LEN:
        rx_packet_checksum = check_sum(rx_array[:-1])
        if rx_packet_checksum == rx_array[-1]:
            if rx_array[0] != UART_CMD_SET_CONFIG_DATA:
                print(f"ERROR --> set_config_data: Invalid command byte received: {rx_array[0]} instead of {UART_CMD_SET_CONFIG_DATA}", file=sys.stderr)
                return (tx_array, None)
            elif rx_array[1] != start_address:
                print(f"ERROR --> set_config_data: Invalid start address received: {rx_array[1]} instead of {start_address}", file=sys.stderr)
                return (tx_array, None)
            elif rx_array[2] != ACK_OK:
                if rx_array[2] == ACK_CFG_WRITE_DISABLED:
                    print(f"ERROR --> set_config_data: failed to set config data on SIS box on port {ser.port}. Config write is disabled.", file=sys.stderr)
                    return (tx_array, None)
                else:
                    print(f"ERROR --> set_config_data: failed to set config data on SIS box on port {ser.port}. Bad acknowledge byte received: {rx_array[2]}", file=sys.stderr)
                    return (tx_array, None)
            else:
                print(f"Write on addresses [{start_address}:{start_address+3}] successful for SIS control box on port {ser.port}.")
        else:
            print(f"ERROR --> set_config_data: failed to set config data on SIS box on port {ser.port}. Invalid checksum received!", file=sys.stderr)
            return (tx_array, None)
    
    return (tx_array, rx_array)
#

def get_config_memory(ser):
    UART_CMD_GET_CONFIG_MEM = 119
    RX_ARR_LEN = 250

    # Open serial port
    if not ser.is_open:
        ser.open()
    ser.reset_input_buffer()

    # Construct transmission array (command packet)
    tx_array = [UART_CMD_GET_CONFIG_MEM, 0, 0, 0, 0, 0]
    tx_array.append(check_sum(tx_array))  # Append checksum
    
    # Send command
    ser.write(bytearray(tx_array))
    #print(f"Sent command: {tx_array}")
    time.sleep(1)
    
    # Wait for response
    try:
        rx_array = ser.read(RX_ARR_LEN)
        rx_array = list(rx_array)
    except Exception as err:
        print(f'ERROR --> get_config_memory: failed to read config data from SIS box on port {ser.port}. Exception message: {err}', file=sys.stderr)
        ser.close()
        return (tx_array, None)
    #
    ser.close()
    
    # Validate received packet
    if len(rx_array) != RX_ARR_LEN:
        print(f"ERROR --> get_config_memory: failed to read config data from SIS box on port {ser.port}. Invalid length of the serial response: received {len(rx_array)} bytes insteead of {RX_ARR_LEN} bytes", file=sys.stderr)
        return (tx_array, None)

    if rx_array and (len(rx_array) == RX_ARR_LEN):
        rx_packet_checksum = check_sum(rx_array[:-1])
        if rx_packet_checksum != rx_array[-1]:
            print(f"ERROR --> get_config_memory: failed to read config data from SIS box on port {ser.port}. Invalid packet or checksum error: received {rx_array[-1]} insteead of {rx_packet_checksum}", file=sys.stderr)
            return (tx_array, None)
            
        if rx_array[0] != tx_array[0]:
            print(f"ERROR --> get_config_memory: failed to read config data from SIS box on port {ser.port}. Invalid command byte received: {rx_array[0]} instead of {tx_array[0]}", file=sys.stderr)
            return (tx_array, None)
        
        print(f"Config data read successfully from SIS control box on port {ser.port}.")
    #

    return (tx_array, rx_array)


def bytearray_to_float(byte_array: bytearray) -> float:
    return struct.unpack('f', byte_array)[0]

def float_to_bytearray(value: float) -> bytearray:
    # Pack the float into 4 bytes, little-endian
    byte_array = struct.pack('<f', value)
    return bytearray(byte_array)

def signed_char_from_byte(byte_value):
    """
    Convert an unsigned byte (0-255) to a signed 8-bit integer (-128 to 127).
    """
    if byte_value > 127:
        return byte_value - 256
    else:
        return byte_value

def byte_from_signed_char(signed_value):
    """
    Convert a signed 8-bit integer (-128 to 127) to an unsigned byte (0-255).
    """
    if signed_value < 0:
        return signed_value + 256
    else:
        return signed_value
