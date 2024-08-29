import pytest
import cv2
import vf_analytics
    
test_data = [    
    "assets/test_images/480p/knockout/no_knockout_09.png"
]

@pytest.mark.parametrize("image_filename", test_data)
def test_is_not_winning_round(image_filename):
    """Tests OCR for seeing if a winning round or not"""
    
    image = cv2.imread(image_filename)

    assert image is not None, f"{image_filename} is none"

    height = image.shape[0]  # Get the dimensions of the frame
    vf_analytics.resolution=f"{height}p"

    assert vf_analytics.is_winning_round(image) == False, f"{image_filename} is unexpectedly winning round"