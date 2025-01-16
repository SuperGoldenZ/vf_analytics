"""Test ability to get player rank from the VS screen"""

import pytest
import cv2
import vf_cv

test_data = [
    ["assets/test_images/1080p/rank/webp/31_25_small.webp", 31, 25, False],
    ["assets/test_images/1080p/rank/webp/26_31.webp", 26, 31, False],
    ["assets/test_images/1080p/rank/webp/32_34.webp", 32, 34, False],
    ["assets/test_images/1080p/rank/webp/42_46_01.webp", 42, 46, False],
    ["assets/test_images/1080p/rank/webp/26_42.webp", 26, 42, False],
    ["assets/test_images/1080p/rank/webp/13_11_02.webp", 13, 11, False],
    ["assets/test_images/1080p/rank/webp/15_14_01.webp", 15, 14, False],
    ["assets/test_images/1080p/rank/webp/27_27_01.webp", 27, 27, False],
    ["assets/test_images/1080p/rank/webp/23_21_01.webp", 23, 21, False],
    ["assets/test_images/1080p/rank/webp/11_13_01.webp", 11, 13, False],
    ["assets/test_images/1080p/rank/webp/8_6_01.webp", 8, 6, False],
    ["assets/test_images/720p/rank/webp/11_12_01.webp", 11, 12, False],
    ["assets/test_images/720p/rank/webp/14_11_01.webp", 14, 11, False],
    ["assets/test_images/720p/rank/webp/19_22_01.webp", 19, 22, False],
    ["assets/test_images/720p/rank/webp/19_21_01.webp", 19, 21, False],
    ["assets/test_images/720p/rank/webp/11_9_01.webp", 11, 9, False],
    ["assets/test_images/720p/rank/webp/7_6_01.webp", 7, 6, False],
    ["assets/test_images/720p/rank/webp/9_9_01.webp", 9, 9, False],
    ["assets/test_images/720p/rank/webp/5_7_01.webp", 6, 4, False],
    ["assets/test_images/720p/rank/webp/5_8_01.webp", 5, 8, False],
    ["assets/test_images/720p/rank/webp/6_9_01.webp", 5, 2, False],
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
