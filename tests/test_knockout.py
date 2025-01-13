import pytest
import cv2
import vf_cv

test_data = [    
    "assets/test_images/1080p/ko/knockout_for_player_1_06.png",
    "assets/test_images/360p/knockout/knockout_43.png",
    "assets/test_images/360p/knockout/knockout_38.png",
    "assets/test_images/360p/knockout/knockout_37.png",
    "assets/test_images/360p/knockout/knockout_35.png",
    "assets/test_images/360p/knockout/knockout_34.png",
    "assets/test_images/360p/knockout/knockout_31.png",
    "assets/test_images/360p/knockout/knockout_14.png",
    "assets/test_images/360p/knockout/knockout_12.png",
    "assets/test_images/360p/knockout/knockout_11.png",
    "assets/test_images/360p/knockout/knockout_10.png",
    "assets/test_images/360p/knockout/knockout_09.png",
    "assets/test_images/360p/knockout/knockout_08.png",
    "assets/test_images/360p/knockout/knockout_07.png",
    "assets/test_images/360p/knockout/knockout_06.png",
    "assets/test_images/360p/knockout/knockout_05.png",
    "assets/test_images/360p/knockout/knockout_04.png",
    "assets/test_images/360p/knockout/knockout_03.png",
    "assets/test_images/360p/knockout/knockout_02.png",
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
    "assets/test_images/360p/knockout/not_knockout_03.png",
    "assets/test_images/360p/knockout/not_knockout_02.png",
    "assets/test_images/360p/knockout/not_knockout_01.png",
    "assets/test_images/360p/time/35_05.png",
    "assets/test_images/360p/time/33_01.png",
    "assets/test_images/360p/time/30_03.png",
    "assets/test_images/360p/time/27_04.png",
    "assets/test_images/720p/knockout/no_knockout_01.png"]


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
