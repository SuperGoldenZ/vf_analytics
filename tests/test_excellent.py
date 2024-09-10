import os
import pytest
import cv2
import vf_cv


test_data = [
    ["assets/test_images/1080p/excellent/excellent_for_player_1_07.png", True],
    ["assets/test_images/1080p/excellent/excellent_for_player_1_06.png", True],
    ["assets/test_images/1080p/excellent/excellent_for_player_1_05.png", True],
    ["assets/test_images/1080p/excellent/excellent_for_player_1_04.png", True],
    ["assets/test_images/1080p/excellent/excellent_for_player_1_03.png", True],
    ["assets/test_images/1080p/excellent/excellent_for_player_1_02.png", True],
    ["assets/test_images/1080p/excellent/excellent_for_player_1_01.png", True],
    ["assets/test_images/480p/excellent/excellent_2_0_01.png", True],
    ["assets/test_images/480p/excellent/excellent_1_0_01.png", True],
    ["assets/test_images/480p/excellent/excellent_1118_original.png", True],
    ["assets/test_images/480p/excellent/excellent_1129.png", True],
    ["assets/test_images/480p/excellent/excellent_1118.png", True],
    ["assets/test_images/480p/excellent/excellent_09.png", True],
    ["assets/test_images/480p/excellent/excellent_08.png", True],
    ["assets/test_images/480p/excellent/excellent_07.png", True],
    ["assets/test_images/480p/excellent/excellent_06.png", True],
    ["assets/test_images/480p/excellent/excellent_05.png", True],
    ["assets/test_images/480p/excellent/excellent_01.jpg", True],
    ["assets/test_images/480p/excellent/excellent_1_1_01.jpg", True],
    ["assets/test_images/480p/excellent/excellent_2_2_01.jpg", True],
    ["assets/test_images/480p/excellent/excellent_0_2_01.jpg", True],
]


@pytest.mark.parametrize("image_filename, expected_result", test_data)
def test_is_excellent(image_filename, expected_result):
    """Tests OCR for determining if frame shows one player winning with an excellent"""

    assert os.path.isfile(image_filename), f"{image_filename} does not exist"

    winning_frame = vf_cv.WinningFrame()

    frame = cv2.imread(image_filename)
    winning_frame.set_frame(frame)

    DEBUG = False
    assert expected_result == winning_frame.is_excellent(
        DEBUG
    ), f"{image_filename} is excellent {expected_result} as expected"
