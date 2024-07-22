import unittest
import cv2
import vf_analytics
import time

class TestVFCVTekken(unittest.TestCase):                    

    def test_is_ro_tekken(self):
        param_sets = [
            ["assets/test_images/480p/rounds_won/tekken/1_1_01.jpg", False]
            ,["assets/test_images/480p/rounds_won/tekken/2_0_01.jpg", False]
            ,["assets/test_images/480p/rounds_won/tekken/1_1_02.jpg", False]
            ,["assets/test_images/480p/rounds_won/tekken/2_2_01.jpg", True]
        ]

        vf_analytics.resolution="480p"
        for params in param_sets:    
            frame = cv2.imread(params[0])
            frame = vf_analytics.remove_black_border(frame, resize_height=480)
            result = vf_analytics.is_ringout(frame)
            self.assertEqual(params[1], result, f"expected {params[0]} ro = {params[1]}")


    def test_is_ko_tekken(self):
        param_sets = [
            ["assets/test_images/480p/rounds_won/tekken/1_1_01.jpg", True]
            ,["assets/test_images/480p/rounds_won/tekken/2_0_01.jpg", True]
            ,["assets/test_images/480p/rounds_won/tekken/1_1_02.jpg", False]
            ,["assets/test_images/480p/rounds_won/tekken/2_2_01.jpg", False]
        ]

        vf_analytics.resolution="480p"
        for params in param_sets:    
            frame = cv2.imread(params[0])
            frame = vf_analytics.remove_black_border(frame, resize_height=480)
            result = vf_analytics.is_ko(frame)
            self.assertEqual(params[1], result, f"expected {params[0]} ko = {params[1]}")

    def test_is_excellent_tekken(self):
        param_sets = [
            ["assets/test_images/480p/rounds_won/tekken/1_1_01.jpg", False]
            ,["assets/test_images/480p/rounds_won/tekken/2_0_01.jpg", False]
            ,["assets/test_images/480p/rounds_won/tekken/1_1_02.jpg", True]
        ]

        vf_analytics.resolution="480p"
        for params in param_sets:    
            frame = cv2.imread(params[0])
            frame = vf_analytics.remove_black_border(frame, resize_height=480)
            result = vf_analytics.is_excellent(frame)
            self.assertEqual(params[1], result, f"expected {params[0]} excellent = {params[1]}")

    def test_rounds_won_tekken(self):        
        return
        param_sets = [
            ["assets/test_images/480p/rounds_won/tekken/1_1_01.jpg", 1, 1]
            ,["assets/test_images/480p/rounds_won/tekken/1_1_02.jpg", 1, 1]
            ,["assets/test_images/480p/rounds_won/tekken/2_0_01.jpg", 2, 0]
            ,["assets/test_images/480p/rounds_won/tekken/2_1_01.jpg", 2, 1]
            ,["assets/test_images/480p/rounds_won/tekken/2_2_01.jpg", 2, 2]
            ,["assets/test_images/480p/rounds_won/tekken/2_3_01.jpg", 2, 3]
            ,["assets/test_images/480p/rounds_won/tekken/3_0_01.jpg", 3, 0]
        ]

        vf_analytics.resolution="480p"
        for params in param_sets:    
            filename = params[0]

            frame = cv2.imread(filename)            
            frame = vf_analytics.remove_black_border(frame, resize_height=480)

            result = vf_analytics.count_rounds_won(frame, 1, wonSoFar=abs(params[1]-1))
            self.assertEqual(params[1], result, f"expected {filename} to be {params[1]} wins for player 1")

            result = vf_analytics.count_rounds_won(frame, 2, wonSoFar=abs(params[2]-1))
            self.assertEqual(params[2], result, f"expected {filename} to be {params[2]} wins for player 2")