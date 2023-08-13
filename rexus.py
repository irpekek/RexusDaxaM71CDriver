import usb.core
import usb.util
import os
import time
import json


class Driver(object):
    def __init__(self):
        self.VENDOR_ID = 0x05AC
        self.PRODUCT_ID = 0x024F
        self.WRITE_REQ_TYPE = 0x21  # Write bmRequestType
        self.WRITE_REQ = 0x09  # Write bRequest
        self.WRITE_VALUE = 0x0300  # Write wValue
        self.WRITE_IDX = 0x0000  # Write wIndex
        self.READ_REQ_TYPE = 0xA1  # Read bmRequestType
        self.READ_REQ = 0x01  # Read bRequest
        self.READ_VALUE = 0x0300  # Read wValue
        self.READ_IDX = 0x00  # Read wIndex
        self.READ_LEN = 64  # Read Length
        # Name, Byte, Colorful, RGB, Direction, Speed
        self.LIGHT_MODE = {
            1: ["Static", 0x01, True, True, "None", False],
            2: ["SingleOn", 0x02, True, True, "None", True],
            3: ["SingleOff", 0x03, True, True, "None", True],
            4: ["Glittering", 0x04, True, True, "None", True],
            5: ["Falling", 0x05, True, True, "None", True],
            6: ["Colorful", 0x06, True, False, "None", True],
            7: ["Breath", 0x07, True, True, "None", True],
            8: ["Spectrum", 0x08, False, False, "None", True],
            9: ["Outward", 0x09, True, True, "None", True],
            10: ["Scrolling", 0x0A, True, True, "UD", True],
            11: ["Rolling", 0x0B, True, True, "LR", True],
            12: ["Rotating", 0x0C, True, True, "None", True],
            13: ["Explode", 0x0D, True, True, "None", True],
            14: ["Launch", 0x0E, True, True, "None", True],
            15: ["Ripples", 0x0F, True, True, "None", True],
            16: ["Flowing", 0x10, True, True, "LR", True],
            17: ["Pulsating", 0x11, True, True, "None", True],
            18: ["Tilt", 0x12, True, True, "LR", True],
            19: ["Shuttle", 0x13, True, True, "None", True],
        }
        # Red, Green, Blue
        self.COLOR = {
            "red": [0xFF, 0x00, 0x00],
            "orange": [0xFF, 0xA5, 0x00],
            "yellow": [0xFF, 0xFF, 0x00],
            "green": [0x00, 0xFF, 0x00],
            "blue": [0x00, 0x00, 0xFF],
            "indigo": [0x4B, 0x00, 0x82],
            "violet": [0x80, 0x00, 0xFF],
            "cyan": [0x00, 0xFF, 0xFF],
        }
        self.wrapper = [0x04, 0x02]
        self.no_light = [0x04, 0xAB]
        self.header = [0x04, 0x13]
        self.footer = [0x04, 0xF0]

        self.device_busy = bool()
        self.conquered = False
        self.buffer_light = []
        self.buffer = []

        self.addzerobytes(self.wrapper, 62)
        self.addzerobytes(self.no_light, 62)
        self.addzerobytes(self.footer, 62)
        self.addzerobytes(self.header, 62)
        self.addzerobytes(self.buffer, 64)
        self.header[8] = 0x12

    def save_config(self, data):
        with open("rexus_config.json", "w") as fp:
            json.dump(data, fp)

    def load_config(self):
        with open("rexus_config.json", "rb") as fp:
            data = json.load(fp)
            return data

    def find_device(self):
        print("Trying to find device...")
        self.rexus = usb.core.find(idVendor=self.VENDOR_ID, idProduct=self.PRODUCT_ID)

    def initPayload(self, instruction_code):
        payload = [0x04]
        payload.append(instruction_code)
        return payload

    def device_state(self):
        try:
            self.device_busy = self.rexus.is_kernel_driver_active(self.WRITE_IDX)
        except usb.core.USBError as exception:
            print(exception.strerror)
            if exception.errno == 13:
                # usb.backend.libusb1.LIBUSB_ERROR_ACCESS as e
                print(
                    "Try adding a udev rule for your rexus, follow the guide here https://wiki.archlinux.org/index.php/udev#Accessing_firmware_programmers_and_USB_virtual_comm_devicesrunning. Running as root will probably work too but not recommended"
                )
            return -1
        except AttributeError:
            print("Device not found. Try replugging")
            return -2
        print("Device is ready to be configured")
        return 1

    def set_color(self):
        self.buffer_light = self.load_config()

        light_mode = self.buffer_light[0]
        self.buffer_light[8] = 0x00

        os.system("clear")
        if self.LIGHT_MODE[light_mode][3] == False:
            print("Your lightning mode does not support RGB color")
            self.buffer_light[8] = 0x01
            self.save_config(self.buffer_light)
            return 0

        print("==================================================")
        print("1.Colorful  2.Red     3.Orange  4.Yellow  5.Green")
        print("6.Blue      7.Indigo  8.Violet  9.Cyan   10.Custom")
        print("==================================================")
        try:
            color = int(input("Set Color (1-10): "))
        except ValueError:
            return self.set_color()

        if color < 1 or color > 10:
            return self.set_color()
        elif color == 1:
            self.buffer_light[8] = 0x01
        elif color == 2:
            self.buffer_light[1] = self.COLOR["red"][0]
            self.buffer_light[2] = self.COLOR["red"][1]
            self.buffer_light[3] = self.COLOR["red"][2]
        elif color == 3:
            self.buffer_light[1] = self.COLOR["orange"][0]
            self.buffer_light[2] = self.COLOR["orange"][1]
            self.buffer_light[3] = self.COLOR["orange"][2]
        elif color == 4:
            self.buffer_light[1] = self.COLOR["yellow"][0]
            self.buffer_light[2] = self.COLOR["yellow"][1]
            self.buffer_light[3] = self.COLOR["yellow"][2]
        elif color == 5:
            self.buffer_light[1] = self.COLOR["green"][0]
            self.buffer_light[2] = self.COLOR["green"][1]
            self.buffer_light[3] = self.COLOR["green"][2]
        elif color == 6:
            self.buffer_light[1] = self.COLOR["blue"][0]
            self.buffer_light[2] = self.COLOR["blue"][1]
            self.buffer_light[3] = self.COLOR["blue"][2]
        elif color == 7:
            self.buffer_light[1] = self.COLOR["indigo"][0]
            self.buffer_light[2] = self.COLOR["indigo"][1]
            self.buffer_light[3] = self.COLOR["indigo"][2]
        elif color == 8:
            self.buffer_light[1] = self.COLOR["violet"][0]
            self.buffer_light[2] = self.COLOR["violet"][1]
            self.buffer_light[3] = self.COLOR["violet"][2]
        elif color == 9:
            self.buffer_light[1] = self.COLOR["cyan"][0]
            self.buffer_light[2] = self.COLOR["cyan"][1]
            self.buffer_light[3] = self.COLOR["cyan"][2]
        elif color == 10:
            return self.set_color_rgb()

        self.save_config(self.buffer_light)

    def set_color_rgb(self):
        self.buffer_light = self.load_config()
        print("Input color in RGB (eg: 255 255 255): ")
        try:
            red = int(input("Red: "))
            green = int(input("Green: "))
            blue = int(input("Blue: "))
        except ValueError:
            return self.set_color_rgb

        if red > 255 or green > 255 or blue > 255 or red < 0 or green < 0 or blue < 0:
            return self.set_color_rgb
        else:
            self.buffer_light[1] = red
            self.buffer_light[2] = green
            self.buffer_light[3] = blue

        self.save_config(self.buffer_light)

    def set_color_direction(self):
        self.buffer_light = self.load_config()

        light_mode = self.buffer_light[0]

        os.system("clear")
        if self.LIGHT_MODE[self.buffer_light[0]][4] == "None":
            print("Your lightning mode does not support color direction")
        elif self.LIGHT_MODE[self.buffer_light[0]][4] == "UD":
            try:
                direction = int(input("1. Upward or 2. Downward: "))
            except ValueError:
                return self.set_color_direction()

            if direction == 1:
                self.buffer_light[11] = 0x02
            elif direction == 2:
                self.buffer_light[11] = 0x03
            else:
                return self.set_color_direction()

        elif self.LIGHT_MODE[self.buffer_light[0]][4] == "LR":
            try:
                direction = int(input("1. Leftward or 2. Rightward: "))
            except ValueError:
                return self.set_color_direction()

            if direction == 1:
                self.buffer_light[11] = 0x01
            elif direction == 2:
                self.buffer_light[11] = 0x00
            else:
                return self.set_color_direction()

        self.save_config(self.buffer_light)

    def set_color_speed(self):
        self.buffer_light = self.load_config()

        light_mode = self.buffer_light[0]

        os.system("clear")
        if self.LIGHT_MODE[self.buffer_light[0]][5] == False:
            print("Your lightning mode does not support color speed")
        else:
            try:
                speed = int(input("Set Color Speed(1-16): "))
            except ValueError:
                return self.set_color_speed()

            if speed < 1 or speed > 16:
                return self.set_color_speed()

        self.buffer_light[10] = speed
        self.save_config(self.buffer_light)

    def set_color_brightness(self):
        self.buffer_light = self.load_config()

        light_mode = self.buffer_light[0]
        os.system("clear")
        try:
            brightness = int(input("Set Color Brightness(1-16): "))
        except ValueError:
            return self.set_color_brightness()

        if brightness < 1 or brightness > 16:
            return self.set_color_brightness()

        self.buffer_light[9] = brightness
        self.save_config(self.buffer_light)

    def set_lightning_mode(self):
        self.buffer_light = self.load_config()

        os.system("clear")
        print("===================================================================")
        print(" 1.Static    2.SingleOn   3.SingleOff  4.Glittering   5.Falling")
        print(" 6.Colorful  7.Breath     8.Spectrum   9.Outward     10.Scrolling")
        print("11.Rolling  12.Rotating  13.Explode   14.Launch      15.Ripples")
        print(
            "16.Flowing  17.Pulsating 18.Tilt      19.Shuttle     20.Custom(Not Ready)"
        )
        print("===================================================================")

        try:
            mode = int(input("Set Lightning Mode(1-20): "))
        except ValueError:
            return self.set_lightning_mode()

        if mode == 20:
            print("Not Yet")
            return self.set_lightning_mode()
        elif mode < 1 or mode > 20:
            return self.set_lightning_mode()

        if mode == 1:
            self.buffer_light[0] = self.LIGHT_MODE[1][1]
        elif mode == 2:
            self.buffer_light[0] = self.LIGHT_MODE[2][1]
        elif mode == 3:
            self.buffer_light[0] = self.LIGHT_MODE[3][1]
        elif mode == 4:
            self.buffer_light[0] = self.LIGHT_MODE[4][1]
        elif mode == 5:
            self.buffer_light[0] = self.LIGHT_MODE[5][1]
        elif mode == 6:
            self.buffer_light[0] = self.LIGHT_MODE[6][1]
        elif mode == 7:
            self.buffer_light[0] = self.LIGHT_MODE[7][1]
        elif mode == 8:
            self.buffer_light[0] = self.LIGHT_MODE[8][1]
        elif mode == 9:
            self.buffer_light[0] = self.LIGHT_MODE[9][1]
        elif mode == 10:
            self.buffer_light[0] = self.LIGHT_MODE[10][1]
        elif mode == 11:
            self.buffer_light[0] = self.LIGHT_MODE[11][1]
        elif mode == 12:
            self.buffer_light[0] = self.LIGHT_MODE[12][1]
        elif mode == 13:
            self.buffer_light[0] = self.LIGHT_MODE[13][1]
        elif mode == 14:
            self.buffer_light[0] = self.LIGHT_MODE[14][1]
        elif mode == 15:
            self.buffer_light[0] = self.LIGHT_MODE[15][1]
        elif mode == 16:
            self.buffer_light[0] = self.LIGHT_MODE[16][1]
        elif mode == 17:
            self.buffer_light[0] = self.LIGHT_MODE[17][1]
        elif mode == 18:
            self.buffer_light[0] = self.LIGHT_MODE[18][1]
        elif mode == 19:
            self.buffer_light[0] = self.LIGHT_MODE[19][1]

        if mode < 20:
            self.buffer_light[8] = (
                0x01 if self.LIGHT_MODE[mode][2] == True else 0x00
            )  # Colorful
            self.buffer_light[10] = (
                0x0E if self.LIGHT_MODE[mode][5] == True else 0x00
            )  # Speed
            self.buffer_light[11] = (
                0x02 if self.LIGHT_MODE[mode][4] == "UD" else 0x00
            )  # Direction

        self.save_config(self.buffer_light)

    def conquer(self):
        if self.device_busy and not self.conquered:
            self.rexus.detach_kernel_driver(self.WRITE_IDX)
            usb.util.claim_interface(self.rexus, self.WRITE_IDX)
            self.conquered = True

    def liberate(self):
        self.conquered
        if self.conquered:
            try:
                usb.util.release_interface(self.rexus, self.WRITE_IDX)
                self.rexus.attach_kernel_driver(self.WRITE_IDX)
                self.conquered = False
            except:
                print("Failed to release device back to kernel")

    def addzerobytes(self, list, number_of_bytes):
        for i in range(number_of_bytes):
            list.append(0x00)

    def send_write_payload(self, payload):
        self.rexus.ctrl_transfer(
            self.WRITE_REQ_TYPE,
            self.WRITE_REQ,
            self.WRITE_VALUE,
            self.WRITE_IDX,
            payload,
        )

    def send_read_payload(self):
        self.rexus.ctrl_transfer(
            self.READ_REQ_TYPE,
            self.READ_REQ,
            self.READ_VALUE,
            self.READ_IDX,
            self.READ_LEN,
        )

