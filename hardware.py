import re
import time

import serial

from variables import DPE_ADDRESS, DPE_BAUD, DPE_PORT, ND1_PORT, ND2_PORT, ND_BAUD


def open_serial_connections():
    dpe = serial.Serial(DPE_PORT, baudrate=DPE_BAUD, timeout=2, xonxoff=True)
    nd1 = serial.Serial(ND1_PORT, baudrate=ND_BAUD, timeout=2)
    nd2 = serial.Serial(ND2_PORT, baudrate=ND_BAUD, timeout=2)
    return dpe, nd1, nd2


def close_serial_connections(*ports):
    for port in ports:
        if port is not None and port.is_open:
            port.close()


def dpe_send(dpe, command):
    full_cmd = f"@{DPE_ADDRESS}{command}\r".encode("ascii")
    dpe.write(full_cmd)


def setup_dpe(dpe):
    dpe_send(dpe, "A1000")   # acceleration
    dpe_send(dpe, "B5000")   # base speed
    dpe_send(dpe, "M10000")  # max speed
    dpe_send(dpe, "-")       # direction: ccw
    time.sleep(0.2)


def move_dpe(dpe, steps_per_move):
    dpe_send(dpe, f"N{steps_per_move}") #increment motor
    dpe_send(dpe, "G")


def read_nd287_angle(nd):
    #return currently displayed angle as a float
    nd.reset_input_buffer()
    nd.write(b"\x1bA0100\r")
    time.sleep(0.1)
    raw = nd.read(50)
    text = raw.decode("ascii", errors="ignore")
    match = re.search(r"[-+]?\d*\.?\d+", text) #finds the number in text
    if match:
        return float(match.group())
    return None
