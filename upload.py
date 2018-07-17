#!/usr/bin/env python

import serial, time, sys

SERIALPORT = sys.argv[1]
BAUDRATE = 9600

ser = serial.Serial(SERIALPORT, BAUDRATE)
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.timeout = None
ser.xonxoff = False
ser.rtscts = False
ser.dsrdtr = False
ser.writeTimeout = 0

if(ser.isOpen() == False):
    try:
        ser.open()
    except Exception, e:
        print "error opening serial port: " + str(e)
        exit()

if ser.isOpen():
    try:
        ser.flushInput()
        ser.flushOutput()
        
        time.sleep(0.5)
        numberOfLine = 0

        while True:
            if ser.inWaiting():
                response = ser.readline()
                print response[:-1]
                if "run?" in response:
                    ser.write("1")
                    print "1"
                if "Program" in response:
                    with open(sys.argv[2], "r") as f:
                        fileBytes = f.read()
                        print "Programming... (%d bytes)" % len(fileBytes)
                        for byte in fileBytes:
                            ser.write(byte)
                            sys.stdout.write("#")
                            sys.stdout.flush()
                            time.sleep(0.01)
                        f.close()
                        sys.stdout.write("\n")
                        sys.stdout.flush()
                    print "Padding empty bytes..."
                    while not ser.inWaiting():
                        ser.write(30)
                        time.sleep(0.01)
                    print "Done."
        
        ser.close()
    except Exception, e:
        print "error communicating: " + str(e)
else:
    print "cannot open serial port "
