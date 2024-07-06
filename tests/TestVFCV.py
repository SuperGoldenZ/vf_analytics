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
        self.assertEquals(2, vf_analytics.count_rounds_won(vs_image, 1))

        vs_image = cv2.imread('assets/test_images/vanessa_vs_blaze.png')
        self.assertEquals(0, vf_analytics.count_rounds_won(vs_image, 1))