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
    time.sleep(0.5)

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


class BoxConfig:
    # Constants
    ACK_REM_CMD_REJECTED = 1
    ACK_INVALID_ID = 2
    ACK_INVALID_VALUE = 4
    
    def __init__(self) -> None:
        self.reset_members()

    def reset_members(self) -> None:
        self.reset_corr_tables()
        #self.AbsEncCorrData_1 = [0] * 64
        #self.AbsEncCorrData_2 = [0] * 64
        #self.AbsEncCorrData_3 = [0] * 64
        self.MechPar_WheelDiam = [46.0] * 3
        self.MechPar_TapeThick = [0.1054] * 3
        self.MechPar_TapeLen = [6500.0] * 3
        self.MechPar_TapeHolePitch = [4.0] * 3
        self.Therm_LiquidArgonLevel = 0.0
        self.Therm_TapeAlpha = 0.0
    
    def reset_corr_tables(self, unit=None):
        if unit is None:
            self.AbsEncCorrData = [[0] * 64 for _ in range(3)]
            return
        #
        self.AbsEncCorrData[unit] = [0] * 64
        

    def read_data_from_file(self, fname):
        self.reset_members()

        try:
            with open(fname, 'r') as infile:
                # Read integer data
                for i in range(64):
                    self.AbsEncCorrData[0][i] = int(infile.readline().strip())
                for i in range(64):
                    self.AbsEncCorrData[1][i] = int(infile.readline().strip())
                for i in range(64):
                    self.AbsEncCorrData[2][i] = int(infile.readline().strip())

                # Read float data
                for i in range(3):
                    self.MechPar_WheelDiam[i] = float(infile.readline().strip())
                for i in range(3):
                    self.MechPar_TapeThick[i] = float(infile.readline().strip())
                for i in range(3):
                    self.MechPar_TapeLen[i] = float(infile.readline().strip())
                for i in range(3):
                    self.MechPar_TapeHolePitch[i] = float(infile.readline().strip())

                self.Therm_LiquidArgonLevel = float(infile.readline().strip())
                self.Therm_TapeAlpha = float(infile.readline().strip())
        except Exception as err:
            print(f"An error occurred while reading from file: {err}", file=sys.stderr)
        #
    #

    def write_data_to_file(self, fname):
        try:
            with open(fname, 'w') as file:
                # Write integer data
                for i in range(64):
                    file.write(f"{self.AbsEncCorrData[0][i]}\n")
                for i in range(64):
                    file.write(f"{self.AbsEncCorrData[1][i]}\n")
                for i in range(64):
                    file.write(f"{self.AbsEncCorrData[2][i]}\n")

                # Write float data
                for i in range(3):
                    file.write(f"{self.MechPar_WheelDiam[i]}\n")
                for i in range(3):
                    file.write(f"{self.MechPar_TapeThick[i]}\n")
                for i in range(3):
                    file.write(f"{self.MechPar_TapeLen[i]}\n")
                for i in range(3):
                    file.write(f"{self.MechPar_TapeHolePitch[i]}\n")

                file.write(f"{self.Therm_LiquidArgonLevel}\n")
                file.write(f"{self.Therm_TapeAlpha}\n")
        except Exception as err:
            print(f"An error occurred while writing to file: {err}")
    #

    def read_data_from_memory(self, ser):
        self.reset_members()

        tx_array, rx_array = get_config_memory(ser)

        if rx_array is None:
            return
        
        #Convert the rx_array back the a bytearray object for proper parsing
        rx_bytearr = bytearray(rx_array)[1:249]

        # Populate the parsed data (example assumes specific indexing)
        for i in range(64):
            try:
                self.AbsEncCorrData[0][i] = signed_char_from_byte(rx_bytearr[i])
                self.AbsEncCorrData[1][i] = signed_char_from_byte(rx_bytearr[i + 64])
                self.AbsEncCorrData[2][i] = signed_char_from_byte(rx_bytearr[i + 128])
            except IndexError as err:
                print(f'Out of array for index "i={i}". Length of "rx_bytearr"={len(rx_bytearr)}')
                raise
        #
        for i in range(3):
            self.MechPar_WheelDiam[i] = bytearray_to_float(rx_bytearr[192+(i*4):196+(i*4)])
            self.MechPar_TapeThick[i] = bytearray_to_float(rx_bytearr[204+(i*4):208+(i*4)])
            self.MechPar_TapeLen[i] = bytearray_to_float(rx_bytearr[216+(i*4):220+(i*4)])
            self.MechPar_TapeHolePitch[i] = bytearray_to_float(rx_bytearr[228+(i*4):232+(i*4)])

        self.Therm_LiquidArgonLevel = bytearray_to_float(rx_bytearr[240:244])
        self.Therm_TapeAlpha = bytearray_to_float(rx_bytearr[244:248])
    #

    def write_data_into_memory(self, ser):
        BYTEARR_LENGTH = 248
        
        #First concatenate the data for the corrections tables into a single bytearray
        data_bytearr = [byte_from_signed_char(val) for val in (self.AbsEncCorrData[0] + self.AbsEncCorrData[1] + self.AbsEncCorrData[2])]
        
        #Append the bytearray corresponding to the single parameters (spool diam., tape thickness, tape total length, Tape hole pitch) for each unit diameter of the three units
        for val in (self.MechPar_WheelDiam
                    + self.MechPar_TapeThick
                    + self.MechPar_TapeLen
                    + self.MechPar_TapeHolePitch
                    ):
            data_bytearr += float_to_bytearray(val)
        
        #Add the level of liquid argon in the cryostat
        data_bytearr += float_to_bytearray(self.Therm_LiquidArgonLevel)
        
        #Add the the thermal dilatation of the band material
        data_bytearr += float_to_bytearray(self.Therm_TapeAlpha)

        
        
        #Write the data in chunks of 4 bytes
        if(len(data_bytearr) != BYTEARR_LENGTH):
            print(f'Error while trying to write data into the memory. The byte array has {len(data_bytearr)} instead of {BYTEARR_LENGTH}')
            return
        
        for iChunk in range(int(len(data_bytearr)//4)):
            set_config_data(ser,
                            0+int(4*iChunk),
                            data_bytearr[int(4*iChunk):int(4*(iChunk+1))]
                            )
