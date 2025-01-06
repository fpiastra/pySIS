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
    if not ser.is_open:
        ser.open()
    cmd_byte = 170
    tx_array=[cmd_byte,
             unit,
             cmd_byte ^ 255,
             unit ^ 255,
             cmd_byte ^ 255,
             unit ^ 255]


    tx_array.append(check_sum(tx_array)) #This is the bytestring to write
    ser.write(bytearray(tx_array))
    time.sleep(0.5)
    
    try:
        rx_array = ser.read(4)
        rx_array = list(rx_array)
    except Exception as err:
        print(f'Error for SIS init. Exception message: {err}', file=sys.stderr)
        rx_array = None
    ser.close()
    return (tx_array, rx_array)



def get_status(ser):
    if not ser.is_open:
        ser.open()
    
    cmd_byte = 51
    tx_array = [cmd_byte,
                0,
                0,
                0,
                0,
                0]
    
    tx_array.append(check_sum(tx_array))
    ser.write(bytearray(tx_array))
    time.sleep(0.5)

    try:
        rx_array = ser.read(15)       
        rx_array = list(rx_array)
    except IndexError as err:
        print(f'Error for SIS init. Exception message: {err}', file=sys.stderr)
        rx_array = None
    ser.close()
    return (tx_array, rx_array)


def get_position(ser):
    if not ser.is_open:
        ser.open()
    
    cmd_byte = 85
    tx_array = [cmd_byte,
                0,
                0,
                0,
                0,
                0]
    
    tx_array.append(check_sum(tx_array))
    ser.write(bytearray(tx_array))
    time.sleep(0.01)

    try:
        rx_array = ser.read(20)
        rx_array = list(rx_array)
    except (IndexError):
        rx_array = None

    ser.close()
    return (tx_array, rx_array)

def stop(ser, unit):
    if not ser.is_open:
        ser.open()
    
    cmd_byte = 195
    tx_array = [cmd_byte,
                unit,
                cmd_byte ^ 255,
                unit ^ 255,
                cmd_byte ^ 255,
                unit ^ 255]
    
    tx_array.append(check_sum(tx_array))

    ser.write(bytearray(tx_array))
    time.sleep(0.5)

    try:
        rx_array = ser.readlines()[0]
        rx_array = list(rx_array)
    except (IndexError):
        rx_array = None

    return (tx_array, rx_array)


def goto_position(ser, unit, pos):
    if not ser.is_open:
        ser.open()
    
    cmd_byte = 15
    pos_lsb = pos & 255
    pos_msb = pos // 256
    tx_array = [cmd_byte,
                unit,
                pos_lsb,
                pos_msb,
                cmd_byte ^ 255,
                unit ^ 255]
    
    tx_array.append(check_sum(tx_array))
    ser.write(bytearray(tx_array))
    time.sleep(0.5)

    try:
        rx_array = ser.read(6)
        rx_array = list(rx_array)
    except Exception as err:
        print(f'Error for SIS move for unit {unit}. Exception message: {err}', file=sys.stderr)
        rx_array = None

    return (tx_array, rx_array)


# Function to send command and set configuration data
def set_config_data(ser, start_address, config_data):
    UART_CMD_SET_CONFIG_DATA = 136
    RX_PACKET_LENGTH = 4
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
    time.sleep(0.1)

    try:
        rx_array = ser.read(RX_PACKET_LENGTH)
        rx_array = list(rx_array)
    except Exception as err:
        print(f'Error for setting config data on SIS box on port {ser.port}. Exception message: {err}', file=sys.stderr)
        return (tx_array, None)
    
    # Validate the received packet
    if rx_array and len(rx_array) >= RX_PACKET_LENGTH:
        rx_packet_checksum = check_sum(rx_array[:-1])
        if rx_packet_checksum == rx_array[-1]:
            if rx_array[0] != tx_array[0]:
                print("Invalid command byte received.")
                return (tx_array, None)
            elif rx_array[1] != tx_array[1]:
                print("Invalid start address received.")
                return (tx_array, None)
            elif rx_array[2] != ACK_OK:
                if rx_array[2] == ACK_CFG_WRITE_DISABLED:
                    print(f"Error for setting config data on SIS box on port {ser.port}. Config write is disabled.")
                    return (tx_array, None)
                else:
                    print(f"Error for setting config data on SIS box on port {ser.port}. Bad acknowledge byte received: {rx_array[2]}", file=sys.stderr)
                    return (tx_array, None)
            else:
                print(f"Write on addresses [{start_address}:{start_address+3}] successful.")
        else:
            print(f"Error for setting config data on SIS box on port {ser.port}. Invalid checksum received!", file=sys.stderr)
            return (tx_array, None)
    
    return (tx_array, rx_array)
#

def get_config_memory(ser):
    UART_CMD_GET_CONFIG_MEM = 119
    RX_PACKET_LENGTH = 250

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
        rx_array = ser.read(RX_PACKET_LENGTH)
        rx_array = list(rx_array)
    except Exception as err:
        print(f'Error for reading config data from SIS box on port {ser.port}. Exception message: {err}', file=sys.stderr)
        return (tx_array, None)
    
    
    # Validate received packet
    if len(rx_array) != RX_PACKET_LENGTH:
        print(f"Error for reading config data from SIS box on port {ser.port}. Invalid length of the serial response: received {len(rx_array)} bytes insteead of {RX_PACKET_LENGTH} bytes", file=sys.stderr)
        return (tx_array, None)

    if rx_array and (len(rx_array) == RX_PACKET_LENGTH):
        rx_packet_checksum = check_sum(rx_array[:-1])
        if rx_packet_checksum != rx_array[-1]:
            print(f"Error for reading config data from SIS box on port {ser.port}. Invalid packet or checksum error: received {rx_array[-1]} insteead of {rx_packet_checksum}", file=sys.stderr)
            return (tx_array, None)
            
        if rx_array[0] != tx_array[0]:
            print(f"Error for reading config data from SIS box on port {ser.port}. Invalid command byte received: {rx_array[0]} instead of {tx_array[0]}", file=sys.stderr)
            return (tx_array, None)
        
        print("Command successful.")
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
