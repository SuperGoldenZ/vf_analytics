import pytest
import cv2
import vf_cv

test_data = [
    ["assets/test_images/480p/time/roundover_02.png", "endround", "96", 480, False],
    ["assets/test_images/480p/time/8_86_01.png", "8", "86", 480, True],
    ["assets/test_images/480p/time/8_85_01.png", "8", "85", 480, True],
    ["assets/test_images/480p/time/08_95_01.png", "8", "95", 480, True],
    ["assets/test_images/480p/time/09_88_01.png", "9", "88", 480, True],
    ["assets/test_images/480p/time/14_65_01.png", "14", "65", 480, False],
    ["assets/test_images/480p/time/25_95_01.png", "25", "95", 480, False],
    ["assets/test_images/480p/time/16_96_01.png", "16", "96", 480, False],
    ["assets/test_images/480p/time/26_91_01.png", "26", "91", 480, False],
    ["assets/test_images/480p/time/40_05_01.png", "40", "05", 480, False],
    ["assets/test_images/480p/time/29_88_01.png", "29", "88", 480, False],
    ["assets/test_images/480p/time/32_21_01.png", "32", "21", 480, False],
    ["assets/test_images/480p/time/39_95_01.png", "39", "95", 480, False],
    ["assets/test_images/480p/time/roundover.png", "endround", "96", 480, False],
    ["assets/test_images/480p/time/30_96_01.png", "30", "96", 480, False],
    ["assets/test_images/480p/time/19_95_01.png", "19", "95", 480, False],
    ["assets/test_images/480p/time/26_98_02.png", "26", "98", 480, False],
    ["assets/test_images/480p/time/32_08_01.png", "32", "08", 480, False],
    ["assets/test_images/480p/time/36_93_01.png", "36", "93", 480, False],
    ["assets/test_images/480p/time/38_96_02.png", "38", "96", 480, False],
    ["assets/test_images/480p/time/39_98_01.png", "39", "98", 480, False],
    ["assets/test_images/480p/time/23_78_01.png", "23", "78", 480, False],
    ["assets/test_images/480p/time/23_96_01.png", "23", "96", 480, False],
    ["assets/test_images/480p/time/29_19_01.png", "29", "19", 480, False],
    ["assets/test_images/480p/time/26_33_01.png", "26", "33", 480, False],
    ["assets/test_images/480p/time/29_96_02.png", "29", "96", 480, False],
    ["assets/test_images/480p/time/22_98_01.png", "22", "98", 480, False],
    ["assets/test_images/480p/time/26_63_01.png", "26", "63", 480, False],
    ["assets/test_images/480p/time/26_98_01.png", "26", "98", 480, False],
    ["assets/test_images/480p/time/36_96_01.png", "36", "96", 480, False],
    ["assets/test_images/480p/time/17_65_01.png", "17", "65", 480, False],
    ["assets/test_images/480p/time/18_85_01.png", "18", "85", 480, False],
    ["assets/test_images/480p/time/27_48_01.png", "27", "48", 480, False],
    ["assets/test_images/480p/time/27_66_01.png", "27", "66", 480, False],
    ["assets/test_images/480p/time/27_98_01.png", "27", "98", 480, False],
    ["assets/test_images/480p/time/28_08_01.png", "28", "08", 480, False],
    ["assets/test_images/480p/time/29_96_01.png", "29", "96", 480, False],
    ["assets/test_images/480p/time/36_86_01.png", "36", "86", 480, False],
    ["assets/test_images/480p/time/36_98_01.png", "36", "98", 480, False],
    ["assets/test_images/480p/time/38_73_01.png", "38", "73", 480, False],
    ["assets/test_images/480p/time/38_96_01.png", "38", "96", 480, False],
    ["assets/test_images/480p/time/39_76_01.png", "39", "76", 480, False],
    ["assets/test_images/480p/time/39_96_02.png", "39", "96", 480, False],
    ["assets/test_images/480p/time/39_96_01.png", "39", "96", 480, False],
    ["assets/test_images/480p/time/42_46_01.png", "42", "46", 480, False],
    ["assets/test_images/480p/time/42_98.png", "42", "98", 480, False],
    ["assets/test_images/720p/time/27_26_01.png", "27", "26", 720, False],
    ["assets/test_images/1080p/time/05_31_02.png", "5", "31", 1080, False],
    ["assets/test_images/1080p/time/05_31_01.png", "5", "31", 1080, False],
    ["assets/test_images/480p/time/41_78.png", "41", "78", 720, False],
    ["assets/test_images/1080p/time/29_85_01.png", "29", "85", 1080, True],
    ["assets/test_images/1080p/time/29_05_01.png", "29", "05", 1080, True],
    ["assets/test_images/1080p/time/41_78_01.png", "41", "78", 1080, True],
    ["assets/test_images/1080p/time/41_76_01.png", "41", "76", 1080, True],
    ["assets/test_images/1080p/time/18_23_01.png", "18", "23", 1080, True],
    ["assets/test_images/1080p/time/45_00_01.png", "45", "00", 1080, True],
    ["assets/test_images/1080p/time/29_46_01.png", "29", "46", 1080, True],
    ["assets/test_images/1080p/time/42_73_01.png", "42", "73", 1080, True],
    ["assets/test_images/1080p/time/42_16_01.png", "42", "16", 1080, True],
    ["assets/test_images/1080p/time/43_66_01.png", "43", "66", 1080, True],
    ["assets/test_images/480p/time/08_00_01.png", "8", "00", 480, True],
    ["assets/test_images/480p/time/45_00_02.png", "45", "00", 480, False],
    ["assets/test_images/480p/time/45_00.png", "45", "00", 480, False],
    ["assets/test_images/480p/time/18_00_01.png", "18", "00", 480, False],
    ["assets/test_images/720p/time/08_00_01.png", "8", "00", 720, True],
    ["assets/test_images/720p/time/09_96_01.png", "9", "96", 720, True],
    ["assets/test_images/720p/time/10_08_01.png", "1", "08", 720, True],
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
    ["assets/test_images/480p/time/43_96.png", "43", "96", 720, False],
]


@pytest.mark.parametrize(
    "image_filename, expected_time_seconds, expected_time_ms, resolution, expected_is_time_running_out",
    test_data,
)
def test_get_time_seconds(
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
    actual_time_seconds = timer.get_time_seconds(DEBUG)
    assert (
        expected_time_seconds == actual_time_seconds
    ), f"{actual_time_seconds} not expected value of {expected_time_seconds} for {image_filename}"
