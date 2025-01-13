"""Tests for getting the number of drink points Shun has"""

import pytest
import cv2
import vf_cv

DIR = "assets/test_images/"

test_data = [
    # [f"{DIR}720p/dp/dp_6_xx.png", 1, 6, 720, True, None],
    [f"{DIR}720p/dp/dp_0_xx_04.png", 1, -1, 720, False, "Waterfalls"],
    [f"{DIR}720p/dp/dp_0_xx_05.png", 1, -1, 720, False, "Waterfalls"],
    [f"{DIR}720p/dp/dp_8_xx_03.png", 1, -1, 720, False, "Waterfalls"],
    [f"{DIR}720p/dp/dp_7_xx_04.png", 1, -1, 720, False, "Waterfalls"],
    # [f"{DIR}720p/dp/dp_xx_01.png", 2, 1, 720, False, "Island"],
    # [f"{DIR}720p/dp/dp_2_xx_01.png", 1, 2, 720, False, "Island"],
    # [f"{DIR}720p/dp/dp_5_xx_05.png", 1, 5, 720, False, "Island"],
    [f"{DIR}720p/dp/dp_4_xx_04.png", 1, 4, 720, False, None],
    [f"{DIR}720p/dp/dp_12_xx_02.png", 1, 12, 720, False, None],
    # [f"{DIR}720p/dp/dp_0_xx.png", 1, 0, 720, True, None],
    [f"{DIR}720p/dp/dp_1_xx_05.png", 1, 1, 720, False, None],
    [f"{DIR}720p/dp/dp_4_xx_03.png", 1, 4, 720, False, None],
    [f"{DIR}720p/dp/dp_11_xx_01.png", 1, 11, 720, False, None],
    [f"{DIR}720p/dp/dp_10_xx_03.png", 1, 10, 720, False, None],
    [f"{DIR}720p/dp/dp_4_xx_02.png", 1, 4, 720, False, None],
    [f"{DIR}720p/dp/dp_22_xx_01.png", 1, 22, 720, False, None],
    [f"{DIR}720p/dp/dp_22_xx.png", 1, 22, 720, False, None],
    [f"{DIR}720p/dp/dp_20_xx_01.png", 1, 20, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_18.png", 2, 18, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_14.png", 2, 14, 720, False, None],
    [f"{DIR}720p/dp/dp_10_xx_02.png", 1, 10, 720, False, None],
    [f"{DIR}720p/dp/dp_0_xx_01.png", 1, 0, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_9.png", 2, 9, 720, False, None],
    [f"{DIR}720p/dp/dp_3_xx_02.png", 1, 3, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_11_04.png", 2, 11, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_16.png", 2, 16, 720, False, None],
    [f"{DIR}720p/dp/dp_10_xx_01.png", 1, 10, 720, False, None],
    [f"{DIR}720p/dp/dp_9_xx_01.png", 1, 9, 720, False, None],
    [f"{DIR}720p/dp/dp_4_12.png", 1, 4, 720, False, None],
    [f"{DIR}720p/dp/dp_4_12.png", 2, 12, 720, False, None],
    # [f"{DIR}720p/dp/dp_xx_6.png", 2, 6, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_7.png", 2, 7, 720, False, None],
    # [f"{DIR}720p/dp/dp_xx_4_01.png", 2, 4, 720, False, None],
    [f"{DIR}720p/dp/dp_7_0.png", 1, 7, 720, False, None],
    [f"{DIR}720p/dp/dp_7_0.png", 2, 0, 720, False, None],
    [f"{DIR}720p/dp/dp_3_3.png", 1, 3, 720, False, None],
    [f"{DIR}720p/dp/dp_3_3.png", 2, 3, 720, False, None],
    [f"{DIR}720p/dp/dp_9_5.png", 1, 9, 720, False, None],
    [f"{DIR}720p/dp/dp_9_5.png", 2, 5, 720, False, None],
    [f"{DIR}720p/dp/dp_1_xx_03.png", 1, 1, 720, False, None],
    [f"{DIR}720p/dp/dp_19_xx_01.png", 1, 19, 720, False, None],
    [f"{DIR}720p/dp/dp_5_xx_04.png", 1, 5, 720, False, None],
    [f"{DIR}720p/dp/dp_7_xx_03.png", 1, 7, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_0_02.png", 2, 0, 720, False, None],
    [f"{DIR}720p/dp/dp_8_xx_02.png", 1, 8, 720, False, None],
    [f"{DIR}720p/dp/dp_0_xx_03.png", 1, 0, 720, False, None],
    [f"{DIR}720p/dp/dp_1_5.png", 1, 1, 720, False, None],
    [f"{DIR}720p/dp/dp_1_5.png", 2, 5, 720, False, None],
    # [f"{DIR}720p/dp/dp_0_xx.png", 1, 0, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_17.png", 2, 17, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_11_03.png", 2, 11, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_11_01.png", 2, 11, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_11_02.png", 2, 11, 720, False, None],
    [f"{DIR}720p/dp/dp_0_xx_02.png", 1, 0, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_7_01.png", 2, 7, 720, False, None],
    [f"{DIR}720p/dp/dp_9_xx.png", 1, 9, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_07_01.png", 2, 8, 720, False, None],
    [f"{DIR}720p/dp/dp_5_xx_03.png", 1, 5, 720, False, None],
    [f"{DIR}720p/dp/dp_5_xx_02.png", 1, 5, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_06_01.png", 2, 6, 720, False, None],
    [f"{DIR}720p/dp/dp_xx_06.png", 2, 6, 720, False, None],
    [f"{DIR}720p/dp/dp_12_xx_01.png", 1, 12, 720, False, None],
    [f"{DIR}720p/dp/dp_7_xx_01.png", 1, 7, 720, False, None],
    [f"{DIR}720p/dp/dp_7_xx_02.png", 1, 7, 720, False, None],
    [f"{DIR}720p/dp/dp_11_xx.png", 1, 11, 720, False, None],
    [f"{DIR}720p/dp/dp_1_xx.png", 1, 1, 720, False, None],
    [f"{DIR}720p/dp/dp_2_xx.png", 1, 2, 720, False, None],
    [f"{DIR}720p/dp/dp_7_xx.png", 1, 7, 720, False, None],
    [f"{DIR}720p/dp/dp_8_xx.png", 1, 8, 720, False, None],
    [f"{DIR}720p/dp/dp_20_xx.png", 1, 20, 720, False, None],
    # [f"{DIR}720p/dp/dp_xx_4.png", 2, 4, 360, False, None],
    [f"{DIR}720p/dp/dp_12_xx.png", 1, 12, 720, False, None],
    [f"{DIR}720p/dp/dp_12_yy.png", 1, 12, 720, False, None],
    [f"{DIR}720p/dp/dp_14_xx.png", 1, 14, 720, False, None],
    # [f"{DIR}720p/dp/dp_10_xx.png", 1, 10, 720, False, None],
    [f"{DIR}720p/dp/dp_12_xx.png", 1, 12, 720, False, None],
    [f"{DIR}720p/dp/dp_14_xx.png", 1, 14, 720, False, None],
    # [f"{DIR}720p/dp/dp_xx_1.png", 2, 1, 720, False, None],
    # [f"{DIR}360p/dp/dp_0_xx.png", 1, 0, 360, False, None],
    # [f"{DIR}360p/dp/dp_3_xx.png", 1, 3, 360, False, None],
    # [f"{DIR}360p/dp/dp_3_xx.png", 1, 6, 360, False, None],
    # [f"{DIR}360p/dp/dp_10_xx.png", 1, 10, 360, False, None],
    # [f"{DIR}360p/dp/dp_15_xx.png", 1, 15, 360, False, None],
    # [f"{DIR}360p/dp/dp_16_xx.png", 1, 16, 360, False, None],
    # [f"{DIR}360p/dp/dp_19_xx.png", 1, 19, 360, False, None],
    # [f"{DIR}360p/dp/dp_xx_0.png", 2, 0, 360, False, None],
    # [f"{DIR}360p/dp/dp_xx_1.png", 2, 1, 360, False, None],
    # [f"{DIR}360p/dp/dp_xx_4.png", 2, 4, 360, False, None],
    # [f"{DIR}360p/dp/dp_xx_5.png", 2, 5, 360, False, None],
    # [f"{DIR}360p/dp/dp_xx_6.png", 2, 6, 360, False, None],
]


@pytest.mark.parametrize(
    "image_filename, playernum, expected_drinks, resolution, debug, stage",
    test_data,
)
def test_drinks_player_2(
    image_filename, playernum, expected_drinks, resolution, debug, stage
):
    """Tests OCR for getting time remaining during a match with 480p resolution"""

    image = cv2.imread(image_filename)
    assert image is not None, f"{image_filename} is none"

    height = image.shape[0]
    assert (
        height == resolution
    ), f"{image_filename} is {height}p instead of expected {resolution}p"

    drinks = vf_cv.Drinks(stage=stage)
    drinks.set_frame(image)

    actual_drinks = drinks.get_drink_points(playernum, debug)
    assert (
        actual_drinks == expected_drinks
    ), f"{actual_drinks} not expected value of {expected_drinks} for {image_filename}"
