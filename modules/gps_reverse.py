'''
This module contains tools to import raw GPS data for
use with the soft correlator.
'''
import numpy as np
import configparser
import os

global d

def main():
    d = IQData('./resources/Single4092KHz5s.max')

class ComplexReturner:
    '''
    Reads in an IQ sampled file, but saves memory
    '''
    stop = False
    complexCarry = 0 + 0j

    def __init__(self, FileDirectory, Skip = 0):
        '''
        # Args
        FileDirectory: directory of the raw data file to read
        Skip: the number of bytes in the file to skip forward
        '''
        self.dir = FileDirectory
        self.f = open(self.dir, 'rb') #Hold the file open
        
        self.fptr = Skip
        self.fsize = os.path.getsize(self.dir)
        self.f.seek(self.fptr)

    
    def returnSampleArray(self, ArraySize):
        '''
        Returns a numpy array of complex data of the size specified
        # Args
        ArraySize: the number of samples in the returned array
        # Outputs
        returnArray: numpy array of complex IQ data samples
        '''
        returnArray = np.zeros(ArraySize, dtype=complex)

        if self.complexCarry != (0 + 0j):
            #If there is a value waiting to be carried in, then 
            #use it for the first element
            returnArray[0] = self.complexCarry
            self.complexCarry = 0+0j
            i = 1
        else:
            i = 0
        
        while i < ArraySize:
            #Read a converted byte, and place the two samples in the array
            I1, I2, Q1, Q2 = self._byteToIQPairs(ord(self.f.read(1)))
            returnArray[i] = I1 + Q1 * 1j
            i += 1
            try:
                returnArray[i] = I2 + Q2 * 1j
                i += 1
                
            except IndexError:
                #If there is not room for the last sample, save it for
                #the next one
                #print('carrying')
                self.complexCarry = I2 + Q2 * 1j

            #Need to handle EOF

        
        return returnArray

    def _byteToIQPairs(self, TheByte ):
        '''
        Reads each of the four pairs of bits from the byte
        and determines the sign and magnitude. Then it returns a list
        containing two pairs of IQ data as floating point [I1,Q1,I2,Q2].
        For magnitude: a bit value of 1 means mag 1, 0 means mag 1/3
        For sign: a bit value of 1 means negative, 0 means positive
        
        This interpretation was taken by the sample code provided
        in the PSAS Launch12 github repo (example was provided in C)
        '''

        IMag1 = (TheByte >> 7) & (0b00000001)
        ISign1 = (TheByte >> 6) & (0b00000001)
        I1 = 1.0 if (IMag1 == 1) else 1.0/3.0
        I1 = -I1 if (ISign1 == 1) else I1

        QMag1 = (TheByte >> 5) & (0b00000001)
        QSign1 = (TheByte >> 4) & (0b00000001)
        Q1 = 1.0 if (QMag1 == 1) else 1.0/3.0
        Q1 = -Q1 if (QSign1 == 1) else Q1

        IMag2 = (TheByte >> 3) & (0b00000001)
        ISign2 = (TheByte >> 2) & (0b00000001)
        I2 = 1.0 if (IMag2 == 1) else 1.0/3.0
        I2 = -I2 if (ISign2 == 1) else I2

        QMag2 = (TheByte >> 1) & (0b00000001)
        QSign2 = (TheByte >> 0) & (0b00000001)
        Q2 = 1.0 if (QMag2 == 1) else 1.0/3.0
        Q2 = -Q2 if (QSign2 == 1) else Q2

        return (I1, I2, Q1, Q2)


