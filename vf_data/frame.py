"""Contains information about a VF round"""

from vf_data.frame_player_info import FramePlayerInfo

class Frame():

    def __init__(self, frame_id):
        self.p1info = FramePlayerInfo()
        self.p2info = FramePlayerInfo()
        self.time_seconds_remaining = 0
        self.id = frame_id
        self.win_prob_player1 = None
        self.win_prob_player2 = None
        self.elapsed_time = 0