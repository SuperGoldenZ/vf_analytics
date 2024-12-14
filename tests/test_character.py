import pytest
import cv2
import vf_cv
import vf_analytics

test_data = [
    # work on this characer and data
    # for video ZQoYcM3e8Hw    
    ["assets/test_images/360p/characters/kage_vs_wolf_02.png", "Kage", "Wolf"],
    ["assets/test_images/360p/characters/kage_vs_wolf.png", "Kage", "Wolf"],
    ["assets/test_images/360p/characters/leifei_vs_akira.png", "Lei Fei", "Akira"],
    ["assets/test_images/360p/characters/jeff_vs_aoi.png", "Jeffry", "Aoi"],
    ["assets/test_images/360p/characters/wolf_vs_leifei.png", "Wolf", "Lei Fei"],
    ["assets/test_images/360p/characters/wolf_vs_pai.png", "Wolf", "Pai"],
    ["assets/test_images/360p/characters/jean_vs_blaze.png", "Jean", "Blaze"],
    ["assets/test_images/360p/characters/kage_vs_akira.png", "Kage", "Akira"],    
    ["assets/test_images/720p/characters/leifei_vs_jean_01.png", "Lei Fei", "Jean"],
    ["assets/test_images/720p/characters/brad_vs_lion_01.png", "Brad", "Lion"],
    ["assets/test_images/720p/stage/ruins_01.png", "Jean", "Aoi"],
    ["assets/test_images/720p/characters/aoi_vs_jean_01.png", "Aoi", "Jean"],
    ["assets/test_images/720p/characters/taka_vs_jacky_01.png", "Taka", "Jacky"],
    ["assets/test_images/720p/characters/lau_vs_akira_01.png", "Lau", "Akira"],
    ["assets/test_images/720p/characters/pai_vs_jacky_01.png", "Pai", "Jacky"],
    ["assets/test_images/720p/characters/lion_vs_goh_01.png", "Lion", "Goh"],
    ["assets/test_images/720p/characters/akira_vs_kage_01.png", "Akira", "Kage"],
    ["assets/test_images/720p/characters/jean_vs_jacky_01.png", "Jean", "Jacky"],
    ["assets/test_images/720p/characters/lion_vs_vanessa_01.png", "Lion", "Vanessa"],
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

    DEBUG = True
    player1_character = character.get_character_name(1, DEBUG)
    
    
    assert (
        player1_character == expected_player_1_character
    ), f"{image_filename} p1 {expected_player_1_character} but got {player1_character}"

    player2_character = character.get_character_name(2, DEBUG)
    assert (
        player2_character == expected_player_2_character
    ), f"{image_filename} p2 {expected_player_2_character} but got {player2_character}"

    vs = vf_analytics.is_vs(frame, DEBUG)
    assert(vs, "not vs as expected")