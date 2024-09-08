import pytest
import cv2
import vf_cv

test_data = [
    "assets/test_images/1080p/winning_frame/not_winning_frame_03.png",
    "assets/test_images/1080p/winning_frame/not_winning_frame_02.png",
    "assets/test_images/1080p/winning_frame/not_winning_frame_01.png",
    "assets/test_images/480p/winning_frame/not_winning_frame_01.png",
    "assets/test_images/480p/knockout/no_knockout_09.png",
]


@pytest.mark.parametrize("image_filename", test_data)
def test_is_not_winning_round(image_filename):
    """Tests OCR for seeing if a winning round or not"""

    image = cv2.imread(image_filename)

    assert image is not None, f"{image_filename} is none"

    winning_round = vf_cv.WinningRound()
    winning_round.set_frame(image)

    DEBUG = False
    assert (
        winning_round.is_winning_round(DEBUG) == 0
    ), f"{image_filename} is unexpectedly winning round"
