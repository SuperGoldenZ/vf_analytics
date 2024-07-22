import unittest
import cv2
import vf_analytics
import time

class TestVFCVRoundsWon(unittest.TestCase):                          
    def test_rounds_won(self):
        param_sets = [
             ['assets/test_images/480p/knockout/knockout_2_2_01.png', 2, 2, vf_analytics.regions_480p]
            ,['assets/test_images/480p/knockout/knockout_0_1_01.jpg', 0, 1, vf_analytics.regions_480p]
            ,["assets/test_images/480p/excellent/excellent_2_2_01.jpg", 2, 2, vf_analytics.regions_480p]
            ,["assets/test_images/480p/knockout/knockout_1_1_01.png", 1, 1, vf_analytics.regions_480p]
            ,["assets/test_images/480p/knockout/knockout_1_2_01.jpg", 1, 2, vf_analytics.regions_480p]
            ,["assets/test_images/480p/knockout/knockout_1_2_02.jpg", 1, 2, vf_analytics.regions_480p]
            ,["assets/test_images/480p/knockout/knockout_3_0_01.jpg", 3, 0, vf_analytics.regions_480p]
            ,['assets/test_images/480p/rounds_won/0_1_01.jpg', 0, 1, vf_analytics.regions_480p]
#            ,['assets/test_images/480p/rounds_won/0_1_01.png', 0, 1, vf_analytics.regions_480p]
            ,['assets/test_images/480p/ringout/ringout_01.jpg', 0, 3, vf_analytics.regions_480p]
            ,['assets/test_images/480p/ringout/ringout_02.png', 3, 2, vf_analytics.regions_480p]
            ,['assets/test_images/480p/knockout/knockout_01.jpg', 2, 1, vf_analytics.regions_480p]
            ,['assets/test_images/480p/knockout/knockout_02.jpg', 1, 0, vf_analytics.regions_480p]
            ,['assets/test_images/480p/knockout/knockout_03.png', 1, 0, vf_analytics.regions_480p]
            ,['assets/test_images/480p/knockout/knockout_04.png', 1, 1, vf_analytics.regions_480p]
            ,['assets/test_images/480p/knockout/knockout_05.png', 2, 1, vf_analytics.regions_480p]
             #['assets/test_images/480p/rounds_won/round_001.jpg', 1, 0, vf_analytics.regions_480p]             
             #['assets/test_images/480p/rounds_won/1_2_02.jpg', 1, 2, vf_analytics.regions_480p]
            #,['assets/test_images/480p/rounds_won/1_0_01.jpg', 1, 0, vf_analytics.regions_480p]
            #,['assets/test_images/480p/rounds_won/1_0_02.jpg', 1, 0, vf_analytics.regions_480p]
            #,['assets/test_images/480p/rounds_won/2_1_01.jpg', 2, 1, vf_analytics.regions_480p]
            #,['assets/test_images/480p/rounds_won/1_2_01.jpg', 1, 2, vf_analytics.regions_480p]
            #,['assets/test_images/480p/rounds_won/2_1_02.jpg', 2, 1, vf_analytics.regions_480p]
            #,['assets/test_images/480p/rounds_won/2_3_01.jpg', 2, 3, vf_analytics.regions_480p]
            #'assets/test_images/rounds_won/0_2_001.jpg' :2
            #,'assets/test_images/rounds_won/0_0_008.png' :0
            #,'assets/test_images/rounds_won/0_0_009.png' :0
            #,'assets/test_images/rounds_won/0_0_010.png' :0
            #,'assets/test_images/rounds_won/0_0_004.png' :0
            #,'assets/test_images/rounds_won/3_1_001.png' :1
            #,'assets/test_images/rounds_won/0_2_001.png' : 2
            #,'assets/test_images/rounds_won/0_3_001.png':3
            #,'assets/test_images/vanessa_vs_blaze.png' :0
            #,'assets/test_images/player2_one_round_won.png' :1
            #,'assets/test_images/player2_two_round_won.png' :2
        ]
        vf_analytics.resolution = "480p"

        for params in param_sets:    
            filename = params[0]

            vs_image = cv2.imread(filename)
            #print(f"\ncount rounds won {filename}")
            result = vf_analytics.count_rounds_won(vs_image, 1, params[3], abs(params[1]-1))
            self.assertEqual(params[1], result, f"expected {filename} to be {params[1]} wins for player 1")

            result = vf_analytics.count_rounds_won(vs_image, 2, params[3], abs(params[2]-1))
            self.assertEqual(params[2], result, f"expected {filename} to be {params[2]} wins for player 2")