class IQData:
    '''
    Opens an IQ data stream stored in a file that is formatted as specified
    '''

    IData = []
    QData = []
    CData = []

    sampleFreq = 0
    sampleTime = 0
    Nsamples   = 0

    def _byteToIQPairs(self, TheByte, realOnly=False):
        '''
        Reads each of the four pairs of bits from the byte
        and determines the sign and magnitude. Then it returns a list
        containing two pairs of IQ data as floating point [I1,Q1,I2,Q2].
        For magnitude: a bit value of 1 means mag 1, 0 means mag 1/3
        For sign: a bit value of 1 means negative, 0 means positive
        
        This interpretation was taken by the sample code provided
        in the PSAS Launch12 github repo (example was provided in C)
        '''

        if realOnly:
            IMag1 = (TheByte >> 7) & (0b00000001)
            ISign1 = (TheByte >> 6) & (0b00000001)
            I1 = 1.0 if (IMag1 == 1) else 1.0/3.0
            I1 = -I1 if (ISign1 == 1) else I1

            IMag2 = (TheByte >> 3) & (0b00000001)
            ISign2 = (TheByte >> 2) & (0b00000001)
            I2 = 1.0 if (IMag2 == 1) else 1.0/3.0
            I2 = -I2 if (ISign2 == 1) else I2

            Q1 = 0
            Q2 = 0

        else:
            IMag1 = (TheByte >> 7) & (0b00000001)
            ISign1 = (TheByte >> 6) & (0b00000001)
            I1 = 1.0 if (IMag1 == 1) else 1.0/3.0
            I1 = -I1 if (ISign1 == 1) else I1

            QMag1 = (TheByte >> 5) & (0b00000001)
            QSign1 = (TheByte >> 4) & (0b00000001)
            Q1 = 1.0 if (QMag1 == 1) else 1.0/3.0
            Q1 = -Q1 if (QSign1 == 1) else Q1

            IMag2 = (TheByte >> 3) & (0b00000001)
            ISign2 = (TheByte >> 2) & (0b00000001)
            I2 = 1.0 if (IMag2 == 1) else 1.0/3.0
            I2 = -I2 if (ISign2 == 1) else I2

            QMag2 = (TheByte >> 1) & (0b00000001)
            QSign2 = (TheByte >> 0) & (0b00000001)
            Q2 = 1.0 if (QMag2 == 1) else 1.0/3.0
            Q2 = -Q2 if (QSign2 == 1) else Q2

        return (I1, I2, Q1, Q2)

    def _complexData(self):
        '''
        Returns array of complex data
        '''
        self.CData = np.zeros(len(self.IData), dtype=np.complex)
        self.CData = np.array(self.IData) + np.array(self.QData) * 1j  # Complex data
        return

    def _timeVector(self, bytesToSkip, Ts, seconds):
        '''
        Generates time vector of requested data.
        Will assume that t=0 for the start of file.
        '''

        # Each byte has 2 IQ pairs, so 2*Ts seconds will have elapsed.
        StartingTime = bytesToSkip*2*Ts
        self.tStart = StartingTime

        EndingTime = StartingTime + seconds
        self.tEnd = EndingTime

        self.t = np.linspace(self.tStart, self.tEnd, self.Nsamples)

    def importFile(self, path, fs, seconds, bytestoskip, realOnly=False):
        '''
        imports IQ Data from a file
        # Args
        
        path: location of file to import
        fs: sampling frequency
        seconds: the length of data in seconds
        
        bytestoskip: integer number of bytes in the file (i.e. samples/2) to skip in the file
        # kwArgs
        realOnly: ignore the complex data points when importing
        # Returns
        Function has no returns, but reads the file data into the IData, QData, and/or CData arrays
        '''
        print("Opening a file.")
        fHandle = open(path,'rb')
        print("File handle is: %d." % (fHandle.fileno()))

        self.sampleFreq = fs
        self.sampleTime = seconds
        self.bytesToSkip = bytestoskip

        # Read file one byte at a time, extract the two
        # IQ pairs, and store in array, after conversion to float.
        # Will initially read enough samples for ~20 ms of data
        Ts = 1/fs # Sampling Period [s]
        SampleLength = seconds # Sample length in 1ms multiples
        StartingByte = self.bytesToSkip # Can change this if we want to discard initial samples
        TotalSamples = int(np.ceil(SampleLength/Ts))
        self.Nsamples = TotalSamples
        TotalBytes = int(np.ceil(TotalSamples/2))
        print("Total Samples to read: %d"%(TotalSamples))
        print("Total Bytes read: %d." %(TotalBytes))
        print("Which equals %d IQ pairs." %(TotalBytes*2))
        print("Sample Length: %f seconds." %(TotalBytes*2*Ts))

        i = 0
        # Go to requested starting position
        fHandle.seek(StartingByte)

        # Read a single byte to get started
        SingleByte = fHandle.read(1)
        if realOnly: # If only processing and returning the IData
            self.IData = []
        else:
            self.IData = []
            self.QData = []

        n = 0
        # Loop until reach EOF (will also break of exceeds requested size)
        while SingleByte != "":
            I1, I2, Q1, Q2 = self._byteToIQPairs(ord(SingleByte))
            if realOnly:
                self.IData.extend((I1, I2))
            else:
                self.IData.extend((I1, I2))
                self.QData.extend((Q1, Q2))
            i += 1 # Increment current position
            if (i >= TotalBytes):
                break # Stop reading bytes if will exceed requested amount of samples
            SingleByte = fHandle.read(1)
            
            pct = (n/TotalBytes)*100
            if(pct % 1 == 0):
                print("%2.0f percent read"%pct, end = '\r')
            n += 1


        fHandle.close()
        print()
        print("File Loaded")

        if realOnly == False:
            self._complexData()
        self._timeVector(self.bytesToSkip, Ts, seconds)

    def ComplexToReal(self,CData):
        '''
        This algorithm was taken from "Fundamentals of Global Positioning
        System Receivers: A Software Approach" by James Bao-Yen Tsui, section 6.14.
        Consider rewriting in Rust and moving to file directory
        '''

        # Step 1: Take DFT of complex data
        CDataFFT = np.fft.fft(CData)

        # Step 2: Shift current frequency components
        N = len(CDataFFT)
        # Because of step 3, length of new List must be 2N
        X1 = np.zeros(N*2, dtype=np.complex)
        for k in range(0,N-1):
            if (k < N/2):
                X1[k]=CDataFFT[int(N/2 + k)]
            else:
                X1[k]=CDataFFT[int(-N/2 + k)]

        # Step 3: Generate complex conjugate of spectrum
        X1[N] = 0
        for k in range(1,N-1):
            X1[int(N + k)] = np.conjugate(X1[int(N-k)])

        # Step 4: Use iFFT to get converted time-domain data
        x1 = np.fft.ifft(X1)
        RealData = x1.real
        tReal = np.linspace(self.tStart, self.tEnd, self.Nsamples*2)
        return (tReal, RealData)