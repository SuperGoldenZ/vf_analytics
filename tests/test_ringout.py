import pytest
import cv2
import vf_cv

test_data = [
    "assets/test_images/1080p/ring_out/ringout_01.png",
]


@pytest.mark.parametrize("image_filename", test_data)
def test_is_not_winning_round(image_filename):
    """Tests OCR for seeing if a winning round or not"""

    image = cv2.imread(image_filename)

    assert image is not None, f"{image_filename} is none"

    winning_frame = vf_cv.WinningFrame()
    winning_frame.set_frame(image)

    assert (
        winning_frame.is_ringout() is True
    ), f"{image_filename} is not ringout as expected"
