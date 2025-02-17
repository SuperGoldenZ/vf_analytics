import cv2
import vf_cv
import pytest
import vf_analytics

test_data = [
    # work on this characer and data
    # for video ZQoYcM3e8Hw
    ["assets/test_images/1080p/rank/png/8_6_01.png", 8, 6],
    ["assets/test_images/1080p/rank/png/13_11_02.png", 13, 11],
    ["assets/test_images/1080p/rank/png/28_29.png", 28, 29],
    ["assets/test_images/1080p/rank/png/31_25.png", 31, 25],
    ["assets/test_images/1080p/rank/png/32_34.png", 32, 34],
    ["assets/test_images/1080p/rank/png/38_40.png", 38, 40],
    
    #####################
    # ["assets/test_images/1080p/rank/png/42_43_01.png", 42, 43],
    # ["assets/test_images/1080p/rank/png/43_41_01.png", 43, 41],
    # ["assets/test_images/720p/rank/6996_0_1_41_Lei Fei_vs_0_Brad_knockout_for_player1_18.38.png",41,44,],
    # ["assets/test_images/1080p/rank/42_41_01.png", 42, 41],
    # ["assets/test_images/1080p/rank/40_41_01.png", 40, 41],
    # ["assets/test_images/720p/rank/44_41_01.png", 44, 41],
    # ["assets/test_images/720p/rank/44_44_01.png", 44, 44],
    # ["assets/test_images/720p/characters/lion_vs_vanessa_01.png", 44, 41],
    # ["assets/test_images/1080p/rank/43_42_01.png", 43, 42],
    # ["assets/test_images/720p/rank/41_41_01.png", 41, 41],
    # ["assets/test_images/720p/rank/42_41_01.png", 42, 41],
    # ["assets/test_images/720p/rank/42_41_02.png", 42, 41],
    # ["assets/test_images/720p/rank/3121__rank_0_for_player2.png", 42, 44],
    # ["assets/test_images/720p/rank/41_43_02.png", 41, 43],
    # ["assets/test_images/720p/rank/42_44_01.png", 42, 44],
    # ["assets/test_images/720p/rank/44_43_01.png", 44, 43],
    # ["assets/test_images/720p/rank/41_43_01.png", 41, 43],
    # ["assets/test_images/720p/rank/41_44_01.png", 41, 44],
    # ["assets/test_images/720p/rank/41_43_01.png", 41, 43],
]


@pytest.mark.parametrize(
    "image_filename, expected_player_1_rank, expected_player_2_rank",
    test_data,
)
def test_get_player_rank(
    image_filename,
    expected_player_1_rank,
    expected_player_2_rank,
):
    frame = cv2.imread(image_filename)
    player_rank = vf_cv.PlayerRank()

    player_rank.set_frame(frame)

    DEBUG = True
    rank = player_rank.get_player_rank(1, DEBUG)
    assert (
        expected_player_1_rank == rank
    ), f"Failed for {image_filename} player 1 expected {expected_player_1_rank} but got {rank}"

    rank = player_rank.get_player_rank(2, DEBUG)
    assert (
        expected_player_2_rank == rank
    ), f"Failed for {image_filename} player 2 expected {expected_player_2_rank} but got {rank}"
