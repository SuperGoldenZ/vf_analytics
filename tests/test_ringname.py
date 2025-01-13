import pytest
import cv2
import vf_cv.vs_screen

test_data = [    
    ["assets/test_images/720p/characters/akira_vs_akira_01.png", "Chaos", "DB"],
    ["assets/test_images/1080p/ringname/japanese_01.png", "べペ    ル", "峰ちゃん"],
    ["assets/test_images/1080p/vs/vs_02.png", "masadamono", "chibaken_tv"],
    ["assets/test_images/1080p/vs/vs_03.png", "joechou222", "take4vf"],
]

@pytest.mark.parametrize("image_filename, expected_p1_ringname, expected_p2_ringname", test_data)
def test_is_vs(image_filename, expected_p1_ringname, expected_p2_ringname):
    vs_image = cv2.imread(image_filename)

    assert vs_image is not None

    debug = False
    vs_screen = vf_cv.vs_screen.VsScreen()
    
    vs_screen.set_frame(vs_image)
    
    p1ringname = vs_screen.get_ringname(1, debug)
    
    assert (
        p1ringname == expected_p1_ringname
    ), f"{image_filename} p1ringname is unexpectedly {p1ringname}"


    p2ringname = vs_screen.get_ringname(2, debug)
    assert (
        p2ringname == expected_p2_ringname
    ), f"{image_filename} p1ringname is unexpectedly {p2ringname}"
