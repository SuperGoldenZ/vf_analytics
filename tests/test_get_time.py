import pytest
import cv2
import vf_analytics

test_data = [
    ["assets/test_images/480p/time/45_00_02.png", "45", "00", 480],
    ["assets/test_images/480p/time/45_00.png", "45", "00", 480],
    ["assets/test_images/480p/time/no_time_01.png", "", "00", 480],
    ["assets/test_images/480p/time/18_00_01.png", "18", "00", 480],
    ["assets/test_images/720p/time/42_75.png", "42", "76", 720],
    ["assets/test_images/480p/time/43_45.png", "43", "46", 720],
    ["assets/test_images/480p/time/16_75.png", "16", "76", 720],
    ["assets/test_images/480p/time/20_16.png", "20", "16", 720],
    ["assets/test_images/480p/time/29_66.png", "29", "66", 720],
    ["assets/test_images/480p/time/24_76.png", "24", "76", 720],
    ["assets/test_images/480p/time/30_56.png", "30", "68", 720],
    ["assets/test_images/480p/time/41_26.png", "41", "26", 720],
    ["assets/test_images/480p/time/44_06.png", "44", "06", 720],
    ["assets/test_images/480p/time/44_18.png", "44", "16", 720],
    ["assets/test_images/480p/time/40_16.png", "40", "16", 720],
    ["assets/test_images/480p/time/40_66.png", "40", "66", 720],
    ["assets/test_images/480p/time/40_76.png", "40", "76", 720],
    ["assets/test_images/480p/time/39_46.png", "39", "46", 720],
    ["assets/test_images/480p/time/39_88.png", "39", "66", 720],
    ["assets/test_images/480p/time/37_78.png", "37", "76", 720],
    ["assets/test_images/480p/time/36_88.png", "36", "66", 720],
    ["assets/test_images/480p/time/22_76.png", "22", "76", 720],
    ["assets/test_images/480p/time/30_96.png", "30", "96", 720],
    ["assets/test_images/480p/time/31_16.png", "31", "16", 720],
    ["assets/test_images/480p/time/32_36.png", "32", "36", 720],
    ["assets/test_images/480p/time/33_36.png", "33", "36", 720],
    ["assets/test_images/480p/time/33_18.png", "33", "18", 720],
    ["assets/test_images/480p/time/34_96.png", "34", "28", 720],
    ["assets/test_images/480p/time/35_28.png", "35", "28", 720],
    ["assets/test_images/480p/time/37_68.png", "37", "68", 720],
    ["assets/test_images/480p/time/38_26.png", "38", "26", 720],
    ["assets/test_images/480p/time/41_78.png", "41", "78", 720],
    ["assets/test_images/480p/time/43_96.png", "43", "96", 720]
]

@pytest.mark.parametrize("image_filename, expected_time_seconds, expected_time_ms, resolution", test_data)
def test_time_480p(image_filename, expected_time_seconds, expected_time_ms, resolution):
    """Tests OCR for getting time remaining during a match with 480p resolution"""

    vf_analytics.resolution=f"480p"
    image = cv2.imread(image_filename)

    assert image is not None, f"{image_filename} is none"

    height = image.shape[0]  # Get the dimensions of the frame
    assert height == resolution, f"{image_filename} is {height}p instead of expected {resolution}p"

    actual_time_seconds = vf_analytics.get_time_seconds(image)
    assert expected_time_seconds == actual_time_seconds, f"{actual_time_seconds} not expected value of {expected_time_seconds} for {image_filename}"

    #actual_time_ms = vf_analytics.get_time_ms(image)
    #assert expected_time_ms == actual_time_ms, f"{actual_time_ms} not expected value of {expected_time_ms}"


test_data_digits = [
    ["assets/test_images/720p/time/6.png", 6, 2],
]

@pytest.mark.parametrize("image_filename, expected_digit, digit_num", test_data_digits)
def test_get_digit_720p(image_filename, expected_digit, digit_num):
    """Tests OCR for getting time individual digits"""

    vf_analytics.resolution="480p"
    image = cv2.imread(image_filename)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    threshold_value = 200
    _, thresholded_image = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY)

    height, width = thresholded_image.shape  # Get the dimensions of the frame
    assert image is not None, f"{image_filename} is none"

    actual_digit = vf_analytics.get_time_digit_720p(thresholded_image, width, height, digit_num)

    assert actual_digit == expected_digit, f"{actual_digit} not expected value of {expected_digit} for {image_filename}"
