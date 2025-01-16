"""Tests for getting the number of drink points Shun has"""

import pytest
import cv2
import vf_cv

DIR = "assets/test_images/"

test_data = [
    [f"{DIR}720p/dp/webp/dp_0_xx_04.webp", 1, -1, 720, False, "Waterfalls"],
    [f"{DIR}720p/dp/webp/dp_0_xx_05.webp", 1, -1, 720, False, "Waterfalls"],
    [f"{DIR}720p/dp/webp/dp_8_xx_03.webp", 1, -1, 720, False, "Waterfalls"],
    [f"{DIR}720p/dp/webp/dp_7_xx_04.webp", 1, -1, 720, False, "Waterfalls"],
    [f"{DIR}720p/dp/webp/dp_4_xx_04.webp", 1, 4, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_12_xx_02.webp", 1, 12, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_1_xx_05.webp", 1, 1, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_4_xx_03.webp", 1, 4, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_11_xx_01.webp", 1, 11, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_4_xx_02.webp", 1, 4, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_22_xx_01.webp", 1, 22, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_22_xx.webp", 1, 22, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_20_xx_01.webp", 1, 20, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_18.webp", 2, 18, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_14.webp", 2, 14, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_10_xx_02.webp", 1, 10, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_0_xx_01.webp", 1, 0, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_9.webp", 2, 9, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_3_xx_02.webp", 1, 3, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_11_04.webp", 2, 11, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_16.webp", 2, 16, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_10_xx_01.webp", 1, 10, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_9_xx_01.webp", 1, 9, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_4_12.webp", 1, 4, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_4_12.webp", 2, 12, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_7.webp", 2, 7, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_7_0.webp", 1, 7, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_7_0.webp", 2, 0, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_3_3.webp", 1, 3, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_3_3.webp", 2, 3, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_9_5.webp", 1, 9, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_9_5.webp", 2, 5, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_1_xx_03.webp", 1, 1, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_19_xx_01.webp", 1, 19, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_5_xx_04.webp", 1, 5, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_7_xx_03.webp", 1, 7, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_0_02.webp", 2, 0, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_8_xx_02.webp", 1, 8, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_0_xx_03.webp", 1, 0, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_1_5.webp", 1, 1, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_1_5.webp", 2, 5, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_17.webp", 2, 17, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_11_03.webp", 2, 11, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_11_01.webp", 2, 11, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_11_02.webp", 2, 11, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_0_xx_02.webp", 1, 0, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_7_01.webp", 2, 7, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_9_xx.webp", 1, 9, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_07_01.webp", 2, 8, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_5_xx_03.webp", 1, 5, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_5_xx_02.webp", 1, 5, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_06_01.webp", 2, 6, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_xx_06.webp", 2, 6, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_12_xx_01.webp", 1, 12, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_7_xx_01.webp", 1, 7, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_7_xx_02.webp", 1, 7, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_11_xx.webp", 1, 11, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_1_xx.webp", 1, 1, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_2_xx.webp", 1, 2, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_7_xx.webp", 1, 7, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_8_xx.webp", 1, 8, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_20_xx.webp", 1, 20, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_12_xx.webp", 1, 12, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_12_yy.webp", 1, 12, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_14_xx.webp", 1, 14, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_12_xx.webp", 1, 12, 720, False, None],
    [f"{DIR}720p/dp/webp/dp_14_xx.webp", 1, 14, 720, False, None],
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
