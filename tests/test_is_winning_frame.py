import pytest
import cv2
import vf_cv

test_data = [
    "assets/test_images/360p/time/4054_fight_36_winning_unknown2.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_17.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_16.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_15.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_14.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_13.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_12.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_11.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_10.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_09.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_08.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_07.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_06.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_05.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_04.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_03.png",
    "assets/test_images/720p/winning_frame/not_winning_frame_02.png",
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
    ["assets/test_images/720p/ringout/ro_01.png", 1, "Sumo Ring"],
    ["assets/test_images/720p/excellent/excellent_01.png", 2, "Aurora"],
    ["assets/test_images/720p/winning_frame/ko_02.png", 2, "River"],
    ["assets/test_images/360p/knockout/knockout_48.png", 2, "City"],
    ["assets/test_images/360p/knockout/knockout_47.png", 1, "Grassland"],
    ["assets/test_images/360p/knockout/knockout_46.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_45.png", 1, "Grassland"],
    ["assets/test_images/360p/knockout/knockout_44.png", 2, "River"],
    ["assets/test_images/360p/time/42_03.png", 0, "City"],
    ["assets/test_images/360p/ringout/ringout_04.png", 1, "Sumo Ring"],
    ["assets/test_images/360p/time/35_06.png", 0, "Sumo Ring"],
    ["assets/test_images/360p/knockout/knockout_43.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_20.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_24.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_25.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_26.png", 1, None],    
    ["assets/test_images/360p/knockout/knockout_33.png", 1, "City"],
    ["assets/test_images/360p/knockout/knockout_42.png", 2, "Island"],
    ["assets/test_images/360p/ringout/ringout_03.png", 0, "Temple"],
    ["assets/test_images/360p/knockout/knockout_41.png", 2, None],
    ["assets/test_images/360p/knockout/knockout_40.png", 2, None],
    ["assets/test_images/360p/time/35_05.png",0, "Island"],
    ["assets/test_images/360p/time/40_03.png",0, "Island"],
    ["assets/test_images/360p/knockout/knockout_40.png", 2, None],
    ["assets/test_images/360p/knockout/knockout_39.png", 2, None],
    ["assets/test_images/360p/excellent/excellent_05.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_36.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_35.png", 2, None],
    ["assets/test_images/360p/knockout/knockout_34.png", 1, "City"],    
    ["assets/test_images/360p/knockout/knockout_30.png", 2, "Temple"],    
    ["assets/test_images/360p/time/40_03.png", 0, "Island"],            
    ["assets/test_images/360p/knockout/knockout_08.png", 2, None],    
    ["assets/test_images/360p/knockout/knockout_23.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_22.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_21.png", 1, None],    
    ["assets/test_images/360p/knockout/knockout_19.png", 2, None],
    ["assets/test_images/360p/knockout/knockout_18.png", 2, None],
    ["assets/test_images/360p/knockout/knockout_17.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_16.png", 2, None],
    ["assets/test_images/360p/knockout/knockout_15.png", 2, None],
    ["assets/test_images/360p/knockout/knockout_14.png", 2, None],
    ["assets/test_images/360p/knockout/knockout_13.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_12.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_11.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_10.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_09.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_07.png", 1, None],
    ["assets/test_images/360p/ringout/ringout_02.png",   2, None],
    ["assets/test_images/360p/knockout/knockout_06.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_04.png", 1, None],
    ["assets/test_images/360p/knockout/knockout_03.png", 2, None],
    ["assets/test_images/360p/knockout/knockout_02.png", 2, None],
    [
        "assets/test_images/480p/knockout/3931_0_1_43_Lei Fei_vs_42_Akira_knockout_for_player1_16.00.png",
        0, None
    ],
    ["assets/test_images/480p/knockout/1139_fight_32_no_match_advance.png", 2, None],
    ["assets/test_images/480p/knockout/knockout_1_01.png", 1, None],
    ["assets/test_images/720p/knockout/knockout_player_1_03.png", 1, None],
    ["assets/test_images/720p/knockout/knockout_player_1_02.png", 1, None],
    ["assets/test_images/480p/knockout/knockout_3_1_03.png", 1, None],
    ["assets/test_images/480p/knockout/knockout_3_1_02.png", 1, None],
    ["assets/test_images/720p/winning_frame/ko_01.png", 1, None],
    ["assets/test_images/1080p/ko/knockout_for_player_2_02.png", 2, None],
    ["assets/test_images/1080p/ko/knockout_for_player_1_01.png", 1, None],
    ["assets/test_images/1080p/ko/knockout_for_player_2_01.png", 2, None],
]


@pytest.mark.parametrize("image_filename, winning_player, stage", test_data)
def test_is_winning_round(image_filename, winning_player, stage):
    """Tests OCR for seeing if a winning round or not"""

    image = cv2.imread(image_filename)

    assert image is not None, f"{image_filename} is none"

    winning_round = vf_cv.WinningRound()
    winning_round.set_frame(image)

    DEBUG = True
    actual_winnner = winning_round.is_winning_round(DEBUG, stage)
    assert (
        actual_winnner == winning_player
    ), f"{image_filename} is {actual_winnner} not {winning_player} as expected"
