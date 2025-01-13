import pytest
import cv2
import vf_cv

test_data = [
    "assets/test_images/1080p/ring_out/ringout_05.png",
    "assets/test_images/1080p/ring_out/ringout_04.png",
    "assets/test_images/1080p/ring_out/ringout_03.png",
    "assets/test_images/1080p/ring_out/ringout_02.png",
    "assets/test_images/360p/ringout/ringout_05.png",
    "assets/test_images/360p/ringout/ringout_02.png",
    "assets/test_images/360p/ringout/ringout_01.png",
    "assets/test_images/1080p/ring_out/ringout_01.png",
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
        winning_frame.is_ringout(debug) is True
    ), f"{image_filename} is not ringout as expected"

test_data=[
    "assets/test_images/360p/ringout/not_ringout_03.png",
    "assets/test_images/360p/ringout/not_ringout_02.png",
    "assets/test_images/360p/ringout/not_ringout_01.png",
    "assets/test_images/360p/ringout/ringout_03.png",
    "assets/test_images/360p/time/35_05.png"
]

@pytest.mark.parametrize("image_filename", test_data)
def test_not_ringout(image_filename):
    """Tests OCR for seeing if a winning round or not"""

    image = cv2.imread(image_filename)

    assert image is not None, f"{image_filename} is none"

    winning_frame = vf_cv.WinningFrame()
    winning_frame.set_frame(image)

    debug=False

    assert (
        winning_frame.is_ringout(debug) is False
    ), f"{image_filename} is unexpectedly ringout"
