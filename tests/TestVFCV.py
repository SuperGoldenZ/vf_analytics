import unittest
import cv2
import vf_analytics
import time

class TestVFCV(unittest.TestCase):
    def test_is_vs(self):
        params = [
             ['assets/test_images/480p/vs/vs_04.jpg', vf_analytics.regions_480p]                        
            ,['assets/test_images/480p/vs/vs_03.jpg', vf_analytics.regions_480p]            
            ,['assets/test_images/480p/vs/vs_02.jpg', vf_analytics.regions_480p]
            ,['assets/test_images/1080p/vs/vs_01.jpg', vf_analytics.regions_1080p]
            ,['assets/test_images/360p/vs/vs_01.jpg', vf_analytics.regions_360p]
            ,['assets/test_images/480p/vs/vs_01.jpg', vf_analytics.regions_480p]                        
            #,['assets/test_images/vanessa_vs_blaze.png', None]
            #,['assets/test_images/vs_vanessa_two.png', None]
            #,['assets/test_images/vs_pai.png', None]            
        ]

        for param in params:
            vs_image = cv2.imread(param[0])
            self.assertIsNotNone(vs_image)
            result = vf_analytics.is_vs(vs_image, 0, param[1])
            self.assertTrue(result, f"Failed for {param[0]} was not VS as expected")

    def test_get_player_rank(self):
        params = [
            ['assets/test_images/480p/rank/31_30_001.jpg', 31, 30, vf_analytics.regions_480p]
            ,['assets/test_images/360p/rank/27_24_001.jpg', 27, 24, vf_analytics.regions_360p]
            #,['assets/test_images/360p/rank/30_30_001.jpg', 30, 0, vf_analytics.regions_360p]
            #,['assets/test_images/360p/rank/31_30_001.jpg', 31, 30, vf_analytics.regions_360p]
            ,['assets/test_images/1080p/rank/27_24_001.jpg', 27, 24, vf_analytics.regions_1080p]
            ,['assets/test_images/480p/rank/27_24_001.jpg', 27, 24, vf_analytics.regions_480p]
            ,['assets/test_images/480p/rank/30_30_001.jpg', 30, 30, vf_analytics.regions_480p]            
        ]

        for param in params:
            vs_image = cv2.imread(param[0])
            rank=vf_analytics.get_player_rank(1, vs_image, override_regions=param[3])
            self.assertEqual(param[1], rank, f"Failed for {param[0]} expected {param[1]} but got {rank}")

            rank=vf_analytics.get_player_rank(2, vs_image, override_regions= param[3])
            self.assertEqual(param[2], rank, f"Failed for {param[0]} expected {param[1]} but got {rank}")
    
    def test_not_rounds_won(self):
        filenames = ['assets/test_images/480p/rounds_won/0_0_01.png'
                     ,'assets/test_images/480p/rounds_won/0_1_01.png'
                     ]

        vf_analytics.resolution = "480p"

        for file in filenames:
            vs_image = cv2.imread(file)
            with self.assertRaises(Exception) as e:
                self.assertEqual("Not sure how won", e.msg)
                vf_analytics.count_rounds_won(vs_image, 1)

        
            
    def test_rounds_won(self):
        param_sets = [
            ['assets/test_images/480p/ringout/ringout_01.jpg', 0, 3, vf_analytics.regions_480p]
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
            result = vf_analytics.count_rounds_won(vs_image, 1, params[3])
            self.assertEqual(params[1], result, f"expected {filename} to be {params[1]} wins for player 1")

            result = vf_analytics.count_rounds_won(vs_image, 2, params[3])
            self.assertEqual(params[2], result, f"expected {filename} to be {params[2]} wins for player 2")

    def test_get_character(self):
        param_sets=[
            ['assets/test_images/480p/characters/blaze_vs_pai.jpg', "Blaze", "Pai", vf_analytics.regions_480p]
            ,['assets/test_images/480p/characters/wolf_vs_pai.jpg', "Wolf", "Pai", vf_analytics.regions_480p]
        ]

        for params in param_sets:
            vs_image = cv2.imread(params[0])
            result = vf_analytics.get_character_name(1, vs_image, retry=0, override_region=params[3])
            self.assertEqual(params[1], result)

            result = vf_analytics.get_character_name(2, vs_image, retry=0, override_region=params[3])
            self.assertEqual(params[2], result)
    
    def test_is_ko(self):
        images = [
             "assets/test_images/480p/knockout/knockout_01.jpg"
            ,"assets/test_images/480p/knockout/knockout_02.jpg"
            ,"assets/test_images/480p/knockout/knockout_03.png"
            ,"assets/test_images/480p/knockout/knockout_04.png"
            ,"assets/test_images/480p/knockout/knockout_05.png"
        ]
        vf_analytics.resolution="480p"

        for image in images:
            vs_image = cv2.imread(image)
            #print(f"is_ko: {image}")
            self.assertTrue(vf_analytics.is_ko(vs_image), f"{image} is not KO as expected")

    def test_is_not_excellent(self):        
        images = [
             "assets/test_images/480p/knockout/knockout_01.jpg"
            ,"assets/test_images/480p/knockout/knockout_02.jpg"
            ,"assets/test_images/480p/knockout/knockout_03.png"
            ,"assets/test_images/480p/knockout/knockout_04.png"
            ,"assets/test_images/480p/knockout/knockout_05.png"
            ,"assets/test_images/480p/ringout/ringout_01.jpg"
            ,"assets/test_images/480p/excellent/not_excellent_01.png"
            ,"assets/test_images/480p/excellent/not_excellent_02.png"
            ,"assets/test_images/480p/excellent/not_excellent_03.png"
        ]
        vf_analytics.resolution="480p"

        for image in images:
            vs_image = cv2.imread(image)
            #print(f"testing is not excellent {image}")
            self.assertFalse(vf_analytics.is_excellent(vs_image), f"{image} is unexpectedly excellent")

    def test_is_not_ringout(self):        
        images = [
             "assets/test_images/480p/knockout/knockout_01.jpg"
            ,"assets/test_images/480p/knockout/knockout_02.jpg"
            ,"assets/test_images/480p/knockout/knockout_03.png"
            ,"assets/test_images/480p/knockout/knockout_04.png"
            ,"assets/test_images/480p/knockout/knockout_05.png"
            ,"assets/test_images/480p/excellent/excellent_01.jpg"
            ,"assets/test_images/480p/excellent/excellent_02.png"
            ,"assets/test_images/480p/ringout/not_ringout_01.png"
            ,"assets/test_images/480p/ringout/not_ringout_02.png"
            ,"assets/test_images/480p/ringout/not_ringout_03.png"
        ]
        vf_analytics.resolution="480p"

        for image in images:
            vs_image = cv2.imread(image)
            #print(f"\ntesting is not ringout {image}")
            self.assertFalse(vf_analytics.is_ringout(vs_image), f"{image} is unexpectedly ringout")

    def test_is_excellent(self):        
        images = [
             "assets/test_images/480p/excellent/excellent_01.jpg"            
             ,"assets/test_images/480p/excellent/excellent_02.png"            
        ]
        vf_analytics.resolution="480p"

        for image in images:
            vs_image = cv2.imread(image)
            #print(f"testing is excellent {image}")
            self.assertTrue(vf_analytics.is_excellent(vs_image), f"{image} is not excellent as expected")

    def test_is_ringout(self):
        return
        images = [
             "assets/test_images/480p/ringout/ringout_01.jpg"            
        ]
        vf_analytics.resolution="480p"

        for image in images:
            vs_image = cv2.imread(image)
            self.assertTrue(vf_analytics.is_ringout(vs_image), f"{image} is not ring out as expected")

    def test_is_not_ko(self):        
        images = [
            "assets/test_images/480p/excellent/excellent_01.jpg"
            ,"assets/test_images/480p/ringout/ringout_01.jpg"
        ]
        vf_analytics.resolution="480p"

        for image in images:
            vs_image = cv2.imread(image)
            self.assertFalse(vf_analytics.is_ko(vs_image), f"{image} is unexpectedly KO")


#    def test_get_player_ringname(self):
#        vs_image = cv2.imread('assets/test_images/ringnames/ringnames-002.png')
#        ringname=vf_analytics.get_ringname(1, vs_image)
#        self.assertEqual("ONSUakr", ringname)
#
#        ringname=vf_analytics.get_ringname(2, vs_image)
#        self.assertEqual("kiri", ringname)
#
#        vs_image = cv2.imread('assets/test_images/vs_akira.png')
#        ringname=vf_analytics.get_ringname(1, vs_image)
#        self.assertEqual("Namflow_Gx2", ringname)
#        
#        ringname=vf_analytics.get_ringname(2, vs_image)
#        self.assertEqual("Dynamite-Sikoku4", ringname)
#
#        vs_image = cv2.imread('assets/test_images/vs_pai.png')
#        ringname=vf_analytics.get_ringname(1, vs_image)
#        self.assertEqual("migu_garden", ringname)
#
#        vs_image = cv2.imread('assets/test_images/vs_pai.png')
#        ringname=vf_analytics.get_ringname(2, vs_image)
#        self.assertEqual("Namflow_Gx2", ringname)
#
#        vs_image = cv2.imread('assets/test_images/ringnames/ringnames-001.png')
#        ringname=vf_analytics.get_ringname(1, vs_image)
#        self.assertEqual("mepadeth-INeking", ringname)
#
#        ringname=vf_analytics.get_ringname(2, vs_image)
#        self.assertEqual("tan-jet6", ringname)

    def test_get_stage(self):
        params = [
             #['assets/test_images/1080p/stage/snow_mountain.jpg', "Snow Mountain", vf_analytics.regions_1080p]
             ['assets/test_images/480p/stage/island.jpg', "Island", vf_analytics.regions_480p]
            ,['assets/test_images/480p/stage/training_room.png', "Training Room", vf_analytics.regions_480p]
            ,['assets/test_images/360p/stage/snow_mountain.jpg', "Snow Mountain", vf_analytics.regions_360p]
            # ,['assets/test_images/stage/training_room.jpg', "Training Room", None]
#            ,['assets/test_images/stage/training_room.jpg', "Training Room", None]
#            ,['assets/test_images/stage/shrine.jpg', "Shrine", None]
#            ,['assets/test_images/stage/shrine.jpg', "Shrine", None]
#            ,['assets/test_images/stage/genesis.png', "Genesis", None]
#            ,['assets/test_images/stage/genesis.png', "Genesis", None]
#            ,['assets/test_images/stage/broken_house.png', "Broken House", None]
#            ,['assets/test_images/stage/broken_house.png', "Broken House", None]
#            ,['assets/test_images/stage/snow.png', "Snow Mountain", None]
#            ,['assets/test_images/stage/snow.png', "Snow Mountain", None]
#            ,['assets/test_images/stage/terrace02.png', "Terrace", None]
#            ,['assets/test_images/stage/terrace02.png', "Terrace", None]
#            ,['assets/test_images/vs_pai.png', 'Statues', None]
#            ,['assets/test_images/vs_pai.png', 'Statues', None]
#            ,['assets/test_images/vs_akira.png', "Great Wall", None]

        ]
        
        for param in params:
            vs_image = cv2.imread(param[0])
            stage=vf_analytics.get_stage(vs_image, param[2])
            self.assertEqual(param[1], stage, f"Failed for {param[0]}")

        #vs_image = cv2.imread('assets/test_images/stage/terrace01.png')
        #ringname=vf_analytics.get_stage(vs_image)
        #self.assertIsNone(ringname)