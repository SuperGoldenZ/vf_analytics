import unittest
import cv2
import vf_analytics
import pytesseract

class TestVFCV(unittest.TestCase):
    def test_is_vs(self):
        vs_image = cv2.imread('assets/test_images/vanessa_vs_blaze.png')
        self.assertTrue(vf_analytics.is_vs(vs_image))

        not_vs_image = cv2.imread('assets/test_images/ko.png')
        self.assertFalse(vf_analytics.is_vs(not_vs_image))

    def test_player1_rounds_won(self):
        vs_image = cv2.imread('assets/test_images/player1_two_rounds_won.png')
        region=vf_analytics.regions['player1_rounds']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]
        self.assertEqual(2, vf_analytics.count_rounds_won(roi, 1))

        vs_image = cv2.imread('assets/test_images/vanessa_vs_blaze.png')
        region=vf_analytics.regions['player1_rounds']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]
        self.assertEqual(0, vf_analytics.count_rounds_won(roi, 1))

        vs_image = cv2.imread('assets/test_images/player2_one_round_won.png')
        region=vf_analytics.regions['player1_rounds']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]
        self.assertEqual(0, vf_analytics.count_rounds_won(roi, 1))
    
    def test_player2_rounds_won(self):
        vs_image = cv2.imread('assets/test_images/vanessa_vs_blaze.png')
        region=vf_analytics.regions['player2_rounds']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]
        self.assertEqual(0, vf_analytics.count_rounds_won(roi, 2))

        vs_image = cv2.imread('assets/test_images/player2_one_round_won.png')
        region=vf_analytics.regions['player2_rounds']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]
        self.assertEqual(1, vf_analytics.count_rounds_won(roi, 2))        

        vs_image = cv2.imread('assets/test_images/player2_two_round_won.png')
        region=vf_analytics.regions['player2_rounds']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]
        self.assertEqual(2, vf_analytics.count_rounds_won(roi, 2))             

    def test_is_excellent(self):
        vs_image = cv2.imread('assets/test_images/player1_three_rounds_won.png')
        region=vf_analytics.regions['excellent']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]
        self.assertTrue(vf_analytics.is_excellent(roi))

        vs_image = cv2.imread('assets/test_images/vanessa_vs_blaze.png')
        region=vf_analytics.regions['ko']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]

        result=vf_analytics.is_excellent(roi)        
        self.assertFalse(result)

        ko_image = cv2.imread('assets/test_images/ko.png')                
        region=vf_analytics.regions['ko']
        (x, y, w, h) = region
        roi = ko_image[y:y+h, x:x+w]

        result=vf_analytics.is_excellent(roi)        
        self.assertFalse(result)


    def test_is_ko(self):
        vs_image = cv2.imread('assets/test_images/vanessa_vs_blaze.png')
        region=vf_analytics.regions['ko']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]

        result=vf_analytics.is_ko(roi)        
        self.assertFalse(result)

        ko_image = cv2.imread('assets/test_images/ko.png')                
        region=vf_analytics.regions['ko']
        (x, y, w, h) = region
        roi = ko_image[y:y+h, x:x+w]

        result=vf_analytics.is_ko(roi)        
        self.assertTrue(result)

    def test_is_ringout(self):
        vs_image = cv2.imread('assets/test_images/vanessa_vs_blaze.png')
        region=vf_analytics.regions['excellent']
        (x, y, w, h) = region
        roi = vs_image[y:y+h, x:x+w]

        result=vf_analytics.is_ringout(roi)        
        self.assertFalse(result)

        ko_image = cv2.imread('assets/test_images/ko.png')                
        region=vf_analytics.regions['excellent']
        (x, y, w, h) = region
        roi = ko_image[y:y+h, x:x+w]

        result=vf_analytics.is_ringout(roi)        
        self.assertFalse(result)

        ko_image = cv2.imread('assets/test_images/ring_out.png')                
        region=vf_analytics.regions['excellent']
        (x, y, w, h) = region
        roi = ko_image[y:y+h, x:x+w]

        result=vf_analytics.is_ringout(roi)        
        self.assertTrue(result)
