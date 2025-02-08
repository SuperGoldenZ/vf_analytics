"""Contains information about a VF round"""

from vf_data.frame import Frame
from vf_data.frame_player_info import FramePlayerInfo


class Round:
    KO = 1
    RO = 2
    EX = 3
    TO = 4

    VICTORIES = {KO: "KO", RO: "RO", EX: "EX", TO: "TO"}

    def __init__(self):
        self.winning_player_num = 0
        self.remaining_time = 0
        self.victory = 0
        self.num = 0
        self.seconds = 0
        self.player1_drink_points_at_start = None
        self.player2_drink_points_at_start = None
        self.first_strike_player_num = None

        # todo make this only two
        self.current_combo_damage = [0, 0, 0]
        self.combo_hits = [0, 0, 0]
        self.max_damage = [0, 0, 0]

        self.frames = []

        self.start_frame_num = 0

    def get_victory(self):
        return self.VICTORIES[self.victory]

    def get_youtube_url(self, video_id):
        return f"https://www.youtube.com/watch?v={video_id}&t={self.seconds}"

    def add_frame(
        self, frame_id, p1health, p2health, time_remaining_seconds, p1drinks, p2drinks
    ):
        p1info = FramePlayerInfo()
        p1info.health = p1health
        p1info.drinks = p1drinks

        p2info = FramePlayerInfo()
        p2info.health = p2health
        p2info.drinks = p2drinks

        frame = Frame(frame_id=frame_id)
        frame.p1info = p1info
        frame.p2info = p2info
        frame.time_seconds_remaining = time_remaining_seconds

        self.frames.append(frame)
