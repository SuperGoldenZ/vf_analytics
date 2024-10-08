import pytest
import cv2
import vf_cv

test_data = [
    ["assets/test_images/720p/time/10_08_01.png", "10", "08", 720, False],
    ["assets/test_images/480p/time/8_86_01.png", "8", "86", 480, True],
    ["assets/test_images/480p/time/09_88_01.png", "9", "88", 480, True],
    ["assets/test_images/1080p/time/43_66_01.png", "43", "66", 1080, False],
    ["assets/test_images/480p/time/08_00_01.png", "8", "00", 480, True],
    ["assets/test_images/720p/time/08_00_01.png", "8", "00", 720, True],
    ["assets/test_images/720p/time/09_96_01.png", "9", "96", 720, True],
    ["assets/test_images/480p/time/45_00_02.png", "45", "00", 480, False],
    ["assets/test_images/480p/time/45_00.png", "45", "00", 480, False],
    ["assets/test_images/480p/time/no_time_01.png", "", "00", 480, False],
    ["assets/test_images/480p/time/18_00_01.png", "18", "00", 480, False],
    ["assets/test_images/720p/time/42_75.png", "42", "76", 720, False],
    ["assets/test_images/480p/time/43_45.png", "43", "46", 720, False],
    ["assets/test_images/480p/time/16_75.png", "16", "76", 720, False],
    ["assets/test_images/480p/time/20_16.png", "20", "16", 720, False],
    ["assets/test_images/480p/time/29_66.png", "29", "66", 720, False],
    ["assets/test_images/480p/time/24_76.png", "24", "76", 720, False],
    ["assets/test_images/480p/time/30_56.png", "30", "68", 720, False],
    ["assets/test_images/480p/time/41_26.png", "41", "26", 720, False],
    ["assets/test_images/480p/time/44_06.png", "44", "06", 720, False],
    ["assets/test_images/480p/time/44_18.png", "44", "16", 720, False],
    ["assets/test_images/480p/time/40_16.png", "40", "16", 720, False],
    ["assets/test_images/480p/time/40_66.png", "40", "66", 720, False],
    ["assets/test_images/480p/time/40_76.png", "40", "76", 720, False],
    ["assets/test_images/480p/time/39_46.png", "39", "46", 720, False],
    ["assets/test_images/480p/time/39_88.png", "39", "66", 720, False],
    ["assets/test_images/480p/time/37_78.png", "37", "76", 720, False],
    ["assets/test_images/480p/time/36_88.png", "36", "66", 720, False],
    ["assets/test_images/480p/time/22_76.png", "22", "76", 720, False],
    ["assets/test_images/480p/time/30_96.png", "30", "96", 720, False],
    ["assets/test_images/480p/time/31_16.png", "31", "16", 720, False],
    ["assets/test_images/480p/time/32_36.png", "32", "36", 720, False],
    ["assets/test_images/480p/time/33_36.png", "33", "36", 720, False],
    ["assets/test_images/480p/time/33_18.png", "33", "18", 720, False],
    ["assets/test_images/480p/time/34_96.png", "34", "28", 720, False],
    ["assets/test_images/480p/time/35_28.png", "35", "28", 720, False],
    ["assets/test_images/480p/time/37_68.png", "37", "68", 720, False],
    ["assets/test_images/480p/time/38_26.png", "38", "26", 720, False],
    ["assets/test_images/480p/time/41_78.png", "41", "78", 720, False],
    ["assets/test_images/480p/time/43_96.png", "43", "96", 720, False],
]


@pytest.mark.parametrize(
    "image_filename, expected_time_seconds, expected_time_ms, resolution, expected_is_time_running_out",
    test_data,
)
def test_time_running_out(
    image_filename,
    expected_time_seconds,
    expected_time_ms,
    resolution,
    expected_is_time_running_out,
):
    """Tests OCR for getting time remaining during a match with 480p resolution"""

    image = cv2.imread(image_filename)

    assert image is not None, f"{image_filename} is none"

    timer = vf_cv.Timer()
    timer.set_frame(image)

    height = image.shape[0]  # Get the dimensions of the frame
    assert (
        height == resolution
    ), f"{image_filename} is {height}p instead of expected {resolution}p"

    DEBUG = False
    actual_is_time_running_out = timer.is_time_running_out(DEBUG)
    assert (
        expected_is_time_running_out == actual_is_time_running_out
    ), f"{actual_is_time_running_out} not expected value of {expected_is_time_running_out} for {image_filename}"
