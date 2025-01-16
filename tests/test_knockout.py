"""Tests for telling if a frame is knocking out another player"""

import pytest
import cv2
import vf_cv

test_data = [
    "assets/test_images/1080p/ko/knockout_for_player_1_06.png",
    "assets/test_images/360p/knockout/webp/knockout_43.webp",
    "assets/test_images/360p/knockout/webp/knockout_38.webp",
    "assets/test_images/360p/knockout/webp/knockout_37.webp",
    "assets/test_images/360p/knockout/webp/knockout_35.webp",
    "assets/test_images/360p/knockout/webp/knockout_34.webp",
    "assets/test_images/360p/knockout/webp/knockout_31.webp",
    "assets/test_images/360p/knockout/webp/knockout_14.webp",
    "assets/test_images/360p/knockout/webp/knockout_12.webp",
    "assets/test_images/360p/knockout/webp/knockout_11.webp",
    "assets/test_images/360p/knockout/webp/knockout_10.webp",
    "assets/test_images/360p/knockout/webp/knockout_09.webp",
    "assets/test_images/360p/knockout/webp/knockout_08.webp",
    "assets/test_images/360p/knockout/webp/knockout_07.webp",
    "assets/test_images/360p/knockout/webp/knockout_06.webp",
    "assets/test_images/360p/knockout/webp/knockout_05.webp",
    "assets/test_images/360p/knockout/webp/knockout_04.webp",
    "assets/test_images/360p/knockout/webp/knockout_03.webp",
    "assets/test_images/360p/knockout/webp/knockout_02.webp",
    "assets/test_images/720p/knockout/knockout_player_1_02.png",
    "assets/test_images/480p/knockout/knockout_3_1_02.png",
    "assets/test_images/720p/knockout/knockout_player_1_01.png",
    "assets/test_images/1080p/ko/knockout_for_player_2_01.png",
]


@pytest.mark.parametrize("image_filename", test_data)
def test_is_knockout(image_filename):
    """Tests OCR for seeing if a winning round or not"""

    image = cv2.imread(image_filename)

    assert image is not None, f"{image_filename} is none"

    winning_frame = vf_cv.WinningFrame()
    winning_frame.set_frame(image)
    DEBUG = False

    assert winning_frame.is_ko(DEBUG) is True, f"not Knockout as expected"


no_knockout_test_data = [
    "assets/test_images/360p/knockout/webp/not_knockout_03.webp",
    "assets/test_images/360p/knockout/webp/not_knockout_02.webp",
    "assets/test_images/360p/knockout/webp/not_knockout_01.webp",
    "assets/test_images/360p/time/35_05.png",
    "assets/test_images/360p/time/33_01.png",
    "assets/test_images/360p/time/30_03.png",
    "assets/test_images/360p/time/27_04.png",
    "assets/test_images/720p/knockout/no_knockout_01.png",
]


@pytest.mark.parametrize("image_filename", no_knockout_test_data)
def test_is_not_knockout(image_filename):
    image = cv2.imread(image_filename)

    assert image is not None, f"{image_filename} is none"

    winning_frame = vf_cv.WinningFrame()
    winning_frame.set_frame(image)
    DEBUG = False

    assert winning_frame.is_excellent(DEBUG) is False, f"is unexpectedly excellent"
    assert winning_frame.is_ko(DEBUG) is False, f"is unexpectedly knockout"
    assert winning_frame.is_ringout(DEBUG) is False, f"is unexpectedly ringout"
