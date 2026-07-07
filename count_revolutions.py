import time
from datetime import datetime

from hardware import (
    close_serial_connections,
    move_dpe,
    open_serial_connections,
    read_nd287_angle,
    setup_dpe,
)
from variables import (
    EQUAL_ANGLE_TOLERANCE_DEG,
    MAX_TINY_MOVEMENTS,
    REV_COUNTER_PROGRESS_INTERVAL,
    REV_COUNTER_SETTLE_TIME,
    STEPS_PER_REV,
    TINY_MOVE_STEPS,
)


def signed_angle_difference(angle, reference):
    diff = angle - reference
    if diff > 180:
        diff -= 360
    elif diff < -180:
        diff += 360
    return diff


def angles_are_equal(angle, reference, tolerance):
    if angle is None or reference is None:
        return False
    return abs(signed_angle_difference(angle, reference)) <= tolerance


def average_counts(count1, count2):
    if count1 is None or count2 is None:
        return None
    if count1 == count2:
        return count1
    return (count1 + count2) / 2


def tiny_movements_to_revolutions(tiny_movements):
    if tiny_movements is None:
        return None
    return (tiny_movements * TINY_MOVE_STEPS) / STEPS_PER_REV


def run_revolution_counter():
    run_start = datetime.now()
    timer_start = time.perf_counter()
    print(f"Revolution counter started: {run_start.isoformat(timespec='seconds')}")
    print(f"Steps per commanded 360 deg revolution: {STEPS_PER_REV}")
    print(f"Steps per tiny movement: {TINY_MOVE_STEPS}")
    print(f"Tolerance: +/-{EQUAL_ANGLE_TOLERANCE_DEG} deg")
    print(f"Max tiny movements: {MAX_TINY_MOVEMENTS}\n")

    dpe = None
    nd1 = None
    nd2 = None
    count_to_equal1 = None
    count_to_equal2 = None
    left_start1 = False
    left_start2 = False
    movement_count = 0
    interrupted = False

    try:
        dpe, nd1, nd2 = open_serial_connections()
        setup_dpe(dpe)

        start1 = read_nd287_angle(nd1)
        start2 = read_nd287_angle(nd2)
        print(f"Starting value (ND1): {start1} deg")
        print(f"Starting value (ND2): {start2} deg\n")

        for movement_count in range(1, MAX_TINY_MOVEMENTS + 1):
            move_dpe(dpe, TINY_MOVE_STEPS)
            time.sleep(REV_COUNTER_SETTLE_TIME)

            angle1 = read_nd287_angle(nd1)
            angle2 = read_nd287_angle(nd2)

            diff1 = signed_angle_difference(angle1, start1) if angle1 is not None and start1 is not None else None
            diff2 = signed_angle_difference(angle2, start2) if angle2 is not None and start2 is not None else None

            equal1 = angles_are_equal(angle1, start1, EQUAL_ANGLE_TOLERANCE_DEG)
            equal2 = angles_are_equal(angle2, start2, EQUAL_ANGLE_TOLERANCE_DEG)

            if not equal1:
                left_start1 = True
            if not equal2:
                left_start2 = True

            returned1 = left_start1 and equal1
            returned2 = left_start2 and equal2

            if returned1 and count_to_equal1 is None:
                count_to_equal1 = movement_count
            if returned2 and count_to_equal2 is None:
                count_to_equal2 = movement_count

            if (
                movement_count == 1
                or movement_count % REV_COUNTER_PROGRESS_INTERVAL == 0
                or returned1
                or returned2
            ):
                equivalent_revs = tiny_movements_to_revolutions(movement_count)
                print(
                    f"Move {movement_count} ({equivalent_revs:.6f} rev): "
                    f"ND1={angle1} deg diff={diff1} left_start={left_start1} returned={returned1}   "
                    f"ND2={angle2} deg diff={diff2} left_start={left_start2} returned={returned2}"
                )

            if count_to_equal1 is not None and count_to_equal2 is not None:
                break

        averaged = average_counts(count_to_equal1, count_to_equal2)
        revs1 = tiny_movements_to_revolutions(count_to_equal1)
        revs2 = tiny_movements_to_revolutions(count_to_equal2)
        average_revs = tiny_movements_to_revolutions(averaged)

        print("\nTiny movement count complete")
        print(f"ND1 tiny movements required: {count_to_equal1}")
        print(f"ND1 equivalent revolutions: {revs1}")
        print(f"ND2 tiny movements required: {count_to_equal2}")
        print(f"ND2 equivalent revolutions: {revs2}")

        if averaged is None:
            print("Average tiny movements required: not available because one or both encoders did not return to start")
        else:
            print(f"Average tiny movements required: {averaged}")
            print(f"Average equivalent revolutions: {average_revs}")
    except KeyboardInterrupt:
        interrupted = True
        print("\nKeyboard interrupt received. Stopping revolution counter gracefully.")
        print(f"Last completed tiny movement: {movement_count}")
        print(f"ND1 tiny movements required so far: {count_to_equal1}")
        print(f"ND2 tiny movements required so far: {count_to_equal2}")
    finally:
        close_serial_connections(dpe, nd1, nd2)

        run_end = datetime.now()
        elapsed_seconds = time.perf_counter() - timer_start
        if interrupted:
            print("Run status: interrupted")
        print(f"\nRevolution counter ended: {run_end.isoformat(timespec='seconds')}")
        print(f"Elapsed time: {elapsed_seconds:.2f} seconds")


if __name__ == "__main__":
    run_revolution_counter()
