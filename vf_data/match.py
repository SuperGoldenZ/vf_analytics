import vf_data.round
import csv
import io

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

    def got_all_vs_info(self):
        """Returns true if the match has all data that we are expecting to process"""

        if self.stage is None:
            return False
        if self.player1character is None:
            return False
        if self.player2character is None:
            return False
        #if self.player1ringname is None:
            #return False
        #if self.player2ringname is None:
            #return False

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

    def vs_frame_to_string(self, writer: csv.DictWriter):
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
                f"https://www.youtube.com/watch?v={self.video_id}&t={self.vs_frame_seconds}"
            ]
        )

    def __str__(self):
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONE)
        self.vs_frame_to_string(writer)
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
                    current_round.get_youtube_url(self.video_id)
                ]
            )

        return output.getvalue()
