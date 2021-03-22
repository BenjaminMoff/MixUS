import serial.tools.list_ports
import serial


class ListUSB:
    @staticmethod
    def get_usb_devices():
        ports = []
        for p in list(serial.tools.list_ports.comports()):
            ports.append(list(p))

        com_port = []
        for port in ports:
            com_port.append(port[0])

        return com_port

    def findusbdevice(self):
        good_port = None
        ports = self.get_usb_devices()
        print(ports)
        for port in ports:
            ser = serial.Serial(port, 250000, 8, 'N', 1, timeout=1)
            message = ser.readline().decode(errors='replace')
            if message == "echo:  M907 X135 Y135 Z135 E135 135":
                good_port = port
                break
        return good_port


listusb = ListUSB()
print(listusb.findusbdevice())
