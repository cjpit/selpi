# Originally authored by Justin Stafford
import serial, threading, time, struct, hashlib, urllib, httplib

sp_pro_baud_rate = 57600 # Options: 57600 115200 9600 2400 1200 4800 19200 38400
sp_pro_port = "/dev/ttyUSB1"
sp_pro_password = "Selectronic SP PRO"

pvo_key = "YOURKEY"
pvo_systemid = "YOURID"  # Your PVoutput system ID here
pvo_statusInterval = 5  # Your PVoutput status interval - normally 5, 10 (default) or 15

pvo_host = "pvoutput.org"
pvo_statusuri = "/service/r2/addstatus.jsp"
pvo_outputuri = "/service/r2/addoutput.jsp"

commonScaleForACVolts = 0
commonScaleForACCurrent = 0
commonScaleForDcVolts = 0
commonScaleForDCCurrent = 0
commonScaleForTemperature = 0

timeReading = time.localtime()
lastStatus = time.localtime()

solarPower = 0
solarEnergy = 0
loadPower = 0
loadEnergy = 0
batteryVolts = 0
dcBatteryPower = 0

solarPowerSum = 0
solarPowerReadings = 0
solarPowerAvg = 0
loadPowerSum = 0
loadPowerReadings = 0
loadPowerAvg = 0
dcBatteryPowerSum = 0
dcBatteryPowerReadings = 0
dcBatteryPowerAvg = 0

# Initialise USB port
SPPort = serial.Serial(sp_pro_port, baudrate=sp_pro_baud_rate, timeout=0.5)
SPPort.flushOutput()

FCSLookUpTable = [0, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf, 0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
    0x1081, 0x108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e, 0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876,
    0x2102, 0x308b, 0x210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd, 0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
    0x3183, 0x200a, 0x1291, 0x318, 0x77a7, 0x662e, 0x54b5, 0x453c, 0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974,
    0x4204, 0x538d, 0x6116, 0x709f, 0x420, 0x15a9, 0x2732, 0x36bb, 0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3,
    0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x528, 0x37b3, 0x263a, 0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
    0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x630, 0x17b9, 0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1,
    0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x738, 0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
    0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7, 0x840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
    0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036, 0x18c1, 0x948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e,
    0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5, 0x2942, 0x38cb, 0xa50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd,
    0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134, 0x39c3, 0x284a, 0x1ad1, 0xb58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
    0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3, 0x4a44, 0x5bcd, 0x6956, 0x78df, 0xc60, 0x1de9, 0x2f72, 0x3efb,
    0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232, 0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0xd68, 0x3ff3, 0x2e7a,
    0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1, 0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0xe70, 0x1ff9,
    0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330, 0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0xf78]

def calculateCRCI(msg):
    n = 0
    for i in xrange(0, len(msg)):
        n = (n >> 8) ^ FCSLookUpTable[(n ^ msg[i]) & 0xff]
    return n

def calculateCRC(msg):
    n = calculateCRCI(msg)
    return struct.pack("<I", n)[:2]

def getReadRequest(address, length):
    m = bytearray(["Q", length])
    m.extend(struct.pack("<I", address))
    m.extend(calculateCRC(m))
    return m

def getWriteRequest(address, data):
    m = bytearray(["W", len(data)-1])
    m.extend(struct.pack("<I", address))
    m.extend(calculateCRC(m))

    # Convert data from int[] to byte[], little endian but reversing the byte order (thanks Selectronic :( )
    ba = bytearray()
    for x in data:
        bb = bytearray(struct.pack("<I", x)[0:2])
        bb.reverse()
        ba.extend(bb)

    m.extend(ba)
    m.extend(calculateCRC(ba))
    return m

def doReadRequest(address, length):
    r = getReadRequest(address, length)
    SPPort.write(r)
    SPPort.flushOutput()
    responseBuffer = bytearray()
    expectedResponseLength = 2 * (length + 1) + 10
    for i in xrange(1, expectedResponseLength + 10): # Allow for a few timeouts @ 0.5s
        responseBuffer.extend(SPPort.read())
        if len(responseBuffer) == expectedResponseLength:
            break
    if calculateCRCI(responseBuffer) != 0:
        responseBuffer = bytearray()
    return responseBuffer # If it fails and just times out, will be empty (or if it fails CRC)

def login():

    # Get hash from SP Pro
    h = doReadRequest(0x1f0000, 7)[8:24]

    # Compute MD5 hash to send back, including login password
    h.extend(sp_pro_password.ljust(32).encode("ascii"))

    # Compute md5
    md5 = bytearray(hashlib.md5(h).digest())

    # Convert md5 to little endian int32 array
    md5ia = []
    for i in xrange(0, len(md5), 2):
        md5ia.extend(struct.unpack("<I", bytes(md5[i:i+2] + bytearray([0, 0]))))

    # Respond with hash/pwd MD5
    r = getWriteRequest(0x1f0000, md5ia)
    SPPort.write(r)
    responseBuffer = bytearray()
    for i in xrange(1, 52):
        responseBuffer.extend(SPPort.read())
        if len(responseBuffer) == 26:
            return True

    return False

def resetAverages():

    global solarPowerSum, solarPowerReadings, solarPowerAvg, loadPowerSum, loadPowerReadings, loadPowerAvg, dcBatteryPowerSum, dcBatteryPowerReadings, dcBatteryPowerAvg
    solarPowerSum = 0
    solarPowerReadings = 0
    solarPowerAvg = 0
    loadPowerSum = 0
    loadPowerReadings = 0
    loadPowerAvg = 0
    dcBatteryPowerSum = 0
    dcBatteryPowerReadings = 0
    dcBatteryPowerAvg = 0

