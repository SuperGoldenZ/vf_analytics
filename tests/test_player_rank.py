import pytest
import cv2
import vf_cv
import vf_analytics

test_data = [
    # work on this characer and data
    # for video ZQoYcM3e8Hw
    ["assets/test_images/720p/rank/11_12_01.png", 11, 12, False],
    ["assets/test_images/720p/rank/14_11_01.png", 14, 11, False],
    ["assets/test_images/720p/rank/19_22_01.png", 19, 22, False],
    ["assets/test_images/720p/rank/19_21_01.png", 19, 21, False],
    ["assets/test_images/720p/rank/11_9_01.png", 11, 9, False],
    ["assets/test_images/720p/rank/7_6_01.png", 7, 6, False],
    ["assets/test_images/720p/rank/9_9_01.png", 9, 9, False],
    ["assets/test_images/720p/rank/5_7_01.png", 6, 4, False],
    ["assets/test_images/720p/rank/5_8_01.png", 5, 8, False],
    ["assets/test_images/1080p/rank/13_11_02.png", 13, 11, False],
    ["assets/test_images/720p/rank/6_9_01.png", 5, 2, False],
    ["assets/test_images/1080p/rank/15_14_01.png", 15, 14, False],
    ["assets/test_images/1080p/rank/27_27_01.png", 27, 27, False],
    ["assets/test_images/1080p/rank/23_21_01.png", 23, 21, False],
    ["assets/test_images/1080p/rank/11_13_01.png", 11, 13, False],
    ["assets/test_images/1080p/rank/8_6_01.png", 8, 6, False],
    #    ["assets/test_images/360p/rank/42_40_01.png", 42, 40],
    #    ["assets/test_images/360p/rank/42_41_01.png", 42, 41],
    #    ["assets/test_images/360p/rank/45_43_01.png", 45, 43],
    #    ["assets/test_images/360p/rank/43_43_01.png", 43, 43],
    #    ["assets/test_images/360p/rank/41_41_01.png", 41, 41],
    #    ["assets/test_images/360p/rank/40_40_01.png", 40, 40],
    #    ["assets/test_images/360p/rank/44_44_01.png", 44, 44],
    #    ["assets/test_images/360p/rank/40_41_02.png", 40, 41],
    #    ["assets/test_images/360p/rank/40_41_01.png", 40, 41],
    #    ["assets/test_images/360p/rank/41_40_01.png", 41, 40],
    #    ["assets/test_images/360p/rank/41_43_02.png", 41, 43],
    #    ["assets/test_images/360p/rank/41_42_01.png", 41, 42],
    #    ["assets/test_images/360p/rank/44_41_01.png", 44, 41],
    #    ["assets/test_images/360p/rank/41_43_01.png", 41, 43],
    #    ["assets/test_images/360p/rank/40_42_01.png", 40, 42],
    #    ["assets/test_images/360p/rank/42_41_01.png", 42, 41],
    #    ["assets/test_images/480p/rank/42_39_001.jpg", 42, 39],
    #    ["assets/test_images/720p/rank/6996_0_1_41_Lei Fei_vs_0_Brad_knockout_for_player1_18.38.png", 41, 44],
    #
    #    ["assets/test_images/1080p/rank/42_41_01.png", 42, 41],
    #    ["assets/test_images/1080p/rank/40_41_01.png", 40, 41],
    #
    #    ["assets/test_images/720p/rank/44_41_01.png", 44, 41],
    #    ["assets/test_images/720p/rank/44_44_01.png", 44, 44],
    #    ["assets/test_images/720p/characters/lion_vs_vanessa_01.png", 44, 41],
    #
    #
    #    ["assets/test_images/1080p/rank/42_43_01.png", 42, 43],
    #    ["assets/test_images/1080p/rank/43_41_01.png", 43, 41],
    #    ["assets/test_images/1080p/rank/43_42_01.png", 43, 42],
    #
    #    ["assets/test_images/720p/rank/41_41_01.png", 41, 41],
    #    ["assets/test_images/720p/rank/42_41_01.png", 42, 41],
    #    ["assets/test_images/720p/rank/42_41_02.png", 42, 41],
    #    ["assets/test_images/720p/rank/3121__rank_0_for_player2.png", 42, 44],
    #    ["assets/test_images/720p/rank/41_43_02.png", 41, 43],
    #    ["assets/test_images/720p/rank/42_44_01.png", 42, 44],
    #    ["assets/test_images/720p/rank/44_43_01.png", 44, 43],
    #    ["assets/test_images/720p/rank/41_43_01.png", 41, 43],
    #    ["assets/test_images/720p/rank/41_44_01.png", 41, 44],
    #    ["assets/test_images/720p/rank/41_43_01.png", 41, 43],
    #    ["assets/test_images/480p/rank/42_42_001.jpg", 42, 42],
    #    ["assets/test_images/480p/rank/40_40_001.jpg", 40, 40],
    #    ["assets/test_images/480p/rank/44_44_001.jpg", 44, 44],
    #    ["assets/test_images/480p/rank/44_44_002.jpg", 44, 44],
    #    ["assets/test_images/480p/rank/43_44_001.jpg", 43, 44],
    #    ["assets/test_images/480p/rank/43_43_002.jpg", 43, 43],
    #    ["assets/test_images/480p/rank/43_44_002.jpg", 43, 44],
    #    ["assets/test_images/480p/rank/43_44_003.jpg", 43, 44],
    #    ["assets/test_images/480p/rank/43_46_001.jpg", 43, 46],
    #    ["assets/test_images/480p/rank/37_36_001.jpg", 37, 36],
    #    ["assets/test_images/480p/rank/36_37_001.jpg", 36, 37],
    #    ["assets/test_images/480p/rank/32_33_001.jpg", 32, 33],
    #    ["assets/test_images/480p/rank/33_30_001.jpg", 33, 30],
    #    ["assets/test_images/480p/rank/36_33_001.jpg", 36, 33],
    #    ["assets/test_images/480p/rank/33_34_001.jpg", 33, 34],
    #    ["assets/test_images/480p/rank/41_41_001.jpg", 41, 41],
    #    ["assets/test_images/480p/rank/44_42_001.jpg", 44, 42],
    #    ["assets/test_images/480p/rank/42_43_001.jpg", 42, 43],
    #    ["assets/test_images/480p/rank/42_43_002.jpg", 42, 43],
    #    ["assets/test_images/480p/rank/43_43_001.jpg", 43, 43],
    #    ["assets/test_images/480p/rank/31_30_001.jpg", 31, 30],
    #    ["assets/test_images/480p/rank/27_24_001.jpg", 27, 24],
    #    ["assets/test_images/480p/rank/30_30_001.jpg", 30, 30],
    #    ["assets/test_images/480p/rank/41_40_01.png", 41, 40],
]


@pytest.mark.parametrize(
    "image_filename, expected_player_1_rank, expected_player_2_rank, debug",
    test_data,
)
def test_get_player_rank(
    image_filename, expected_player_1_rank, expected_player_2_rank, debug
):
    frame = cv2.imread(image_filename)
    player_rank = vf_cv.PlayerRank()

    player_rank.set_frame(frame)

    rank = player_rank.get_player_rank(1, debug)
    assert (
        expected_player_1_rank == rank
    ), f"Failed for {image_filename} player 1 expected {expected_player_1_rank} but got {rank}"

    rank = player_rank.get_player_rank(2, debug)
    assert (
        expected_player_2_rank == rank
    ), f"Failed for {image_filename} player 2 expected {expected_player_2_rank} but got {rank}"
