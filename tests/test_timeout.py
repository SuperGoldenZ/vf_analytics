import pytest
import cv2
import vf_cv

test_data = [
    "assets/test_images/720p/timeout/timeout_03.png",
    "assets/test_images/720p/timeout/timeout_04.png",
    "assets/test_images/720p/timeout/timeout_05.png",
    "assets/test_images/720p/timeout/timeout_06.png",
    "assets/test_images/720p/timeout/timeout_02.png",
    "assets/test_images/720p/timeout/timeout_01.png",
    "assets/test_images/360p/timeout/timeout_01.png",
]


@pytest.mark.parametrize("image_filename", test_data)
def test_ringout(image_filename):
    """Tests OCR for seeing if a winning round or not"""

    image = cv2.imread(image_filename)

    assert image is not None, f"{image_filename} is none"

    winning_frame = vf_cv.WinningFrame()
    winning_frame.set_frame(image)

    debug=False

    assert (
        winning_frame.is_timeout(debug) is True
    ), f"{image_filename} is not timeout as expected"