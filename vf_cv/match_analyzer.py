"""This module provide functions to extract information from a VFES/US game frame"""

import traceback
import os
import time
import cv2

from line_profiler import profile

import vf_data.match
import vf_analytics
import vf_cv.winning_frame
import vf_cv.winning_round
import vf_cv.character
import vf_cv.vs_screen
import vf_cv.revo
import vf_cv.video_capture_async


class MatchAnalyzer:
    """This is the class that analyzes a video of a match, extracts and stores data into other classes"""

    DONT_SAVE = False
    SAVE_PIC_ALL = False

    def __init__(
        self,
        cap: vf_cv.video_capture_async.VideoCaptureAsync,
        logger,
        jpg_folder,
        interval,
        frame_rate,
        youtube_video_title,
        process_vs_only,
        dont_save=False,
    ):
        self.match = vf_data.Match()
        self.match.video_url = cap.src
        self.match.video_frame_rate = cap.get_frame_rate()

        self.cap = cap
        self.logger = logger

        self.character = vf_cv.Character()
        self.time_cv = vf_cv.Timer()
        self.winning_round = vf_cv.WinningRound()
        self.winning_frame = vf_cv.WinningFrame()
        self.player_rank = vf_cv.PlayerRank()
        self.character = vf_cv.Character()
        self.vs_screen = vf_cv.VsScreen()
        self.drinks = vf_cv.Drinks()
        self.frame = None
        self.frame_bw = None
        self.frame_height = 0
        self.frame_rate = 0
        self.count = 0
        self.state = None
        self.jpg_folder = jpg_folder
        self.matches_processed = 0
        self.original_frame = None
        self.interval = interval
        self.frame_rate = frame_rate
        self.skip_frames = 0
        self.old_time = None
        self.old_time_seconds = None
        self.time_seconds = None
        self.time_matches = 0
        self.timestr = None
        self.current_round = None
        self.endround = False
        self.youtube_video_title = youtube_video_title
        self.process_vs_only = process_vs_only
        self.DONT_SAVE = dont_save

    @profile
    def analyze_next_match(
        self,
        video_id="n/a",
        cam=-1,
        frame_count=None,
        start_frame=0,
    ):

        self.match = vf_data.Match()

        self.match.video_url = self.cap.src
        self.match.video_frame_rate = self.cap.get_frame_rate()

        self.endround = False
        self.time_seconds = None
        self.time_matches = 0
        self.timestr = None

        end_frame = frame_count

        self.count = start_frame + 1

        self.state = "before"
        self.current_round = vf_data.Round()
        self.match.video_id = video_id

        self.skip_frames = 0

        if cam != -1:
            jpg_folder = "assets/jpg/cam"
            if not os.path.exists(jpg_folder):
                os.makedirs(jpg_folder)

        actual_count = self.count - 1

        result = self.get_next_frame(cam, video_id, actual_count)

        while (
            self.cap.frames_read < end_frame or cam != -1
        ) and self.frame is not None:
            actual_count = result

            debug_beta = False
            if self.state != "before" and vf_cv.revo.REVO.is_beta_screen(
                self.frame, debug_beta
            ):
                raise PrematureMatchFinishException("Found Revo BETA Frame")

            result = self.analyze_next_frame()
            if result is not None:
                return result

            result = self.get_next_frame(cam, video_id, actual_count)

        if self.state != "before":
            raise PrematureMatchFinishException()

        print(f"returning 0 because {self.cap.frames_read} >= {end_frame}")
        return 0

    @profile
    def get_next_frame(self, cam, video_id, actual_count):
        count_int = int(self.count)

        # use epoch time for cam
        if cam != -1:
            count_int = int(time.time() * 1000)
            self.count = count_int

        self.frame = None
        if self.skip_frames > 0 and cam != -1:
            self.skip_frames -= 1
            if cam != -1:
                self.cap.read()
                self.process_fight_shun_drinks()
                time.sleep(self.interval)
            return

        if self.skip_frames > 0 and cam == -1:
            self.count += int((self.frame_rate * self.interval) * self.skip_frames)
            count_int = int(self.count)
            self.skip_frames = 0

        self.original_frame = None

        self.frame = None

        if cam != -1:
            actual_count = self.count - 1

        while actual_count < count_int:
            try:
                self.frame = self.cap.read()
                self.process_fight_shun_drinks(actual_count)
            except:
                time.sleep(5)

                self.frame = self.cap.read()
                self.process_fight_shun_drinks(actual_count)

            if self.frame is None:
                break
            actual_count = actual_count + 1

        if self.frame is None:
            self.logger.warning(f"Skipping frame {self.count:13d} because no return")
            self.count += 1
            print("self.frame none continue")
            return None

        return actual_count

    def analyze_next_frame(self):
        self.original_frame = self.frame
        self.frame_height = self.frame.shape[0]  # Get the dimensions of the frame

        if self.state == "before":
            self.process_before_vs()
            return
        if self.state == "vs":
            if self.process_vs():
                return 0
            return
        if self.state == "fight" and self.process_fight():
            return self.count

    def save_cam_frame(self, suffix, force_save=False):
        if self.DONT_SAVE and not force_save:
            return

        if not os.path.exists(self.jpg_folder):
            os.makedirs(self.jpg_folder)

        if not os.path.exists(self.jpg_folder + f"/{self.matches_processed}"):
            os.makedirs(self.jpg_folder + f"/{self.matches_processed}")

        original_out_filename = (
            self.jpg_folder
            + f"/{self.matches_processed}/"
            + str(f"{self.cap.frames_read}_{suffix}")
            + ".png"
        )

        if not os.path.isfile(original_out_filename):
            cv2.imwrite(original_out_filename, self.frame)

    @profile
    def process_before_vs(self):
        self.logger.debug(f"BEFORE - searching for vs frame count {self.count}")
        stage = None

        self.vs_screen.set_frame(self.frame)
        if self.vs_screen.is_vs_ver1():
            print("Found VS screen")
            stage = self.vs_screen.get_stage()
            print(f"Got stage {stage}")
            if stage is None:
                self.save_cam_frame("invalid_is_vs")

        if self.SAVE_PIC_ALL:
            self.save_cam_frame("invalid_is_vs")

        if stage is not None:
            formatted_match_id = "%02d" % (self.matches_processed + 1,)
            self.match.id = f"{self.match.video_id}-{formatted_match_id}"
            self.match.stage = stage
            self.match.vs_frame_seconds = int(self.cap.frames_read / self.frame_rate)
            print("setting state to vs")
            self.state = "vs"
            self.logger.debug(
                f"{self.match.video_id} {self.count:13d} - got stage {stage} and setting to vs {self.match.player1character} vs {self.match.player2character}"
            )
        else:
            self.count += int(self.frame_rate * self.interval * 40)
            del self.frame
            del self.original_frame

        self.count += 1

    def skip_beginning_of_round(self):
        return (
            self.time_seconds == "43"
            or self.time_seconds == "44"
            or self.time_seconds == "45"
        )

    @profile
    def process_vs(self):
        # print(f"{self.count} processing vs {self.match.player1character} vs {self.match.player2character} on {self.match.stage}")
        print("processing vs")
        if self.match.player1character is None:
            self.character.set_frame(self.frame)
            self.character.set_youtube_video_title(self.youtube_video_title)

            player1character = self.character.get_character_name(1)
            if player1character is not None:
                self.match.player1character = player1character
                self.logger.debug(
                    f"{self.match.video_id} {self.count:13d} - player 1 character {player1character}"
                )
                self.save_cam_frame(
                    f"player1_character-{player1character}",
                )

        if self.match.player2character is None:
            self.character.set_frame(self.frame)
            player2character = self.character.get_character_name(2)
            if player2character is not None:
                self.match.player2character = player2character
                self.logger.debug(
                    f"{self.match.video_id} {self.count:13d} - player 2 character {player2character}"
                )
                self.save_cam_frame(
                    f"player2_character-{player2character}",
                )

        if self.match.stage is None:
            self.logger.debug(
                f"{self.match.video_id} {self.count:13d} - looking for stage"
            )
            stage = vf_analytics.get_stage(self.frame)
            if stage is not None:
                self.match.stage = stage
                self.logger.debug(
                    f"{self.match.video_id} {self.count:13d} - stage {stage}"
                )

        if self.match.got_all_vs_info():
            # todo remove this duplicate code
            self.player_rank.set_frame(self.frame)
            self.player_rank.set_youtube_video_title(self.youtube_video_title)

            debug_player_rank = False

            try:
                if self.match.player1rank is None:
                    player1rank = self.player_rank.get_player_rank(1, debug_player_rank)
                    self.match.player1rank = player1rank
                    if player1rank == 0:
                        self.save_cam_frame(
                            "_rank_0_for_player1",
                        )

                if self.match.player2rank is None:
                    player2rank = self.player_rank.get_player_rank(2, debug_player_rank)
                    self.match.player2rank = player2rank
                    if player2rank == 0:
                        self.save_cam_frame(
                            "_rank_0_for_player2",
                        )
            except vf_cv.UnrecognizePlayerRankException as e:
                self.save_cam_frame(f"_unrecognized_rank_{str(e)}")
                # raise e

            self.vs_screen.set_frame(self.frame)
            self.match.date = self.vs_screen.get_date(debug=False)
            print(f"got date {self.match.date}")
            self.match.player1ringname = self.vs_screen.get_ringname(1, False)
            self.match.player2ringname = self.vs_screen.get_ringname(2, False)

            self.state = "fight"
            # print(f"\tstarting fight at {self.count}" )
            self.logger.debug(f"{self.match.video_id} {self.count:13d} - fight")

            if self.process_vs_only:
                return True

            self.skip_frames = (int)(25 / self.interval)

            self.save_cam_frame("start")

            del self.frame
            del self.original_frame
        else:
            self.count = self.count + 1

        return False

    @profile
    def process_fight(self):
        self.old_time_seconds = self.time_seconds

        # if matches twice know endround and no need to get time seconds
        self.time_cv.set_frame(self.frame)

        try:
            self.time_seconds = self.time_cv.get_time_seconds()
        except Exception as a:
            print(f"Exception getting time {a}")
            self.save_cam_frame("invalid_time")
            raise a

        if self.time_seconds == "endround":
            if self.old_time_seconds is None:
                self.count += 10
                return False

            self.time_seconds = self.old_time_seconds
            self.time_matches = 2

            if self.SAVE_PIC_ALL:
                self.save_cam_frame(f"fight_{self.timestr}_endround")

            self.count += 1

            self.endround = True
            return False

        if self.old_time_seconds == "endround":
            self.old_time_seconds = self.time_seconds

        if (
            self.time_seconds is not None
            and self.old_time_seconds is not None
            and int(self.old_time_seconds) != int(self.time_seconds)
            and int(self.old_time_seconds) != int(self.time_seconds) + 1
            and not self.endround
        ):
            self.save_cam_frame("invalid_time")
            raise UnexpectedTimeException(
                f"Unexpected time seconds old {self.old_time_seconds}   new {self.time_seconds}"
            )

        if (
            self.skip_beginning_of_round()
            or ((self.time_seconds != self.old_time_seconds) and not self.endround)
            or self.old_time_seconds is None
        ):
            self.count += int(self.frame_rate * self.interval)

            # if self.SAVE_PIC_ALL:
            # self.save_cam_frame(f"fight_skip")

            if self.SAVE_PIC_ALL:
                self.save_cam_frame(
                    f"fight_skip_{self.skip_beginning_of_round()}_{self.old_time_seconds}_{self.time_seconds}_{self.endround}"
                )

            del self.frame
            del self.original_frame
            # print(f"\tskip {self.time_seconds} vs {self.old_time_seconds} skip: {self.skip_beginning_of_round()}")

            return False

        # time_ms = self.time_cv.get_time_ms()

        self.old_time = self.timestr
        # self.timestr = f"{self.time_seconds}.{time_ms}"
        self.timestr = f"{self.time_seconds}"

        if (
            self.old_time == self.timestr
            and self.timestr != "45.00"
            and self.time_seconds != ""
        ):
            self.time_matches = self.time_matches + 1
        else:
            self.time_matches = 0

        player_num = 0

        self.winning_frame.set_frame(self.frame)
        is_ro = self.winning_frame.is_ringout()
        if (
            self.time_matches >= 2
            or self.endround
            or (
                self.time_matches >= 1
                and (
                    is_ro
                    or self.winning_frame.is_ko()
                    or self.winning_frame.is_excellent()
                    or self.winning_frame.is_timeout()
                )
            )
        ):
            self.winning_round.set_frame(self.frame)
            player_num = self.winning_round.is_winning_round(False, self.match.stage)

        else:
            # print(f"advancing cause no match {int(self.frame_rate * 0.5)}")
            if self.SAVE_PIC_ALL:
                self.save_cam_frame(
                    f"fight_{self.timestr}_no_match_advance_{self.time_matches}_matches_endround_{self.endround}_timeout_{is_ro}"
                )

            self.count += int(self.frame_rate * 0.5)
            del self.frame
            del self.original_frame
            return False

        if player_num == 0:
            self.count += 1
            if self.SAVE_PIC_ALL and not self.DONT_SAVE:
                self.save_cam_frame(
                    f"fight_{self.timestr}_{self.time_seconds}_endround{self.endround}_no_winner_zero_{player_num}_{self.time_matches}_KO{self.winning_frame.is_ko()}_RO{self.winning_frame.is_ringout()}_EX{self.winning_frame.is_excellent()}_TO{self.winning_frame.is_timeout()}"
                )

            del self.frame
            del self.original_frame

            return False

        self.winning_frame.set_frame(self.frame)
        is_ro = self.winning_frame.is_ringout()
        is_excellent = not is_ro and self.winning_frame.is_excellent()
        is_ko = not is_excellent and not is_ro and self.winning_frame.is_ko()
        is_to = (
            not is_ko
            and not is_ro
            and not is_excellent
            and self.winning_frame.is_timeout()
        )

        if self.timestr != self.old_time and not self.endround:
            # try advance half a second
            self.count += int(self.frame_rate * 0.5)

            # print(f"advancing {int(self.frame_rate * 0.5)} frames")
            del self.frame
            del self.original_frame
            return False

        self.current_round.winning_player_num = player_num
        if is_ro:
            self.current_round.victory = vf_data.Round.RO
            # print(f"{self.count} got RO for player {player_num}")
            # self.save_cam_frame("ro")
            self.save_cam_frame(f"fight_{self.timestr}_ro_{player_num}")
        elif is_excellent:
            self.current_round.victory = vf_data.Round.EX
            # print(f"{self.count} got EX for player {player_num}")
            # self.save_cam_frame("ex")
            self.save_cam_frame(f"fight_{self.timestr}_ex_{player_num}")
        elif is_ko:
            self.current_round.victory = vf_data.Round.KO
            # print(f"{self.count} got KO for player {player_num}")
            # self.save_cam_frame("ko")
            self.save_cam_frame(f"fight_{self.timestr}_ko_{player_num}")
        elif is_to:
            self.current_round.victory = vf_data.Round.TO
            # print(f"{self.count} got KO for player {player_num}")
            # self.save_cam_frame("ko")
            self.save_cam_frame(f"fight_{self.timestr}_to_{player_num}")
        else:
            self.count = self.count + 1
            self.current_round.winning_player_num = 0
            # print(f"{self.count} unknown way to victory for {player_num} skipping")
            self.count += int(self.frame_rate * self.interval)

            self.save_cam_frame(f"fight_{self.timestr}_winning_unknown{player_num}")

            del self.frame
            del self.original_frame
            return False

        try:
            self.timestr = None
            try:
                time_ms = "00"
                # self.time_seconds = self.time_cv.get_time_seconds(self.frame)
                # time_ms = self.time_cv.get_time_ms()
                self.timestr = f"{self.time_seconds}.{time_ms}"
            except Exception as a:
                self.save_cam_frame("invalid time")
                self.logger.error(
                    f"Exception occured getting time frame: {self.count} error: {a}"
                )
                self.logger.error(traceback.format_exc())
                self.timestr = "na"

            suffix = ""
            p1r = self.match.player1rank
            p2r = self.match.player2rank

            if is_excellent:
                suffix = f"{p1r}_{self.match.player1character}_vs_{p2r}_{self.match.player2character}_excellent_for_player{player_num}"
            elif is_ro:
                suffix = f"{p1r}_{self.match.player1character}_vs_{p2r}_{self.match.player2character}_ringout_for_player{player_num}"
            elif is_ko:
                suffix = f"{p1r}_{self.match.player1character}_vs_{p2r}_{self.match.player2character}_knockout_for_player{player_num}"
            else:
                suffix = f"{p1r}_{self.match.player1character}_vs_{p2r}_{self.match.player2character}_unknownwin_for_player{player_num}"

            self.save_cam_frame(
                f"{0}_{1}_{suffix}_{self.timestr}",
            )
        except:
            self.logger.error(
                f"{self.match.video_id} {self.count:13d} ERROR write to csv"
            )
            self.logger.error(traceback.format_exc())

        if self.match.player1rank == 0:
            self.logger.error(
                f"{self.match.video_id} {self.count:13d} - round is over but player 1 rank is 0"
            )

        if self.match.player2rank == 0:
            self.logger.error(
                f"{self.match.video_id} {self.count:13d} - round is over but player 2 rank is 0"
            )

        self.current_round.seconds = int(self.cap.frames_read / self.frame_rate)
        self.current_round.remaining_time = self.timestr

        self.match.add_finished_round(self.current_round)

        if self.match.count_rounds_won(1) < 3 and self.match.count_rounds_won(2) < 3:
            self.current_round = vf_data.Round()
            self.endround = False
            self.skip_frames = 10 / self.interval
            self.time_matches = 0
            self.time_seconds = None
            self.old_time_seconds = None
        else:
            # print("advancing one frame")
            self.count += 1
            return True

        if self.match.get_round_num() > 5:
            raise Exception(f"Invalid round number {self.current_round.num}")

        # print(f"advancing {int(self.frame_rate * 0.5)} frames at end")
        self.count += int(self.frame_rate * 0.5)
        del self.frame
        del self.original_frame
        return False

    def process_fight_shun_drinks(self, actual_count):
        if self.state != "fight":
            return
        if (
            self.match.player1character != "Shun"
            and self.match.player2character != "Shun"
        ):
            return
        if self.current_round.player1_drink_points_at_start is not None:
            return
        if self.current_round.player2_drink_points_at_start is not None:
            return

        original_height = self.frame.shape[0]
        if original_height != 720:
            self.frame = cv2.resize(self.frame, (1280, 720))

        if self.match.get_round_num() == 1:
            if self.match.player1character == "Shun":
                self.current_round.player1_drink_points_at_start = 0
            if self.match.player2character == "Shun":
                self.current_round.player2_drink_points_at_start = 0

            return
        if (self.count - actual_count) > 70:
            return

        print(
            f"\nprocessing shun fight drinks round {self.match.get_round_num()} {self.state} {self.count - actual_count}"
        )
        self.time_cv.set_frame(self.frame)

        try:
            time_seconds = self.time_cv.get_time_seconds()
            print(f"looking for shun drinks got time: {time_seconds}")
            if time_seconds != "45":
                return
        except Exception as a:
            return

        self.drinks.set_frame(self.frame)

        if self.match.player1character == "Shun":
            self.current_round.player1_drink_points_at_start = (
                self.drinks.get_drink_points(1)
            )
            self.save_cam_frame(
                f"player1_character-shun-drinks_{self.match.stage}_{self.current_round.player1_drink_points_at_start}",
                force_save=True,
            )

        if self.match.player2character == "Shun":
            self.current_round.player2_drink_points_at_start = (
                self.drinks.get_drink_points(2)
            )
            self.save_cam_frame(
                f"player2_character-shun-drinks_{self.match.stage}_{self.current_round.player2_drink_points_at_start}",
                force_save=True,
            )

    def remaining_video(self):
        return self.cap.queue.qsize() > 0


class PrematureMatchFinishException(Exception):
    pass


class UnexpectedTimeException(Exception):
    pass
