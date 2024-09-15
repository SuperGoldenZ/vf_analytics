import pytest
import cv2
import vf_cv

test_data = [
    "assets/test_images/720p/winning_frame/not_winning_frame_01.png",
    "assets/test_images/1080p/winning_frame/not_winning_frame_06.png",
    "assets/test_images/1080p/winning_frame/not_winning_frame_04.png",
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
    ), f"{image_filename} is unexpectedly winning frame"


test_data = [
    ["assets/test_images/1080p/ko/knockout_for_player_2_02.png", 2],
    ["assets/test_images/1080p/ko/knockout_for_player_1_01.png", 1],
    ["assets/test_images/1080p/ko/knockout_for_player_2_01.png", 2],
]


@pytest.mark.parametrize("image_filename, winning_player", test_data)
def test_is_winning_round(image_filename, winning_player):
    """Tests OCR for seeing if a winning round or not"""

    image = cv2.imread(image_filename)

    assert image is not None, f"{image_filename} is none"

    winning_round = vf_cv.WinningRound()
    winning_round.set_frame(image)

    DEBUG = False
    actual_winnner = winning_round.is_winning_round(DEBUG)
    assert (
        actual_winnner == winning_player
    ), f"{image_filename} is {actual_winnner} not {winning_player} as expected"
