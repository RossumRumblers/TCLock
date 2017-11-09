import re
import USB
import evdev
import time
import threading

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Need root priviledges.")
    exit(1)

# VID and PID of the USB Device
ids = ["c216","0180"]

#Regex used to search ASU ID's
cardRegex = r";601744(\d{10})\d(\d{10})\?"
#Regex used to search USB Physical Addresses
usbRegex = r"usb-.+-(\d\.\d)\/input0"

###TODO###
# This info needs to be updated for the PI
# namely the Physical Port information and
# the GPIO Stuff
portDevices = [
    {
        "name": "port1",
        "port": "1.2",
        "GPIO": 0,
    },
    {
        "name": "port2",
        "port": "1.1",
        "GPIO": 0,
    }
]

###TODO###
#Find a better way to do this
#maybe a stored CSV or JSON
authorizedUsers = [
    "1207467036"
]

def runUSB(port, reader):
    print("starting", port['name'])
    reader.grabDevice()
    while True:
        Id = reader.extractID(reader.interpretEvents(reader.readData()), cardRegex)
        if Id in authorizedUsers:
            openLock(port['GPIO'])
    reader.ungrabDevice()

def initGPIO():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup([port['GPIO'] for port in portDevices], GPIO.OUT, initial=0)


#making initial assumtions about what the lock interface will be
def openLock(pin):
    GPIO.output(pin, 1)
    time.sleep(5)
    GPIO.output(pin, 0)

if __name__ == "__main__":
    #get all USB Devices in an iterable List
    for device in [evdev.InputDevice(fn) for fn in evdev.list_devices()]:
        #filter the ones with a particular VID and PID
        if hex(device.info.vendor)[2:].zfill(4) == ids[0] and \
           hex(device.info.product)[2:].zfill(4) == ids[1]:
            # Use regex to extract bus and port info
            deviceBus = re.search(re.compile(usbRegex), device.phys).group(1)
            for portObj in portDevices:
                #if the busport info match one of the expected devices, spin up a handler thread
                if portObj['port'] == deviceBus:
                    #we don't save the the thread object here because we never need to touch it after creating it
                    threading.Thread(target=runUSB, args=(portObj, USB.Reader(device))).start()
