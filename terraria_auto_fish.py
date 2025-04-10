import cv2
import numpy as np
import pyautogui as gui
import pydirectinput as di
import time

# When run, this script will prompt the user to place the mouse in two locations.
# First, place the pointer where the bobber will sit and press enter. Then, at the player.
# The script will then monitor the position of the bobber to determine when a fish is hooked.

MOTION_THRESHOLD = 100000

CAPTURE_WIDTH  = 100
CAPTURE_HEIGHT = 100

HORIZONTAL_DRIFT_SCALE = 0.1

CAST_DISTANCE = 500

PRESS_KEY = 'p'

def capture_region(region):
    screenshot = gui.screenshot(region=region)
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    return frame

def terraria_auto_fish():
    # Get the locations of the bobber and the player.
    input("Place the mouse over the BOBBER and press Enter...")
    bobber_pos = gui.position()
    print(f"Bobber position recorded at: {bobber_pos}")

    input("Place the mouse over the PLAYER and press Enter...")
    player_pos = gui.position()
    print(f"Player position recorded at: {player_pos}")

    # Calculate the vector from the player to the bobber and cast a point along the line for our clicking position
    x_vec = bobber_pos.x - player_pos.x
    y_vec = bobber_pos.y - player_pos.y

    magnitude  = (x_vec**2 + y_vec**2) ** 0.5
    unit_vec_x = x_vec / magnitude
    unit_vec_y = y_vec / magnitude

    cast_x = int(player_pos.x + unit_vec_x * CAST_DISTANCE)
    cast_y = int(player_pos.y + unit_vec_y * CAST_DISTANCE)

    # Calculate the capture box coordinates (left, top). Account for some small x-drift of the bobber on cast.
    left = int(bobber_pos.x + x_vec * HORIZONTAL_DRIFT_SCALE - CAPTURE_WIDTH // 2)
    top  = int(bobber_pos.y - CAPTURE_HEIGHT // 2)

    capture_box = (left, top, CAPTURE_WIDTH, CAPTURE_HEIGHT)

    # Click into game and do initial cast.
    di.moveTo(cast_x, cast_y)
    di.click(cast_x, cast_y)
    time.sleep(0.1)
    di.press(PRESS_KEY)

    # Begin watch
    time.sleep(1.0)
    prev_frame = capture_region(capture_box)
    time.sleep(0.1)

    trigger_time = 0.0
    motion_detected = False
    print("Monitoring started. Press ESC to exit.")

    while True:
        curr_frame = capture_region(capture_box)
        
        diff = cv2.absdiff(prev_frame, curr_frame)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

        motion_level = np.sum(thresh)
        cv2.imshow("Motion Detection", thresh)

        if motion_level > MOTION_THRESHOLD and not motion_detected:
            print("Got a bite!")
            di.moveTo(cast_x, cast_y)
            di.press(PRESS_KEY)
            time.sleep(0.25)
            di.press(PRESS_KEY)

            trigger_time = time.time()
            motion_detected = True

        elif motion_detected and time.time() - trigger_time > 0.5:
            motion_detected = False
            print("Looking for movement...")

        prev_frame = curr_frame

        # Exit when ESC key is pressed
        key = cv2.waitKey(1)
        if key == 27:  # ESC key
            print("Exiting.")
            break

        time.sleep(0.1)

    cv2.destroyAllWindows()

terraria_auto_fish()
