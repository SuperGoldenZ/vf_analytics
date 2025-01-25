"""Tests for getting the time from the timer in the middle of the screen"""

import pytest
import cv2
import vf_cv

DIR = "assets/test_images/"

test_data_other = [
    f"{DIR}720p/time/png/endround_08.png",
    f"{DIR}720p/time/png/endround_07.png",
    f"{DIR}720p/time/png/endround_06.png",
    f"{DIR}1080p/winning_frame/endround_02.png",
]


@pytest.mark.parametrize(
    "image_filename",
    test_data_other,
)
def test_other(image_filename):
    image = cv2.imread(image_filename)
    assert image is not None, f"{image_filename} is none"

    timer = vf_cv.Timer()

    stage = None

    timer.set_frame(image, stage)

    actual_endround_other = timer.is_endround_other(False)

    assert actual_endround_other == True, f"not endround as expected {image_filename}"


test_data_720p = [
    [f"{DIR}1080p/time/png/44.png", "44", 1080, True],
    [f"{DIR}1080p/time/webp/19_02.webp", "19", 1080, False],
    [f"{DIR}1080p/time/webp/19_01.webp", "19", 1080, False],
    [f"{DIR}1080p/time/webp/28_45.webp", "28", 1080, False],
    [f"{DIR}720p/time/webp/29_04.webp", "29", 720, False],
    [f"{DIR}720p/time/webp/39_02.webp", "39", 720, False],
    [f"{DIR}720p/time/webp/26_03.webp", "26", 720, False],
    [f"{DIR}720p/time/webp/9_01.webp", "9", 720, False],
    [f"{DIR}720p/time/webp/29_02.webp", "29", 720, False],
    [f"{DIR}720p/time/webp/32_01.webp", "32", 720, False],
    [f"{DIR}720p/time/webp/35_02.webp", "35", 720, False],
    [f"{DIR}720p/time/webp/24_01.webp", "24", 720, False],
    [f"{DIR}720p/time/webp/29_01.webp", "29", 720, False],
    [f"{DIR}720p/time/webp/26_01.webp", "26", 720, False],
    [f"{DIR}720p/time/webp/16_01.webp", "16", 720, False],
    [f"{DIR}720p/time/webp/25_01.webp", "25", 720, False],
    [f"{DIR}720p/time/webp/29_03.webp", "29", 720, False],
    [f"{DIR}720p/time/webp/29_16_01.webp", "29", 720, False],
    [f"{DIR}720p/time/webp/38_01.webp", "38", 720, False],
    [f"{DIR}720p/time/webp/7848_invalid_time_27_25.webp", "26", 720, False],
    [f"{DIR}720p/time/webp/39_01.webp", "39", 720, False],
    [f"{DIR}720p/time/webp/35_01.webp", "35", 720, False],
    [f"{DIR}720p/time/webp/24_91.webp", "24", 720, False],
    [f"{DIR}720p/time/webp/38_96.webp", "38", 720, False],
    [f"{DIR}720p/time/webp/31_55.webp", "31", 720, False],
    [f"{DIR}720p/time/webp/38_83.webp", "38", 720, False],
    [f"{DIR}720p/time/webp/39_83.webp", "39", 720, False],
    [f"{DIR}720p/time/webp/3943_unknown_skip.webp", "37", 720, False],
    [f"{DIR}720p/time/webp/2790_unknown_skip.webp", "22", 720, False],
    [f"{DIR}720p/time/webp/2479_unknown_skip.webp", "27", 720, False],
    [f"{DIR}720p/time/webp/2116_invalid_time_35_33_last.webp", "33", 720, False],
    [f"{DIR}720p/time/webp/2116_invalid_time_35_33.webp", "33", 720, False],
    [f"{DIR}720p/time/webp/5753_invalid_time_23_28.webp", "22", 720, False],
    [f"{DIR}720p/time/webp/2094_invalid_time_37_35_last.webp", "35", 720, False],
    [f"{DIR}720p/time/webp/2094_invalid_time_37_35.webp", "35", 720, False],
]


# @todo move back to all test data
@pytest.mark.parametrize(
    "image_filename, expected_time_seconds, resolution, DEBUG",
    test_data_720p,
)
def test_get_time_seconds(
    image_filename,
    expected_time_seconds,
    resolution,
    DEBUG,
):
    """Tests OCR for getting time remaining during a match with 480p resolution"""

    image = cv2.imread(image_filename)
    assert image is not None, f"{image_filename} is none"

    height = image.shape[0]
    assert (
        height == resolution
    ), f"{image_filename} is {height}p instead of expected {resolution}p"

    timer = vf_cv.Timer()

    stage = None

    if "1080p/time/28_45.png" in image_filename:
        stage = "Deep Mountain"

    timer.set_frame(image, stage)

    actual_time_seconds = timer.get_time_seconds(DEBUG)
    assert (
        expected_time_seconds == actual_time_seconds
    ), f"{actual_time_seconds} not expected value of {expected_time_seconds} for {image_filename}"