def post(uri, params):
    try:
        headers = {'X-Pvoutput-Apikey': pvo_key,
                   'X-Pvoutput-SystemId': pvo_systemid,
                   "Accept": "text/plain",
                   "Content-type": "application/x-www-form-urlencoded"}
        conn = httplib.HTTPConnection(pvo_host)
        #        conn.set_debuglevel(2) # debug purposes only
        conn.request("POST", uri, urllib.urlencode(params), headers)
        response = conn.getresponse()
        print("Status", response.status, "   Reason:", response.reason, "-", response.read())
        conn.close()
        return response.status == 200
    except Exception as e:
        print("Exception posting results\n", e)
        return False

def postPVstatus():
    params = {'d': time.strftime('%Y%m%d', timeReading),
              't': time.strftime('%H:%M', timeReading),
              'v1': int(solarEnergy),
              'v2': int(solarPowerAvg),
              'v3': int(loadEnergy),
              'v4': int(loadPowerAvg),
              #'v6': "{0:.2f}".format(batteryVolts),
              #'v8': int(dcBatteryPower),
              'c1': 1,
              'n': 0}

    print("Params:", params)
    # POST the data
    return post(pvo_statusuri, params)

# SPReader thread will loop gathering data from the SPPro into the global variables
class SPReader (threading.Thread):

    def run(self):

        login()

        while True:

            global timeReading, lastStatus
            timeReading = time.localtime()

            # Common scales
            rb = doReadRequest(0xa028, 7)
            if len(rb) == 0:
                login()
                continue
            global commonScaleForACVolts, commonScaleForACCurrent, commonScaleForDcVolts, commonScaleForDCCurrent, commonScaleForTemperature
            commonScaleForACVolts = struct.unpack("<I", bytes(rb[8:10] + bytearray([0, 0])))[0]
            commonScaleForACCurrent = struct.unpack("<I", bytes(rb[10:12] + bytearray([0, 0])))[0]
            commonScaleForDcVolts = struct.unpack("<I", bytes(rb[12:14] + bytearray([0, 0])))[0]
            commonScaleForDCCurrent = struct.unpack("<I", bytes(rb[14:16] + bytearray([0, 0])))[0]
            commonScaleForTemperature = struct.unpack("<I", bytes(rb[16:18] + bytearray([0, 0])))[0]

            global solarPower, solarEnergy, loadPower, loadEnergy, solarPowerSum, solarPowerReadings, solarPowerAvg, loadPowerSum, loadPowerReadings, loadPowerAvg, batteryVolts, dcBatteryPower, dcBatteryPowerSum, dcBatteryPowerReadings, dcBatteryPowerAvg

            # Solar Power - CombinedKacoAcPowerHiRes
            rb = doReadRequest(0xa3a8, 3)
            if len(rb) == 0: continue
            solarPower = struct.unpack("<I", bytes(rb[8:12]))[0]
            solarPower = solarPower * commonScaleForACVolts * commonScaleForACCurrent / 26214400.0
            solarPowerSum += solarPower
            solarPowerReadings += 1
            solarPowerAvg = solarPowerSum / solarPowerReadings

            # Solar Energy - ACSolarKacokWhTotalAcc
            rb = doReadRequest(0xa22f, 3)
            if len(rb) == 0: continue
            solarEnergy = struct.unpack("<I", bytes(rb[8:12]))[0]
            solarEnergy = solarEnergy * 24 * commonScaleForACVolts * commonScaleForACCurrent / 3276800.0

            # Load Power - LoadAcPower
            rb = doReadRequest(0xa093, 3)
            if len(rb) == 0: continue
            loadPower = struct.unpack("<i", bytes(rb[8:12]))[0]
            loadPower = loadPower * commonScaleForACVolts * commonScaleForACCurrent / 26214400.0
            loadPowerSum += loadPower
            loadPowerReadings += 1
            loadPowerAvg = loadPowerSum / loadPowerReadings

            # Load Energy - ACLoadkWhTotalAcc
            rb = doReadRequest(0xa1de, 3)
            if len(rb) == 0: continue
            loadEnergy = struct.unpack("<I", bytes(rb[8:12]))[0]
            loadEnergy = loadEnergy * 24 * commonScaleForACVolts * commonScaleForACCurrent / 3276800.0

            # Battery Volts - BatteryVolts
            rb = doReadRequest(0xa05c, 1)
            if len(rb) == 0: continue
            batteryVolts = struct.unpack("<I", bytes(rb[8:10] + bytearray([0, 0])))[0]
            batteryVolts = batteryVolts * commonScaleForDcVolts / 327680.0

            # Battery Power - DCBatteryPower
            rb = doReadRequest(0xa02f, 3)
            if len(rb) == 0: continue
            dcBatteryPower = struct.unpack("<i", bytes(rb[8:12]))[0]
            dcBatteryPower = dcBatteryPower * commonScaleForDcVolts * commonScaleForDCCurrent / 3276800.0
            dcBatteryPowerSum += dcBatteryPower
            dcBatteryPowerReadings += 1
            dcBatteryPowerAvg = dcBatteryPowerSum / dcBatteryPowerReadings

            # Post Status data to PV Output at set intervals
            if (timeReading.tm_min % pvo_statusInterval == 0) & (lastStatus.tm_min != timeReading.tm_min):
                if postPVstatus():
                    lastStatus = timeReading
                    resetAverages()

            time.sleep(1)

# Start threads
sr = SPReader()
sr.start()


print "Exiting main thread"


