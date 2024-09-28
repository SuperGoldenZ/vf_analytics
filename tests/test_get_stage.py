import pytest
import cv2
import vf_analytics
import traceback

test_data = [
    ["assets/test_images/720p/stage/ruins_01.png", "Ruins"],
    ["assets/test_images/480p/main_menu.png", None],
    ["assets/test_images/480p/stage/deep_mountain.png", "Deep Mountain"],
    ["assets/test_images/480p/stage/genesis.png", "Genesis"],
    ["assets/test_images/480p/stage/city.jpg", "City"],
    ["assets/test_images/480p/stage/terrace.png", "Terrace"],
    ["assets/test_images/480p/stage/sumo_ring.png", "Sumo Ring"],
    ["assets/test_images/480p/stage/training_room.png", "Training Room"],
    ["assets/test_images/480p/stage/island_01.jpg", "Island"],
    ["assets/test_images/480p/stage/island_02.jpg", "Island"],
    ["assets/test_images/480p/stage/island_03.jpg", "Island"],
    ["assets/test_images/480p/stage/genesis.png", "Genesis"],
    ["assets/test_images/480p/stage/aurora.png", "Aurora"],
    ["assets/test_images/480p/stage/terrace.png", "Terrace"],
    ["assets/test_images/480p/stage/shrine.png", "Shrine"],
    ["assets/test_images/480p/stage/sumo_ring.png", "Sumo Ring"],
    ["assets/test_images/480p/stage/training_room.png", "Training Room"],
    ["assets/test_images/480p/stage/waterfalls.png", "Waterfalls"],
    ["assets/test_images/480p/stage/aurora.png", "Aurora"],
    ["assets/test_images/480p/stage/shrine.png", "Shrine"],
    ["assets/test_images/480p/stage/waterfalls.png", "Waterfalls"],
    ["assets/test_images/480p/stage/city.jpg", "City"],
]


@pytest.mark.parametrize("image_filename, expected_stage_name", test_data)
def test_get_stage(image_filename, expected_stage_name):
    vs_image = cv2.imread(image_filename)

    assert vs_image is not None, f"{image_filename} is unexpectedly none"

    try:
        DEBUG_STAGE = False
        stage = vf_analytics.get_stage(vs_image, DEBUG_STAGE)
        assert expected_stage_name == stage

    except Exception as a:
        assert False, f"Test failed because of exception {a} {traceback.format_exc()}"
