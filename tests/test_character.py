"""Tests for getting the character name from the VS screen"""

import pytest
import cv2
import vf_cv


test_data = [
    ["assets/test_images/1080p/characters/webp/shun_vs_akira.webp", "Shun", "Akira"],
    ["assets/test_images/1080p/characters/webp/akira_vs_jacky.webp", "Akira", "Jacky"],
    ["assets/test_images/1080p/characters/webp/goh_vs_kage.webp", "Goh", "Kage"],
    ["assets/test_images/1080p/characters/webp/wolf_vs_shun.webp", "Wolf", "Shun"],
]


@pytest.mark.parametrize(
    "image_filename, expected_player_1_character, expected_player_2_character",
    test_data,
)
def test_get_player_character(
    image_filename,
    expected_player_1_character,
    expected_player_2_character,
):
    frame = cv2.imread(image_filename)
    character = vf_cv.Character()

    character.set_frame(frame)

    DEBUG = False
    player1_character = character.get_character_name(1, DEBUG)

    assert (
        player1_character == expected_player_1_character
    ), f"{image_filename} p1 {expected_player_1_character} but got {player1_character}"

    player2_character = character.get_character_name(2, DEBUG)
    assert (
        player2_character == expected_player_2_character
    ), f"{image_filename} p2 {expected_player_2_character} but got {player2_character}"
