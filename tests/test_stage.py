import pytest
import cv2
import os
import vf_cv.vs_screen

test_data = [    
    ["assets/test_images/720p/vs/snow_mountain.png", "Snow Mountain"],
    ["assets/test_images/720p/vs/statues.png", "Statues"],
    ["assets/test_images/720p/vs/statues_02.png", "Statues"],
    #["assets/test_images/480p/main_menu.png", None],
    ["assets/test_images/480p/stage/deep_mountain.png", "Deep Mountain"],
    ["assets/test_images/1080p/stage/snow_mountain.jpg", "Snow Mountain"],
    ["assets/test_images/480p/stage/genesis.png", "Genesis"],
    ["assets/test_images/480p/stage/city.jpg", "City"],
    ["assets/test_images/480p/stage/terrace.png", "Terrace"],
    ["assets/test_images/480p/stage/sumo_ring.png", "Sumo Ring"],
    ["assets/test_images/480p/stage/training_room.png", "Training Room"],
    ["assets/test_images/480p/stage/aurora.png", "Aurora"],
    #["assets/test_images/480p/stage/none_01.png", None],
    ["assets/test_images/360p/stage/snow_mountain.jpg", "Snow Mountain"],
    ["assets/test_images/stage/training_room.jpg", "Training Room"],    
    ["assets/test_images/stage/shrine.jpg", "Shrine"],    
    ["assets/test_images/stage/genesis.png", "Genesis"],
    ["assets/test_images/stage/broken_house.png", "Broken House"],
    ["assets/test_images/stage/broken_house.png", "Broken House"],    
    ["assets/test_images/stage/snow.png", "Snow Mountain"],
    ["assets/test_images/stage/terrace02.png", "Terrace"],
    ["assets/test_images/vs_pai.png", "Statues"],
    ["assets/test_images/vs_akira.png", "Great Wall"],
]

@pytest.mark.parametrize("image_filename, expected_stage_name", test_data)
def test_get_stage(image_filename, expected_stage_name):
    """Tests OCR for seeing if a winning round or not"""
    
    if (os.path.isfile(image_filename)):    
        
        image = cv2.imread(image_filename)
        assert image is not None

        actual_stage = None

        vs_screen = vf_cv.vs_screen.VsScreen()
        
        vs_screen.set_frame(image)
        
        #roi = vf_analytics.get_stage_roi(image)
        #cv2.imshow("roi", roi)
        #cv2.waitKey()

        DEBUG = True
        actual_stage = vs_screen.get_stage(DEBUG)
        
        assert (
            actual_stage == expected_stage_name
        ), f"got unexpected stage {actual_stage} for expected: {expected_stage_name}"
