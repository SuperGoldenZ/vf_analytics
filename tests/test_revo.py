import pytest
import cv2
import vf_cv.revo

test_data = [
    ["assets/test_images/1080p/beta.png", True],
    ["assets/test_images/1080p/vs/statues.png", False],
    ["assets/test_images/1080p/vs/vs_01.jpg", False],    
    ["assets/test_images/1080p/ko/knockout_for_player_1_01.png", False],
    ["assets/test_images/1080p/ko/knockout_for_player_2_01.png", False],
]


@pytest.mark.parametrize("image_filename, expected_beta", test_data)
def test_is_vs(image_filename, expected_beta):
    image = cv2.imread(image_filename)

    assert image is not None

    DEBUG = True
    
    actual_is_beta = vf_cv.REVO.is_beta_screen(image, DEBUG)

    assert (
        expected_beta == actual_is_beta
    ), f"{image_filename} is_vs unexpectedly {actual_is_beta}"
