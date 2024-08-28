import pytest
import cv2
import vf_analytics

test_data= [
    ['assets/test_images/720p/stage/ruins_01.png', "Ruins"],
    ['assets/test_images/480p/main_menu.png', None],
    ['assets/test_images/480p/stage/deep_mountain.png', "Deep Mountain"],
    ['assets/test_images/480p/stage/genesis.png', "Genesis"],
    ['assets/test_images/480p/stage/city.jpg', "City"],
    ['assets/test_images/480p/stage/terrace.png', "Terrace"],
    ['assets/test_images/480p/stage/sumo_ring.png', "Sumo Ring"],
    ['assets/test_images/480p/stage/training_room.png', "Training Room"],
    ['assets/test_images/480p/stage/island_01.jpg', "Island"],
    ['assets/test_images/480p/stage/island_02.jpg', "Island"],
    ['assets/test_images/480p/stage/island_03.jpg', "Island"],
    ['assets/test_images/480p/stage/genesis.png', "Genesis"],
    ['assets/test_images/480p/stage/aurora.png', "Aurora"],
    ['assets/test_images/480p/stage/terrace.png', "Terrace"],
    ['assets/test_images/480p/stage/shrine.png', "Shrine"],
    ['assets/test_images/480p/stage/sumo_ring.png', "Sumo Ring"],
    ['assets/test_images/480p/stage/training_room.png', "Training Room"],
    ['assets/test_images/480p/stage/waterfalls.png', "Waterfalls"],
    ['assets/test_images/480p/stage/aurora.png', "Aurora"],
    ['assets/test_images/480p/stage/shrine.png', "Shrine"],
    ['assets/test_images/480p/stage/waterfalls.png', "Waterfalls"],
    ['assets/test_images/480p/stage/city.jpg', "City"],

    ["assets/test_images/480p/time/08_00_01.png", None],
    ["assets/test_images/720p/time/08_00_01.png", None],
    ["assets/test_images/720p/time/09_96_01.png", None],    
    ["assets/test_images/720p/time/10_08_01.png", None],
    ["assets/test_images/480p/time/45_00_02.png", None],        
    ["assets/test_images/480p/time/18_00_01.png", None],
    ["assets/test_images/720p/time/42_75.png", None],
    ["assets/test_images/480p/time/43_45.png", None],
    ["assets/test_images/480p/time/16_75.png", None],
    ["assets/test_images/480p/time/20_16.png", None],
    ["assets/test_images/480p/time/29_66.png", None],
    ["assets/test_images/480p/time/24_76.png", None],
    ["assets/test_images/480p/time/30_56.png", None],
    ["assets/test_images/480p/time/41_26.png", None],
    ["assets/test_images/480p/time/44_06.png", None],
    ["assets/test_images/480p/time/44_18.png", None],
    ["assets/test_images/480p/time/40_16.png", None],
    ["assets/test_images/480p/time/40_66.png", None],
    ["assets/test_images/480p/time/40_76.png", None],
    ["assets/test_images/480p/time/39_46.png", None],
    ["assets/test_images/480p/time/39_88.png", None],
    ["assets/test_images/480p/time/37_78.png", None],
    ["assets/test_images/480p/time/36_88.png", None],
    ["assets/test_images/480p/time/22_76.png", None],
    ["assets/test_images/480p/time/30_96.png", None],
    ["assets/test_images/480p/time/31_16.png", None],
    ["assets/test_images/480p/time/32_36.png", None],
    ["assets/test_images/480p/time/33_36.png", None],
    ["assets/test_images/480p/time/33_18.png", None],
    ["assets/test_images/480p/time/34_96.png", None],
    ["assets/test_images/480p/time/35_28.png", None],
    ["assets/test_images/480p/time/37_68.png", None],
    ["assets/test_images/480p/time/38_26.png", None],
    ["assets/test_images/480p/time/41_78.png", None],
    ["assets/test_images/480p/time/43_96.png", None],
]

@pytest.mark.parametrize("image_filename, expected_stage_name", test_data)
def test_is_vs(image_filename, expected_stage_name):
    vs_image = cv2.imread(image_filename)

    assert vs_image is not None

    actual_is_vs=vf_analytics.is_vs(vs_image)
    expected_actual_vs = expected_stage_name is not None
    assert expected_actual_vs == actual_is_vs, f"{image_filename} is_vs unexpectedly {actual_is_vs}"