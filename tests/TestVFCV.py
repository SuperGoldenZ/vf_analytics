import unittest
import cv2
import vf_analytics
import pytesseract

class TestVFCV(unittest.TestCase):
    def test_player2_rounds_won(self):
        filenames = {
            'assets/test_images/rounds_won/0_2_001.jpg' :2
            ,'assets/test_images/rounds_won/0_0_008.png' :0
            ,'assets/test_images/rounds_won/0_0_009.png' :0
            ,'assets/test_images/rounds_won/0_0_010.png' :0
            ,'assets/test_images/rounds_won/0_0_004.png' :0
            ,'assets/test_images/rounds_won/3_1_001.png' :1
            ,'assets/test_images/rounds_won/0_2_001.png' : 2
            ,'assets/test_images/rounds_won/0_3_001.png':3
            ,'assets/test_images/vanessa_vs_blaze.png' :0
            ,'assets/test_images/player2_one_round_won.png' :1
            ,'assets/test_images/player2_two_round_won.png' :2
        }
        
        for filename in filenames:    
            vs_image = cv2.imread(filename)
            self.assertEqual(filenames[filename], vf_analytics.count_rounds_won(vs_image, 2, True), f"expected ${filename} to be {filenames[filename]} wins")

    def test_player1_rounds_won(self):
        vs_image = cv2.imread('assets/test_images/rounds_won/0_0_008.png')
        self.assertEqual(0, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/rounds_won/0_0_009.png')
        self.assertEqual(0, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/rounds_won/0_0_010.png')
        self.assertEqual(0, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/player1_two_rounds_won.png')
        self.assertEqual(2, vf_analytics.count_rounds_won(vs_image, 1))

        vs_image = cv2.imread('assets/test_images/rounds_won/0_0_007.png')
        self.assertEqual(0, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/rounds_won/0_0_006.png')
        self.assertEqual(0, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/rounds_won/0_0_005.png')
        self.assertEqual(0, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/rounds_won/0_0_004.png')
        self.assertEqual(0, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/rounds_won/0_0_001.png')
        self.assertEqual(0, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/rounds_won/0_0_002.png')
        self.assertEqual(0, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/rounds_won/0_0_003.png')
        self.assertEqual(0, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/rounds_won/1_0_002.png')
        self.assertEqual(1, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/rounds_won/3_1_001.png')
        self.assertEqual(3, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/rounds_won/1_0_001.png')
        self.assertEqual(1, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/rounds_won/2_0_001.png')
        self.assertEqual(2, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/rounds_won/0_2_001.png')
        self.assertEqual(0, vf_analytics.count_rounds_won(vs_image, 1, True))

        vs_image = cv2.imread('assets/test_images/vanessa_vs_blaze.png')
        self.assertEqual(0, vf_analytics.count_rounds_won(vs_image, 1))

        vs_image = cv2.imread('assets/test_images/player2_one_round_won.png')
        self.assertEqual(0, vf_analytics.count_rounds_won(vs_image, 1))

    def test_get_character(self):
        vs_image = cv2.imread('assets/test_images/characters/blaze_vs_taka.png')
        self.assertEqual("Blaze", vf_analytics.get_character_name(1, vs_image))
        self.assertEqual("Taka", vf_analytics.get_character_name(2, vs_image))

        vs_image = cv2.imread('assets/test_images/characters/jacky_vs_blaze.png')
        self.assertEqual("Jacky", vf_analytics.get_character_name(1, vs_image))
        self.assertEqual("Blaze", vf_analytics.get_character_name(2, vs_image))

        vs_image = cv2.imread('assets/test_images/characters/blaze_vs_sarah.png')
        self.assertEqual("Blaze", vf_analytics.get_character_name(1, vs_image))
        self.assertEqual("Sarah", vf_analytics.get_character_name(2, vs_image))

        vs_image = cv2.imread('assets/test_images/characters/blaze_vs_akira.png')
        self.assertEqual("Blaze", vf_analytics.get_character_name(1, vs_image))
        self.assertEqual("Akira", vf_analytics.get_character_name(2, vs_image))

        vs_image = cv2.imread('assets/test_images/characters/blaze_vs_wolf.png')
        self.assertEqual("Blaze", vf_analytics.get_character_name(1, vs_image))
        self.assertEqual("Wolf", vf_analytics.get_character_name(2, vs_image))

    def test_is_not_vs(self):
        filenames = [
            'assets/test_images/vs/not_vs_005.jpg'
            ,'assets/test_images/vs/not_vs_001.jpg'
            ,'assets/test_images/vs/not_vs_002.jpg'
            ,'assets/test_images/vs/not_vs_003.jpg'
            ,'assets/test_images/vs/not_vs_004.jpg'            
            ,'assets/test_images/ko.png'
        ]        
        for filename in filenames:
            vs_image = cv2.imread(filename)
            #print(f"not {filename}")
            self.assertFalse(vf_analytics.is_vs(vs_image),
                             f"{filename} is accidentally vs")

    def test_is_vs(self):
        #print("vanessa vs blaze")
        vs_image = cv2.imread('assets/test_images/vanessa_vs_blaze.png')        
        self.assertTrue(vf_analytics.is_vs(vs_image))

        vs_image = cv2.imread('assets/test_images/vs_vanessa_two.png')        
        self.assertTrue(vf_analytics.is_vs(vs_image))

        vs_image = cv2.imread('assets/test_images/vs_pai.png')        
        self.assertTrue(vf_analytics.is_vs(vs_image))

    
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

    def test_get_player_rank(self):
        vs_image = cv2.imread('assets/test_images/rank/34_37.png')
        rank=vf_analytics.get_player_rank(1, vs_image, True)
        self.assertEqual(34, rank)

        rank=vf_analytics.get_player_rank(2, vs_image, True)
        self.assertEqual(37, rank)

        vs_image = cv2.imread('assets/test_images/rank/40_41_02.png')
        rank=vf_analytics.get_player_rank(2, vs_image, True)
        self.assertEqual(41, rank)

        rank=vf_analytics.get_player_rank(1, vs_image, True)
        self.assertEqual(40, rank)

        vs_image = cv2.imread('assets/test_images/rank/40_41_01.png')
        rank=vf_analytics.get_player_rank(1, vs_image, True)
        self.assertEqual(40, rank)

        rank=vf_analytics.get_player_rank(2, vs_image, True)
        self.assertEqual(41, rank)


        vs_image = cv2.imread('assets/test_images/rank/42_44_01.png')
        rank=vf_analytics.get_player_rank(1, vs_image, True)
        self.assertEqual(42, rank)

        rank=vf_analytics.get_player_rank(2, vs_image, True)
        self.assertEqual(44, rank)

        vs_image = cv2.imread('assets/test_images/rank/36_34.png')
        rank=vf_analytics.get_player_rank(1, vs_image, True)
        self.assertEqual(36, rank)

        rank=vf_analytics.get_player_rank(2, vs_image, True)
        self.assertEqual(34, rank)

        vs_image = cv2.imread('assets/test_images/rank/26_33_01.png')
        rank=vf_analytics.get_player_rank(1, vs_image, True)
        self.assertEqual(26, rank)

        rank=vf_analytics.get_player_rank(2, vs_image, True)
        self.assertEqual(33, rank)

        vs_image = cv2.imread('assets/test_images/rank/26_33.png')
        rank=vf_analytics.get_player_rank(1, vs_image, True)
        self.assertEqual(26, rank)

        rank=vf_analytics.get_player_rank(2, vs_image, True)
        self.assertEqual(33, rank)

        vs_image = cv2.imread('assets/test_images/rank/32_29.png')
        rank=vf_analytics.get_player_rank(1, vs_image, True)
        self.assertEqual(32, rank)

        rank=vf_analytics.get_player_rank(2, vs_image, True)
        self.assertEqual(29, rank)

        vs_image = cv2.imread('assets/test_images/rank/42_44.png')
        rank=vf_analytics.get_player_rank(1, vs_image, True)
        self.assertEqual(42, rank)

        rank=vf_analytics.get_player_rank(2, vs_image, True)
        self.assertEqual(44, rank)

        vs_image = cv2.imread('assets/test_images/rank/43_43.png')
        rank=vf_analytics.get_player_rank(1, vs_image, True)
        self.assertEqual(43, rank)

        rank=vf_analytics.get_player_rank(2, vs_image, True)
        self.assertEqual(43, rank)

        vs_image = cv2.imread('assets/test_images/rank/32_30.png')
        rank=vf_analytics.get_player_rank(1, vs_image, True)
        self.assertEqual(32, rank)

        rank=vf_analytics.get_player_rank(2, vs_image, True)
        self.assertEqual(30, rank)

        vs_image = cv2.imread('assets/test_images/rank/42_39.png')
        rank=vf_analytics.get_player_rank(1, vs_image, True)
        self.assertEqual(42, rank)

        rank=vf_analytics.get_player_rank(2, vs_image, True)
        self.assertEqual(39, rank)

        vs_image = cv2.imread('assets/test_images/player1_two_rounds_won.png')
        rank=vf_analytics.get_player_rank(1, vs_image)
        self.assertEqual(37, rank)

        rank=vf_analytics.get_player_rank(2, vs_image)
        self.assertEqual(36, rank)        

        vs_image = cv2.imread('assets/test_images/vftv_blaze_vs_blaze.png')
        rank=vf_analytics.get_player_rank(1, vs_image, True)
        self.assertEqual(27, rank)

        rank=vf_analytics.get_player_rank(2, vs_image, True)
        self.assertEqual(25, rank)

    def test_get_player_ringname(self):
        vs_image = cv2.imread('assets/test_images/ringnames/ringnames-002.png')
        ringname=vf_analytics.get_ringname(1, vs_image)
        self.assertEqual("ONSUakr", ringname)

        ringname=vf_analytics.get_ringname(2, vs_image)
        self.assertEqual("kiri", ringname)

        vs_image = cv2.imread('assets/test_images/vs_akira.png')
        ringname=vf_analytics.get_ringname(1, vs_image)
        self.assertEqual("Namflow_Gx2", ringname)
        
        ringname=vf_analytics.get_ringname(2, vs_image)
        self.assertEqual("Dynamite-Sikoku4", ringname)

        vs_image = cv2.imread('assets/test_images/vs_pai.png')
        ringname=vf_analytics.get_ringname(1, vs_image)
        self.assertEqual("migu_garden", ringname)

        vs_image = cv2.imread('assets/test_images/vs_pai.png')
        ringname=vf_analytics.get_ringname(2, vs_image)
        self.assertEqual("Namflow_Gx2", ringname)

        vs_image = cv2.imread('assets/test_images/ringnames/ringnames-001.png')
        ringname=vf_analytics.get_ringname(1, vs_image)
        self.assertEqual("mepadeth-INeking", ringname)

        ringname=vf_analytics.get_ringname(2, vs_image)
        self.assertEqual("tan-jet6", ringname)

    def test_get_stage(self):
        vs_image = cv2.imread('assets/test_images/stage/training_room.jpg')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Training Room", ringname)

        vs_image = cv2.imread('assets/test_images/stage/shrine.jpg')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Shrine", ringname)

        vs_image = cv2.imread('assets/test_images/stage/genesis.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Genesis", ringname)

        vs_image = cv2.imread('assets/test_images/stage/broken_house.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Broken House", ringname)

        vs_image = cv2.imread('assets/test_images/stage/snow.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Snow Mountain", ringname)

        vs_image = cv2.imread('assets/test_images/stage/terrace01.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertIsNone(ringname)

        vs_image = cv2.imread('assets/test_images/stage/terrace02.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Terrace", ringname)

        vs_image = cv2.imread('assets/test_images/vs_pai.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Statues", ringname)

        vs_image = cv2.imread('assets/test_images/vs_akira.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Great Wall", ringname)
                
        vs_image = cv2.imread('assets/test_images/vs_wolf.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Sumo Ring", ringname)

        vs_image = cv2.imread('assets/test_images/vs_vanessa_two.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Waterfalls", ringname)

        vs_image = cv2.imread('assets/test_images/vanessa_vs_blaze.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Island", ringname)

        vs_image = cv2.imread('assets/test_images/vs_jacky.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Arena", ringname)

        vs_image = cv2.imread('assets/test_images/stage/palace.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Palace", ringname)

        vs_image = cv2.imread('assets/test_images/stage/temple.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Temple", ringname)

        vs_image = cv2.imread('assets/test_images/stage/aurora.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Aurora", ringname)

        vs_image = cv2.imread('assets/test_images/stage/ruins.png')
        ringname=vf_analytics.get_stage(vs_image)
        self.assertEqual("Ruins", ringname)
