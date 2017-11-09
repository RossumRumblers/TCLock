import re
import USB
import evdev
import threading

ids = ["c216","0180"]
cardRegex = r";601744(\d{10})\d(\d{10})\?"
usbRegex = r"usb-.+-(\d\.\d)\/input0"

portDevices = [
    {
        "name": "port1",
        "port": "1.2",
        "GPIO": [0,0],
    },
    {
        "name": "port2",
        "port": "1.1",
        "GPIO": [0,0],
    }
]

def runUSB(port, reader):
    print("starting", port)
    reader.grabDevice()
    while True:
        Id = reader.extractID(reader.interpretEvents(reader.readData()), cardRegex)
        print(port, Id)
    reader.ungrabDevice()


if __name__ == "__main__":
    for device in [evdev.InputDevice(fn) for fn in evdev.list_devices()]:
        if hex(device.info.vendor)[2:].zfill(4) == ids[0] and \
           hex(device.info.product)[2:].zfill(4) == ids[1]:
            print(device.phys)
            deviceBus = re.search(re.compile(usbRegex), device.phys).group(1)
            for portObj in portDevices:
                if portObj['port'] == deviceBus:
                    print("starting Thread")
                    threading.Thread(target=runUSB, args=(portObj['name'], USB.Reader(device))).start()
