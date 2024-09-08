import pytest
import cv2
import vf_cv

test_data = [
    ["assets/test_images/1080p/time/29_05_01.png", "28", "05", 1080, True],
    ["assets/test_images/1080p/time/29_85_01.png", "29", "85", 1080, True],
    ["assets/test_images/1080p/time/41_78_01.png", "41", "78", 1080, True],
    ["assets/test_images/1080p/time/41_76_01.png", "41", "76", 1080, True],
    ["assets/test_images/1080p/time/42_18_01.png", "42", "18", 1080, True],
    ["assets/test_images/1080p/time/32_93_01.png", "32", "93", 1080, True],
    ["assets/test_images/1080p/time/32_90_01.png", "32", "90", 1080, True],
    ["assets/test_images/1080p/time/32_85_01.png", "32", "85", 1080, True],
    ["assets/test_images/1080p/time/32_88_01.png", "32", "88", 1080, True],
    ["assets/test_images/1080p/time/42_73_01.png", "42", "73", 1080, True],
    ["assets/test_images/1080p/time/23_28_01.png", "23", "28", 1080, True],
    ["assets/test_images/1080p/time/23_26_01.png", "23", "26", 1080, True],
    ["assets/test_images/1080p/time/23_25_01.png", "23", "25", 1080, True],
    ["assets/test_images/1080p/time/18_23_01.png", "18", "23", 1080, True],
    ["assets/test_images/1080p/time/34_88_01.png", "34", "88", 1080, False],
    ["assets/test_images/480p/time/45_00_02.png", "45", "20", 480, False],
    ["assets/test_images/480p/time/08_00_01.png", "8", "00", 480, True],
    ["assets/test_images/1080p/time/42_16_01.png", "42", "16", 1080, True],
    ["assets/test_images/1080p/time/43_66_01.png", "43", "66", 1080, True],
]


@pytest.mark.parametrize(
    "image_filename, expected_time_seconds, expected_time_ms, resolution, expected_is_time_running_out",
    test_data,
)
def test_get_time_ms(
    image_filename,
    expected_time_seconds,
    expected_time_ms,
    resolution,
    expected_is_time_running_out,
):
    """Tests OCR for getting time remaining during a match with 480p resolution"""

    image = cv2.imread(image_filename)
    assert image is not None, f"{image_filename} is none"

    height = image.shape[0]
    assert (
        height == resolution
    ), f"{image_filename} is {height}p instead of expected {resolution}p"

    timer = vf_cv.Timer()
    timer.set_frame(image)
    DEBUG = False
    actual_time_ms = timer.get_time_ms(DEBUG)
    assert (
        expected_time_ms == actual_time_ms
    ), f"{actual_time_ms} not expected value of {expected_time_ms} for {image_filename}"
