from .libSIS import *

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
    #
    
    def reset_corr_tables(self, unit=None):
        if unit is None:
            self.AbsEncCorrData = [[0] * 64 for _ in range(3)]
            return
        #
        self.AbsEncCorrData[unit] = [0] * 64
    #
    
    def reset_corr_table_single(self, unit):
        self.reset_corr_tables(unit)
    #
    
    def set_corr_table(self, unit, corr_arr):
        #The following fails if the array_is not an 64 long array of integers 
        _corr_arr = [int(corr_arr[iEl]) for iEl in range(64)]
        
        #This fails if the unit is wrong
        self.AbsEncCorrData[unit] = [el for el in _corr_arr]
    #
     
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
