import unittest
import cv2
import vf_analytics

class TestVFCV(unittest.TestCase):
    def test_is_vs(self):
        vs_image = cv2.imread('assets/test_images/vanessa_vs_blaze.png')
        self.assertTrue(vf_analytics.is_vs(vs_image))

        not_vs_image = cv2.imread('assets/test_images/ko.png')
        self.assertFalse(vf_analytics.is_vs(not_vs_image))

    def test_player1_rounds_won(self):
        vs_image = cv2.imread('assets/test_images/player1_two_rounds_won.png')
        region=vf_analytics.regions['player1rounds']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]
        self.assertEquals(2, vf_analytics.count_rounds_won(roi, 1))

        vs_image = cv2.imread('assets/test_images/vanessa_vs_blaze.png')
        region=vf_analytics.regions['player1rounds']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]
        self.assertEquals(0, vf_analytics.count_rounds_won(roi, 1))

        vs_image = cv2.imread('assets/test_images/player2_one_round_won.png')
        region=vf_analytics.regions['player1rounds']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]
        self.assertEquals(0, vf_analytics.count_rounds_won(roi, 1))
    
    def test_player2_rounds_won(self):
        vs_image = cv2.imread('assets/test_images/vanessa_vs_blaze.png')
        region=vf_analytics.regions['player2rounds']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]
        self.assertEquals(0, vf_analytics.count_rounds_won(roi, 2))

        vs_image = cv2.imread('assets/test_images/player2_one_round_won.png')
        region=vf_analytics.regions['player2rounds']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]
        self.assertEquals(1, vf_analytics.count_rounds_won(roi, 2))        

        vs_image = cv2.imread('assets/test_images/player2_two_round_won.png')
        region=vf_analytics.regions['player2rounds']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]
        self.assertEquals(2, vf_analytics.count_rounds_won(roi, 2))                