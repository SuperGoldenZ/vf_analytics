"""Tests to get stage name from vs screen"""

import pytest
import cv2
import vf_cv.vs_screen


test_data = [
    ["assets/test_images/480p/stage/webp/aurora.webp", "Aurora"],
    ["assets/test_images/480p/stage/webp/deep_mountain.webp", "Deep Mountain"],
    ["assets/test_images/480p/stage/webp/genesis.webp", "Genesis"],
    ["assets/test_images/480p/stage/webp/none_01.webp", None],
    ["assets/test_images/480p/stage/webp/shrine.webp", "Shrine"],
    ["assets/test_images/480p/stage/webp/sumo_ring.webp", "Sumo Ring"],
    ["assets/test_images/480p/stage/webp/terrace.webp", "Terrace"],
    ["assets/test_images/480p/stage/webp/training_room.webp", "Training Room"],
    ["assets/test_images/480p/stage/webp/waterfalls.webp", "Waterfalls"],
]


@pytest.mark.parametrize("image_filename, expected_stage_name", test_data)
def test_get_stage(image_filename, expected_stage_name):
    vs_image = cv2.imread(image_filename)

    assert vs_image is not None, f"{image_filename} is unexpectedly none"

    try:
        debug_stage = False
        vs_screen = vf_cv.VsScreen()
        vs_screen.set_frame(vs_image)
        stage = vs_screen.get_stage(debug_stage)
        assert expected_stage_name == stage

    except Exception as a:
        assert False, f"Test failed because of exception {a}"
