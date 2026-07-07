from pathlib import Path

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
OUTPUT_DIR = Path("output")
OUTPUT_CSV = OUTPUT_DIR / "encoder_data.csv"
PLOT_FILENAME = OUTPUT_DIR / "encoder_diff_plot.png"