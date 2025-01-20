"""This module provides classes that contain VF match data"""

import csv
import io
import hashlib
from datetime import timedelta
from datetime import datetime

import vf_data.round
import vf_cv.player_rank


class Match:
    """wrapping up VF match data"""

    def __init__(self):
        self.video_id = None
        self.id = None
        self.stage = None

        self.player1character = None
        self.player1ringname = None
        self.player1rank = None

        self.player2character = None
        self.player2ringname = None
        self.player2rank = None
        self.vs_frame = 0
        self.vs_frame_seconds = 0
        self.rounds = []
        self.date = None
        self.video_url = None
        self.video_frame_rate = None

    def got_all_vs_info(self):
        """Returns true if the match has all data that we are expecting to process"""

        if self.stage is None:
            return False
        if self.player1character is None:
            return False
        if self.player2character is None:
            return False
        # if self.player1ringname is None:
        # return False
        # if self.player2ringname is None:
        # return False

        return True

    def count_rounds_won(self, player_num: int):
        result = 0

        for current_round in self.rounds:
            if current_round.winning_player_num == player_num:
                result += 1

        return result

    def get_round_num(self):
        return len(self.rounds) + 1

    def add_finished_round(self, new_round: vf_data.round.Round):
        new_round.num = self.get_round_num()
        self.rounds.append(new_round)

    def vs_frame_to_string(self, writer: csv.writer):
        self.id = self.make_id()

        writer.writerow(
            [
                self.video_id,
                self.id,
                self.date,
                self.stage,
                self.player1ringname,
                self.player1rank,
                self.player1character,
                self.player2ringname,
                self.player2rank,
                self.player2character,
                0,
                0,
                "NA",
                0,
                None,
                None,
                f"https://www.youtube.com/watch?v={self.video_id}&t={self.vs_frame_seconds}",
            ]
        )

    def make_id(self):
        fields = [
            self.date,
            self.player1character,
            self.player1ringname,
            self.player2character,
            self.player2ringname,
            self.player1rank,
            self.player2rank,
        ]

        if len(self.rounds) >= 3:
            fields = [
                self.date,
                self.player1character,
                self.player1ringname,
                self.player2character,
                self.player2ringname,
                self.player1rank,
                self.player2rank,
                self.rounds[0].victory,
                self.rounds[0].remaining_time,
                self.rounds[0].winning_player_num,
                self.rounds[1].victory,
                self.rounds[1].remaining_time,
                self.rounds[1].winning_player_num,
                self.rounds[2].victory,
                self.rounds[2].remaining_time,
                self.rounds[2].winning_player_num,
            ]

        m = hashlib.md5()
        for s in fields:
            if type(s) == str:
                m.update(s.encode())
            elif type(s) == int:
                m.update(s.to_bytes(10, "big"))
            elif s is not None:
                print(type(s))
                m.update(s)

        return m.hexdigest()

    def __str__(self):
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONE, escapechar="\\")
        self.vs_frame_to_string(writer)
        self.id = self.make_id()

        for current_round in self.rounds:

            writer.writerow(
                [
                    self.video_id,
                    self.id,
                    self.date,
                    self.stage,
                    self.player1ringname,
                    self.player1rank,
                    self.player1character,
                    self.player2ringname,
                    self.player2rank,
                    self.player2character,
                    current_round.num,
                    current_round.winning_player_num,
                    current_round.get_victory(),
                    current_round.remaining_time,
                    current_round.player1_drink_points_at_start,
                    current_round.player2_drink_points_at_start,
                    current_round.first_strike_player_num,
                    round(current_round.max_damage[1]),
                    round(current_round.max_damage[2] * 100),
                    current_round.get_youtube_url(self.video_id),
                ]
            )

        return output.getvalue()

    def to_youtube_title(self):
        player1rank_english = None
        player2rank_english = None

        try:
            player1rank_english = vf_cv.player_rank.PlayerRank.ENGLISH_NAMES[
                self.player1rank
            ]
            player2rank_english = vf_cv.player_rank.PlayerRank.ENGLISH_NAMES[
                self.player2rank
            ]
        except Exception as e:
            player1rank_english = "na"
            player2rank_english = "na"

        return f'【VF5 R.E.V.O. Ranked】{player1rank_english} (Lv. {self.player1rank}) {self.player1character} \\"{self.player1ringname}\\" VS {player2rank_english} (Lv. {self.player2rank}) {self.player2character} \\"{self.player2ringname}\\" - {self.stage}'

    def to_file_title(self):
        player1rank_english = None
        player2rank_english = None

        try:
            player1rank_english = vf_cv.player_rank.PlayerRank.ENGLISH_NAMES[
                self.player1rank
            ]
            player2rank_english = vf_cv.player_rank.PlayerRank.ENGLISH_NAMES[
                self.player2rank
            ]
        except Exception as e:
            player1rank_english = "na"
            player2rank_english = "na"

        time_str = datetime.now().strftime("%Y%m%d%H:%M:%S")
        return f'【VF5 R.E.V.O. Ranked】{player1rank_english} (Lv. {self.player1rank}) {self.player1character} "{self.player1ringname}" VS {player2rank_english} (Lv. {self.player2rank}) {self.player2character} "{self.player2ringname}" - {self.stage} {time_str}'

    def to_ffmpeg_copy_command(self):
        if self.video_url is None or "youtube" in self.video_url:
            return ""

        if self.rounds is None or len(self.rounds) == 0:
            return ""

        first_round: vf_data.Round = self.rounds[0]
        match_start_seconds = (
            int(first_round.seconds) - (45 - float(first_round.remaining_time)) - 17
        )

        last_round: vf_data.Round = self.rounds[len(self.rounds) - 1]

        start_timestamp = str(timedelta(seconds=match_start_seconds))
        clip_duration = int((int(last_round.seconds) - match_start_seconds) + 15)

        dest_dir = "/mnt/sdb/Users/alexa/Videos/2024Q4 Open Beta/Matches/"
        return f'ffmpeg -y -ss "{start_timestamp}" -i "{self.video_url}" -c copy -t {clip_duration} "{dest_dir}{self.to_youtube_title()}.mp4"'

    def get_video_filename(self):
        dest_dir = "/mnt/sdb/Users/alexa/Videos/vfes/"
        return f"{dest_dir}{self.to_file_title()}.mkv"
