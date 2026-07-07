import csv
from datetime import datetime

import matplotlib.pyplot as plt

from variables import OUTPUT_CSV_PREFIX, OUTPUT_DIR, PLOT_FILENAME_PREFIX

CSV_HEADER = [
    "timestamp",
    "step",
    "commanded_theta_deg",
    "raw_encoder_1_deg",
    "raw_encoder_2_deg",
    "measured_angle_1_deg",
    "measured_angle_2_deg",
    "diff_1_minus_2_deg",
    "diff_2_minus_1_deg",
    "unoffset_encoder_1_deg",
    "unoffset_encoder_2_deg",
    "raw_diff_1_minus_2_deg",
    "raw_diff_2_minus_1_deg",
]


def timestamp():
    return datetime.now().isoformat(timespec="seconds")


def filename_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def prepare_output_folder():
    OUTPUT_DIR.mkdir(exist_ok=True)


def make_run_output_paths():
    run_stamp = filename_timestamp()
    csv_path = OUTPUT_DIR / f"{OUTPUT_CSV_PREFIX}_{run_stamp}.csv"
    plot_path = OUTPUT_DIR / f"{PLOT_FILENAME_PREFIX}_{run_stamp}.png"
    return csv_path, plot_path


def open_results_csv(csv_path):
    csv_needs_header = not csv_path.exists() or csv_path.stat().st_size == 0
    csv_file = open(csv_path, "a", newline="")
    writer = csv.writer(csv_file)

    if csv_needs_header:
        writer.writerow(CSV_HEADER)
        csv_file.flush()

    return csv_file, writer


def write_result(writer, csv_file, plot_theta, plot_diff, step, commanded, raw1, raw2, measured1, measured2):
    diff_1_minus_2 = (measured1 - measured2) if (measured1 is not None and measured2 is not None) else ""
    diff_2_minus_1 = (measured2 - measured1) if (measured1 is not None and measured2 is not None) else ""
    raw_diff_1_minus_2 = (raw1 - raw2) if (raw1 is not None and raw2 is not None) else ""
    raw_diff_2_minus_1 = (raw2 - raw1) if (raw1 is not None and raw2 is not None) else ""
    writer.writerow([
        timestamp(),
        step,
        commanded,
        raw1,
        raw2,
        measured1,
        measured2,
        diff_1_minus_2,
        diff_2_minus_1,
        raw1,
        raw2,
        raw_diff_1_minus_2,
        raw_diff_2_minus_1,
    ])
    csv_file.flush()

    if diff_1_minus_2 != "":
        plot_theta.append(measured1)
        plot_diff.append(diff_1_minus_2)


def save_difference_plot(plot_theta, plot_diff, plot_path):
    plt.figure(figsize=(9, 6))
    plt.plot(plot_theta, plot_diff, marker="o")
    plt.xlabel("Encoder 1 (deg)")
    plt.ylabel("Encoder 1 - Encoder 2 (deg)")
    plt.title("Encoder 1 vs Encoder 2 Difference")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plot_path, bbox_inches="tight")
    print(f"Plot saved to {plot_path}")
    plt.show()
