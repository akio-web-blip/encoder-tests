import serial
import time
import re
import csv
import matplotlib.pyplot as plt

#port assignment
DPE_PORT = "COM5"
DPE_BAUD = 38400
DPE_ADDRESS = 0
ND1_PORT = "COM3"
ND2_PORT = "COM6"
ND_BAUD = 115200

STEPS_PER_REV = 143000 #need to find out how much this actually is
NUM_MOVES = 360
STEPS_PER_MOVE = STEPS_PER_REV // NUM_MOVES
DEGREES_PER_MOVE = 360 / NUM_MOVES            
MOVE_SETTLE_TIME = 0.5          #wait a bit before reading encoder
DIRECTION_1 = -1
DIRECTION_2 = 1
OUTPUT_CSV = "encoder_data.csv"

#open connections
dpe = serial.Serial(DPE_PORT, baudrate=DPE_BAUD, timeout=2, xonxoff=True)
nd1 = serial.Serial(ND1_PORT, baudrate=ND_BAUD, timeout=2)
nd2 = serial.Serial(ND2_PORT, baudrate=ND_BAUD, timeout=2)

def dpe_send(command):
    full_cmd = f"@{DPE_ADDRESS}{command}\r".encode("ascii")
    dpe.write(full_cmd)
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

#DPE25601 setup
dpe_send("A1000")   # acceleration
dpe_send("B5000")    # base speed
dpe_send("M10000")   # max speed
dpe_send("-")       # direction: ccw
time.sleep(0.2)

results = []

#get initial readings
offset1 = read_nd287_angle(nd1)
offset2 = read_nd287_angle(nd2)
print(f"Initial reading (ND1): {offset1} deg")
print(f"Initial reading (ND2): {offset2} deg\n")

print(f"Step 0/{NUM_MOVES}  Commanded:    0.0 deg   Measured1: 0.0   Measured2: 0.0")
results.append((0, 0.0, 0.0, 0.0))

#track last raw reading and running total for each encoder, so measured angle counts past 360
last_raw1 = offset1
last_raw2 = offset2
unwrapped1 = 0.0
unwrapped2 = 0.0

for i in range(NUM_MOVES):
    commanded_theta = (i+1) * DEGREES_PER_MOVE
 
    dpe_send(f"N{STEPS_PER_MOVE}") #increment motor
    dpe_send("G")
 
    time.sleep(MOVE_SETTLE_TIME)
 
    raw_measured1 = read_nd287_angle(nd1)
    raw_measured2 = read_nd287_angle(nd2)
 
    if raw_measured1 is not None:
        delta1 = raw_measured1 - last_raw1
        if delta1 > 180:
            delta1 -= 360
        elif delta1 < -180:
            delta1 += 360
        unwrapped1 += delta1 * DIRECTION_1
        last_raw1 = raw_measured1
        measured_angle1 = unwrapped1
    else:
        measured_angle1 = None

    if raw_measured2 is not None:
        delta2 = raw_measured2 - last_raw2
        if delta2 > 180:
            delta2 -= 360
        elif delta2 < -180:
            delta2 += 360
        unwrapped2 += delta2 * DIRECTION_2
        last_raw2 = raw_measured2
        measured_angle2 = unwrapped2
    else:
        measured_angle2 = None
 
    print(f"Step {i + 1}/{NUM_MOVES}  Commanded: {commanded_theta:6.1f} deg   Measured1: {measured_angle1}   Measured2: {measured_angle2}")
    results.append((i, commanded_theta, measured_angle1, measured_angle2))
    
#save results to CSV
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["step", "commanded_theta_deg", "measured_angle_1_deg", "measured_angle_2_deg", "diff_1_minus_2_deg"])
    for i, commanded, measured1, measured2 in results:
        diff = (measured1 - measured2) if (measured1 is not None and measured2 is not None) else ""
        writer.writerow([i, commanded, measured1, measured2, diff])
dpe.close()
nd1.close()
nd2.close()
print(f"\nDone. Results saved to {OUTPUT_CSV}")

#plot the difference between the two encoders vs commanded angle
plot_theta = []
plot_diff = []
for i, commanded, measured1, measured2 in results:
    if measured1 is not None and measured2 is not None:
        plot_theta.append(measured1)
        plot_diff.append(measured1 - measured2)

plt.figure()
plt.plot(plot_theta, plot_diff, marker="o")
plt.xlabel("Encoder 1 (deg)")
plt.ylabel("Encoder 1 - Encoder 2 (deg)")
plt.title("Encoder 1 vs Encoder 2 Difference")
plt.grid(True)

plot_filename = "encoder_diff_plot.png"
plt.savefig(plot_filename)
print(f"Plot saved to {plot_filename}")
plt.show()
