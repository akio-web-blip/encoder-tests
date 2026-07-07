import csv
from datetime import datetime

import matplotlib.pyplot as plt

from variables import OUTPUT_CSV, OUTPUT_DIR, PLOT_FILENAME

CSV_HEADER = [
    "timestamp",
    "step",
    "commanded_theta_deg",
    "measured_angle_1_deg",
    "measured_angle_2_deg",
    "diff_1_minus_2_deg",
]


def timestamp():
    return datetime.now().isoformat(timespec="seconds")


def prepare_output_folder():
    OUTPUT_DIR.mkdir(exist_ok=True)


def open_results_csv():
    csv_needs_header = not OUTPUT_CSV.exists() or OUTPUT_CSV.stat().st_size == 0
    csv_file = open(OUTPUT_CSV, "a", newline="")
    writer = csv.writer(csv_file)

    if csv_needs_header:
        writer.writerow(CSV_HEADER)
        csv_file.flush()

    return csv_file, writer


def write_result(writer, csv_file, plot_theta, plot_diff, step, commanded, measured1, measured2):
    diff = (measured1 - measured2) if (measured1 is not None and measured2 is not None) else ""
    writer.writerow([timestamp(), step, commanded, measured1, measured2, diff])
    csv_file.flush()

    if diff != "":
        plot_theta.append(measured1)
        plot_diff.append(diff)


def save_difference_plot(plot_theta, plot_diff):
    plt.figure()
    plt.plot(plot_theta, plot_diff, marker="o")
    plt.xlabel("Encoder 1 (deg)")
    plt.ylabel("Encoder 1 - Encoder 2 (deg)")
    plt.title("Encoder 1 vs Encoder 2 Difference")
    plt.grid(True)
    plt.savefig(PLOT_FILENAME)
    print(f"Plot saved to {PLOT_FILENAME}")
    plt.show()