def send_to_device(driver):
    driver.conquer()
    driver.send_write_payload(driver.no_light)
    driver.send_read_payload()
    driver.send_write_payload(driver.wrapper)
    driver.send_read_payload()
    driver.send_write_payload(driver.header)
    driver.send_read_payload()
    for i in range(17):
        driver.send_write_payload(driver.buffer)
    driver.send_write_payload(driver.buffer_light)
    driver.send_write_payload(driver.wrapper)
    driver.send_read_payload()
    driver.send_write_payload(driver.footer)
    driver.liberate()

def main():
    driver = Driver()
    time.sleep(1)
    driver.find_device()
    driver.device_state()
    time.sleep(1)
    os.system("clear")
    print("=====================")
    print("Rexus Light Control")
    print("1. Lightning Mode")
    print("2. Color")
    print("3. Direction")
    print("4. Speed")
    print("5. Brightness")
    print("0. exit")
    print("=====================")
    try:
        choose = int(input("Input number: "))
    except ValueError:
        return main

    if choose > 5 or choose < 0:
        return main()
    elif choose == 1:
        driver.set_lightning_mode()
        send_to_device(driver)
        return main()
    elif choose == 2:
        driver.set_color()
        send_to_device(driver)
        return main()
    elif choose == 3:
        driver.set_color_direction()
        send_to_device(driver)
        return main()
    elif choose == 4:
        driver.set_color_speed()
        send_to_device(driver)
        return main()
    elif choose == 5:
        driver.set_color_brightness()
        send_to_device(driver)
        return main()
    elif choose == 0:
        return 0

if __name__ == "__main__":
    main()
