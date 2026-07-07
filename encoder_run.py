import time
from datetime import datetime

from hardware import (
    close_serial_connections,
    move_dpe,
    open_serial_connections,
    read_nd287_angle,
    setup_dpe,
)
from output_files import (
    open_results_csv,
    prepare_output_folder,
    save_difference_plot,
    write_result,
)
from variables import (
    DEGREES_PER_MOVE,
    DIRECTION_1,
    DIRECTION_2,
    MOVE_SETTLE_TIME,
    NUM_MOVES,
    OUTPUT_CSV,
    STEPS_PER_MOVE,
)


def unwrap_angle(raw_measured, last_raw, unwrapped, direction):
    if raw_measured is None:
        return None, last_raw, unwrapped
    if last_raw is None:
        return unwrapped, raw_measured, unwrapped

    delta = raw_measured - last_raw
    if delta > 180:
        delta -= 360
    elif delta < -180:
        delta += 360

    unwrapped += delta * direction
    return unwrapped, raw_measured, unwrapped


def run_encoder_test():
    run_start = datetime.now()
    timer_start = time.perf_counter()
    print(f"Run started: {run_start.isoformat(timespec='seconds')}")

    dpe = None
    nd1 = None
    nd2 = None
    csv_file = None

    try:
        prepare_output_folder()

        dpe, nd1, nd2 = open_serial_connections()
        setup_dpe(dpe)

        csv_file, writer = open_results_csv()
        plot_theta = []
        plot_diff = []

        offset1 = read_nd287_angle(nd1)
        offset2 = read_nd287_angle(nd2)
        print(f"Initial reading (ND1): {offset1} deg")
        print(f"Initial reading (ND2): {offset2} deg\n")

        print(f"Step 0/{NUM_MOVES}  Commanded:    0.0 deg   Measured1: 0.0   Measured2: 0.0")
        write_result(writer, csv_file, plot_theta, plot_diff, 0, 0.0, 0.0, 0.0)

        last_raw1 = offset1
        last_raw2 = offset2
        unwrapped1 = 0.0
        unwrapped2 = 0.0

        for i in range(NUM_MOVES):
            commanded_theta = (i + 1) * DEGREES_PER_MOVE

            move_dpe(dpe, STEPS_PER_MOVE)
            time.sleep(MOVE_SETTLE_TIME)

            measured_angle1, last_raw1, unwrapped1 = unwrap_angle(
                read_nd287_angle(nd1),
                last_raw1,
                unwrapped1,
                DIRECTION_1,
            )
            measured_angle2, last_raw2, unwrapped2 = unwrap_angle(
                read_nd287_angle(nd2),
                last_raw2,
                unwrapped2,
                DIRECTION_2,
            )

            print(f"Step {i + 1}/{NUM_MOVES}  Commanded: {commanded_theta:6.1f} deg   Measured1: {measured_angle1}   Measured2: {measured_angle2}")
            write_result(writer, csv_file, plot_theta, plot_diff, i + 1, commanded_theta, measured_angle1, measured_angle2)

        print(f"\nDone. Results saved to {OUTPUT_CSV}")
        save_difference_plot(plot_theta, plot_diff)
    finally:
        if csv_file is not None:
            csv_file.close()
        close_serial_connections(dpe, nd1, nd2)

        run_end = datetime.now()
        elapsed_seconds = time.perf_counter() - timer_start
        print(f"Run ended: {run_end.isoformat(timespec='seconds')}")
        print(f"Elapsed time: {elapsed_seconds:.2f} seconds")
