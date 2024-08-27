import pytest
import cv2
import vf_analytics

def test_excellent():
        param_sets = [            
            ["assets/test_images/480p/time/45_00_02.png", "45", "00"],
            ["assets/test_images/480p/time/45_00.png", "45", "00"],
            ["assets/test_images/480p/time/no_time_01.png", "", "00"],
            ["assets/test_images/480p/time/18_00_01.png", "18", "00"],
            ["assets/test_images/480p/time/42_75.png", "42", "76"],
            ["assets/test_images/480p/time/43_45.png", "43", "46"],
            ["assets/test_images/480p/time/16_75.png", "16", "76"],
            ["assets/test_images/480p/time/20_16.png", "20", "16"],
            ["assets/test_images/480p/time/29_66.png", "29", "66"],
            ["assets/test_images/480p/time/24_76.png", "24", "76"],
            ["assets/test_images/480p/time/30_56.png", "30", "68"],
            ["assets/test_images/480p/time/41_26.png", "41", "26"],
            ["assets/test_images/480p/time/44_06.png", "44", "06"],         
            ["assets/test_images/480p/time/44_18.png", "44", "16"],                    
            ["assets/test_images/480p/time/40_16.png", "40", "16"],            
            ["assets/test_images/480p/time/40_66.png", "40", "66"],
            ["assets/test_images/480p/time/40_76.png", "40", "76"],            
            ["assets/test_images/480p/time/39_46.png", "39", "46"],            
            ["assets/test_images/480p/time/39_88.png", "39", "66"],   
            ["assets/test_images/480p/time/37_78.png", "37", "76"],         
            ["assets/test_images/480p/time/36_88.png", "36", "66"],            
            ["assets/test_images/480p/time/22_76.png", "22", "76"],
            ["assets/test_images/480p/time/30_96.png", "30", "96"],
            ["assets/test_images/480p/time/31_16.png", "31", "16"],
            ["assets/test_images/480p/time/32_36.png", "32", "36"],
            ["assets/test_images/480p/time/33_36.png", "33", "36"],
            ["assets/test_images/480p/time/33_18.png", "33", "18"],
            ["assets/test_images/480p/time/34_96.png", "34", "28"],
            ["assets/test_images/480p/time/35_28.png", "35", "28"],            
            ["assets/test_images/480p/time/37_68.png", "37", "68"],
            ["assets/test_images/480p/time/38_26.png", "38", "26"],            
            ["assets/test_images/480p/time/41_78.png", "41", "78"],            
            ["assets/test_images/480p/time/43_96.png", "43", "96"]
        ]
        vf_analytics.resolution="480p"
        for params in param_sets:            
            image = cv2.imread(params[0])
            assert image is not None