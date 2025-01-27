"""This module provide functions to extract information from a VFES/US game frame"""

import traceback
import os
import time
from enum import Enum
from datetime import datetime
import cv2
import threading

from line_profiler import profile

import vf_data.match
import vf_analytics
import vf_cv.winning_frame
import vf_cv.winning_round
import vf_cv.character
import vf_cv.vs_screen
import vf_cv.revo
import vf_cv.video_capture_async
import vf_cv.config


from vf_data.win_probability import WinProbability

from obs import ObsHelper


class State(Enum):
    BEFORE_VS = 0
    VS_SCREEN = 1
    BEFORE_FIGHT = 2
    BEFORE_ENDROUND = 3
    ENDROUND = 4


class MatchAnalyzer:
    """This is the class that analyzes a video of a match, extracts and stores data into other classes"""

    def __init__(
        self,
        cap: vf_cv.video_capture_async.VideoCaptureAsync,
        logger,
        jpg_folder,
        interval,
        frame_rate,
        youtube_video_title,
        process_vs_only,
        config: vf_cv.config.Config = None,
    ):
        self.match = vf_data.Match()

        self.match.video_url = None
        if hasattr(cap, "src"):
            self.match.video_url = cap.src

        self.match.video_frame_rate = frame_rate
        if hasattr(cap, "get_frame_rate"):
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
        self.youtube_video_title = youtube_video_title
        self.process_vs_only = process_vs_only
        self.config = config
        self.round_start_count = None
        self.obs_helper: ObsHelper = None
        self.win_probability = WinProbability()

    @profile
    def analyze_next_match(
        self,
        video_id="n/a",
        cam=-1,
        frame_count=None,
        start_frame=0,
        obs_helper: ObsHelper = None,
    ):
        self.match = vf_data.Match()

        self.match.video_url = None
        if hasattr(self.cap, "src"):
            self.match.video_url = self.cap.src

        self.match.video_frame_rate = None
        if hasattr(self.cap, "get_frame_rate"):
            self.match.video_frame_rate = self.cap.get_frame_rate()

        self.time_seconds = None
        self.time_matches = 0
        self.timestr = None

        end_frame = frame_count

        self.count = start_frame + 1

        self.state = State.BEFORE_VS

        self.current_round = vf_data.Round()
        self.match.video_id = video_id

        self.skip_frames = 0
        self.obs_helper = obs_helper

        result = None

        if cam != -1:
            jpg_folder = "assets/jpg/cam"
            if not os.path.exists(jpg_folder):
                os.makedirs(jpg_folder)

            result = self.get_next_frame(cam, video_id, 0)
        else:
            actual_count = self.count - 1

            result = self.get_next_frame(cam, video_id, actual_count)

            if result is None:
                time.sleep(5)
                result = self.get_next_frame(cam, video_id, actual_count)

        self.save_cam_frame("cam_test")

        while cam != -1 or (
            ((self.cap.frames_read < end_frame or cam != -1))
            and self.frame is not None
            and result is not None
        ):
            actual_count = result

            debug_beta = False
            if self.state != State.BEFORE_VS and vf_cv.revo.REVO.is_beta_screen(
                self.frame, debug_beta
            ):
                self.save_cam_frame("revo")
                raise PrematureMatchFinishException("Found Revo BETA Frame")

            result = self.analyze_next_frame()
            if result is not None:
                print("\t\tResult is not none, stopping to process match!")
                return result

            # if (cam == -1):
            result = self.get_next_frame(cam, video_id, actual_count)
            # else:
            # result, frame = self.cap.read()
            # if (ret):
            # self.frame = frame
            # cv2.imshow("cam", self.frame)
            # cv2.waitKey()

            if result is None:
                print("\tnext frame is none")

        if self.state != State.BEFORE_VS:
            raise PrematureMatchFinishException(f"Unexpected state {self.state}")

        if self.cap.frames_read >= end_frame:
            print(f"returning 0 because {self.cap.frames_read} >= {end_frame}")
            return 0

    @profile
    def get_next_frame(self, cam, video_id, actual_count):
        self.frame = None

        count_int = int(self.count)

        # use epoch time for cam
        if self.config.cam_int != -1:
            # count_int = int(time.time() * 1000)
            # self.count = count_int

            if self.skip_frames > 0:
                seconds_to_sleep = self.skip_frames / self.frame_rate
                dt = datetime.now().strftime("%Y%m%d%H%M%S")
                print(
                    f"\t\t{dt} CAM sleeping START {self.skip_frames} frames, {seconds_to_sleep} seconds"
                )

                start_time = time.time()  # Record the start time
                while (
                    time.time() - start_time < seconds_to_sleep
                ):  # Loop until 5 seconds have passed
                    ret, frame = self.cap.read()
                    if ret:
                        self.frame = frame
                    time.sleep(0.1)  # Optional: Sleep to reduce CPU usage

                dt = datetime.now().strftime("%Y%m%d%H%M%S")
                print(f"\t\t{dt} CAM sleeping END")

                # self.save_cam_frame(f"after_sleep_{self.skip_frames}")

            self.skip_frames = 0

            ret, frame = self.cap.read()
            if ret:
                self.frame = frame

            # self.count += int((self.frame_rate * self.interval) * self.skip_frames)
            # count_int = int(self.count)
            # self.skip_frames = 0
            return 1

        self.original_frame = None

        self.frame = None

        if cam != -1:
            actual_count = self.count - 1

        shun_drinks = False

        while actual_count < count_int or self.frame is None:
            try:
                self.frame = self.cap.read()
                if not shun_drinks:
                    shun_drinks = self.process_fight_shun_drinks(actual_count)
                    if shun_drinks:
                        count_int += int(self.frame_rate)
            except:
                time.sleep(5)

                self.frame = self.cap.read()
                if not shun_drinks:
                    shun_drinks = self.process_fight_shun_drinks(actual_count)
                    if shun_drinks:
                        count_int += int(self.frame_rate)

            if self.frame is None:
                break
            actual_count = actual_count + 1

        if self.frame is None:
            print(
                f"!!!! Skipping frame {self.cap.frames_read:13d} because self.frame is none"
            )
            self.logger.warning(
                f"Skipping frame {self.cap.frames_read:13d} because self.frame is none"
            )
            self.count += 1
            return None

        return actual_count

    @profile
    def analyze_next_frame(self):
        self.original_frame = self.frame
        if not hasattr(self.frame, "shape"):
            return

        self.frame_height = self.frame.shape[0]  # Get the dimensions of the frame

        if self.state == State.BEFORE_VS:
            self.process_before_vs()
            return
        if self.state == State.VS_SCREEN:
            if self.process_vs():
                return 0
            return
        if self.state == State.BEFORE_FIGHT:
            self.process_before_fight()
        elif self.state == State.BEFORE_ENDROUND:
            self.process_before_endround()
        if self.state == State.ENDROUND and self.process_endround():
            print(
                f"\t\tnect frame returning {self.count} because ENDROUND and process_endround"
            )
            return self.count

    def remove_jpegs(self):
        images_folder = self.jpg_folder + f"/{self.matches_processed}"

        if not os.path.exists(images_folder):
            return

        filelist = [f for f in os.listdir(images_folder) if f.endswith(".png")]
        for f in filelist:
            if os.path.exists(os.path.join(images_folder, f)):
                os.remove(os.path.join(images_folder, f))

        if os.path.exists(images_folder):
            os.rmdir(images_folder)

    def save_cam_frame(self, suffix, force_save=False):
        if self.config.dont_save_any_images and not force_save:
            return

        if not hasattr(self, "frame") or self.frame is None:
            return

        # if self.matches_processed != 0 or self.matches_processed != 54 or self.matches_processed != 2 or self.matches_processed != 9 or self.matches_processed != 83 or self.matches_processed != 64 or self.matches_processed != 137 or self.matches_processed != 169:
        # return

        if not os.path.exists(self.jpg_folder):
            os.makedirs(self.jpg_folder)

        if not os.path.exists(self.jpg_folder + f"/{self.matches_processed}"):
            os.makedirs(self.jpg_folder + f"/{self.matches_processed}")

        if hasattr(self.cap, "frames_read"):
            original_out_filename = (
                self.jpg_folder
                + f"/{self.matches_processed}/"
                + str(f"{self.cap.frames_read}_{suffix}")
                + f".{self.config.save_image_format}"
            )
        else:
            time_str = datetime.now().strftime("%Y%m%d%H%M%S")

            original_out_filename = (
                self.jpg_folder
                + f"/{self.matches_processed}/"
                + str(f"{time_str}_{suffix}")
                + f".{self.config.save_image_format}"
            )

        if not os.path.isfile(original_out_filename):
            if self.config.save_image_format == "webp":
                cv2.imwrite(
                    original_out_filename, self.frame, [cv2.IMWRITE_WEBP_QUALITY, 100]
                )
            else:
                cv2.imwrite(original_out_filename, self.frame)

    @profile
    def process_before_vs(self):
        self.logger.debug(f"BEFORE - searching for vs frame count {self.count}")
        stage = None

        self.vs_screen.set_frame(self.frame)
        if self.vs_screen.is_vs_ver1():
            stage = self.vs_screen.get_stage()
            print(f"\tVS screen got stage {stage}")

        if stage is not None:
            formatted_match_id = "%02d" % (self.matches_processed + 1,)
            self.match.id = f"{self.match.video_id}-{formatted_match_id}"
            self.match.stage = stage
            if hasattr(self.cap, "frames_read"):
                self.match.vs_frame_seconds = int(
                    self.cap.frames_read / self.frame_rate
                )
            else:
                self.match.vs_frame_seconds = 1

            print("\tsetting state to vs")
            if self.config.auto_record:
                try:
                    self.obs_helper.start_recording()
                except Exception as e:
                    print(f"could not start recording {e}")
                    print(traceback.format_exc())
                    self.logger.error(f"could not start recording {e}")
                    self.logger.error(traceback.format_exc())

            self.state = State.VS_SCREEN
            self.logger.debug(
                f"{self.match.video_id} {self.count:13d} - got stage {stage} and setting to vs {self.match.player1character} vs {self.match.player2character}"
            )
        else:
            # self.save_cam_frame("before_vs_invalid_stage")
            self.count += int(self.frame_rate * self.interval * 40)
            del self.frame
            del self.original_frame

        self.count += 1

    def skip_beginning_of_round(self):
        return (
            self.time_seconds == "endround"
            or self.time_seconds == "43"
            or self.time_seconds == "44"
            or self.time_seconds == "45"
        )

    @profile
    def process_vs(self):
        # print(f"{self.count} processing vs {self.match.player1character} vs {self.match.player2character} on {self.match.stage}")
        print("\tprocessing vs")
        if self.match.player1character is None:
            print("\t\tgetting character 1 name")
            self.character.set_frame(self.frame)
            self.character.set_youtube_video_title(self.youtube_video_title)

            player1character = self.character.get_character_name(1)
            if player1character is not None:
                self.match.player1character = player1character
                self.logger.debug(
                    f"{self.match.video_id} {self.count:13d} - player 1 character {player1character}"
                )

        if self.match.player2character is None:
            print("\t\tgetting character 2 name")
            self.character.set_frame(self.frame)
            player2character = self.character.get_character_name(2)
            if player2character is not None:
                self.match.player2character = player2character
                self.logger.debug(
                    f"{self.match.video_id} {self.count:13d} - player 2 character {player2character}"
                )

        if self.match.stage is None:
            print("\t\tgetting stage")
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
            except vf_cv.UnrecognizePlayerRankException as e:
                self.logger.warn("unrecognized rank player 1")

            try:
                if self.match.player2rank is None:
                    player2rank = self.player_rank.get_player_rank(2, debug_player_rank)
                    self.match.player2rank = player2rank
            except vf_cv.UnrecognizePlayerRankException as e:
                self.logger.warn("unrecognized rank player 2")

            self.vs_screen.set_frame(self.frame)
            self.match.date = self.vs_screen.get_date(debug=False)

            self.match.player1ringname = self.vs_screen.get_ringname(1, False)
            self.match.player2ringname = self.vs_screen.get_ringname(2, False)

            self.state = State.BEFORE_FIGHT
            print("\tState = BEFORE_FIGHT (start looking for start of fight)")
            try:
                self.round_start_count = self.cap.frames_read
            except Exception as e:
                self.logger.debug("skipping because of CAM")

            self.logger.debug(f"{self.match.video_id} {self.count:13d} - fight")
            self.save_cam_frame(
                f"vs_screen_complete_{self.match.player1rank}_{self.match.player1character}_{self.match.player1ringname}_vs_{self.match.player2rank}_{self.match.player2character}_{self.match.player2ringname}_on_{self.match.stage}"
            )
            if self.process_vs_only:
                return True

            # if self.config.cam_int != -1:
            # self.skip_frames = self.frame_rate * 25
            # else:
            # self.skip_frames = (int)(25 / self.interval)

            # self.save_cam_frame("start")

            del self.frame
            del self.original_frame
        else:
            print("\t\tdid not get all info")
            self.count = self.count + 1

        return False

    @profile
    def process_before_fight(self):
        self.time_cv.set_frame(self.frame, self.match.stage)
        self.old_time_seconds = self.time_seconds

        try:
            self.time_seconds = self.time_cv.get_time_seconds()
            if (
                self.time_seconds == "44"
                or self.time_seconds == "43"
                or self.time_seconds == "42"
                or self.time_seconds == "41"
            ):
                self.state = State.BEFORE_ENDROUND
                self.save_cam_frame("round_start")
                return
            else:
                if self.config.save_all_images:
                    self.save_cam_frame(f"before_fight_{self.time_seconds}")
        except vf_cv.InvalidTimeException:
            return
        except vf_cv.UnrecognizeTimeDigitException:
            return
        except IndexError:
            return

            # if not self.skip_beginning_of_round():
            # Will consider round started after not endround (but really beginning of)
            # if (not self.time_cv.is_endround_other(False)):
            self.state = State.BEFORE_ENDROUND
            print(
                f"\tState = BEFORE_ENDROUND (start looking for the end of the round) at {self.time_seconds} seconds"
            )

    def process_damage_data(self, player_num):
        (green, black, grey, white, red) = self.winning_frame.get_player_health(
            player_num
        )

        if white == 0 and red == 0:
            self.current_round.current_combo_damage[3 - player_num] = 0
            self.current_round.combo_hits[3 - player_num] = 0

            try:
                self.obs_helper.hide_text_overlay(3 - player_num)
            except Exception as e:
                self.logger.debug(f"OBS exception occured {e}")

        if self.current_round.first_strike_player_num == None:
            if red > 0 or white > 0 or black > 0 or grey > 0:

                try:
                    self.obs_helper.first_strike(3 - player_num)
                    self.obs_helper.win_probability_visibility(True)
                except Exception as e:
                    self.logger.debug(f"OBS exception occured {e}")

                self.current_round.first_strike_player_num = 3 - player_num
                self.save_cam_frame(
                    f"first_strike_p{self.current_round.first_strike_player_num}"
                )
                return

        if white > 0 or red > 0:
            damage_percent = (red + white) / (red + black + green + white)
            damage_percent_int = round(damage_percent * 100)

            if (
                damage_percent_int
                > self.current_round.current_combo_damage[3 - player_num] + 2
            ):
                if damage_percent_int > self.current_round.max_damage[3 - player_num]:
                    self.current_round.max_damage[3 - player_num] = damage_percent_int

                self.current_round.combo_hits[3 - player_num] = (
                    self.current_round.combo_hits[3 - player_num] + 1
                )

                if self.current_round.combo_hits[3 - player_num] >= 2 or (
                    damage_percent_int >= 34
                    and self.current_round.combo_hits[3 - player_num] == 1
                ):
                    try:
                        self.obs_helper.combo(
                            playernum=3 - player_num,
                            hits=self.current_round.combo_hits[3 - player_num],
                            damage=damage_percent_int,
                        )

                        # Hide other players overlay just in case
                        self.obs_helper.hide_text_overlay(playernum=player_num)
                    except Exception as e:
                        self.logger.debug(f"OBS exception occured {e}")

                self.current_round.current_combo_damage[3 - player_num] = (
                    damage_percent_int
                )

                debug_string = f"p{3-player_num}_{self.current_round.combo_hits[3 - player_num]}_hits_{damage_percent_int}_dmg"
                self.save_cam_frame(debug_string)

    @profile
    def process_before_endround(self):
        self.old_time_seconds = self.time_seconds

        # if matches twice know endround and no need to get time seconds
        self.time_cv.set_frame(self.frame, self.match.stage)

        # possible_timeover = ((self.cap.frames_read - self.round_start_count) / self.frame_rate) > 64
        # self.winning_round.set_frame(self.frame)

        self.winning_frame.set_frame(self.frame)
        for player_num in range(1, 3):
            self.process_damage_data(player_num)

        possible_to_or_ro = self.winning_frame.is_ringout(False)
        is_endround_other = self.time_cv.is_endround_other()

        time_seconds = None

        try:
            time_seconds = self.time_cv.get_time_seconds()
        except (
            vf_cv.UnexpectedTimeException,
            vf_cv.InvalidTimeException,
            vf_cv.UnrecognizeTimeDigitException,
        ) as e:
            self.save_cam_frame("bad_time")
            self.logger.debug(f"bad_time {e}")

        if not hasattr(self.cap, "frames_read") or self.cap.frames_read % 2 == 0:
            try:
                frames_read = len(self.current_round.frames) + 1

                if hasattr(self.cap, "frames_read"):
                    frames_read = self.cap.frames_read

                image_filename = (
                    self.win_probability.generate_win_prob_chart_with_single_line(
                        round_number=self.match.get_round_num(),
                        stage=self.match.stage,
                        frame_data=self.current_round.frames,
                        frame_num=frames_read,
                        save_to_file=True,
                        p1character=self.match.player1character,
                        p2character=self.match.player2character,
                    )
                )
            except Exception as e:
                print(e)
                repr(e)
                self.logger.error("Could not show image")

        if possible_to_or_ro:
            try:
                # self.old_time_seconds = self.time_cv.get_time_seconds()
                self.old_time_seconds = time_seconds
            except vf_cv.UnrecognizeTimeDigitException as e:
                self.save_cam_frame("unrecognized_time_digit")
                raise e

            self.time_seconds = self.old_time_seconds

            self.state = State.ENDROUND
            print("\tState = ENDROUND (finish up round with who won)")

            if self.config.save_all_images:
                self.save_cam_frame("process_before_endround_pissble_to_ro")

            return False

        if not hasattr(self.cap, "frames_read") or self.cap.frames_read % 2 == 0:
            frames_read = len(self.current_round.frames) + 1

            if hasattr(self.cap, "frames_read"):
                frames_read = self.cap.frames_read

            p1health = self.winning_frame.get_player_health_percent(1)
            p2health = self.winning_frame.get_player_health_percent(2)
            self.current_round.add_frame(
                frame_id=frames_read,
                p1health=p1health,
                p2health=p2health,
                time_remaining_seconds=time_seconds,
            )

        if self.config.save_all_images:
            self.save_cam_frame("process_before_endround_many")
        # check green text area for possbile ringout and timeout
        # don't need to necessarily keep track of elapsed time from the counter (maybe that is faster for time out)?
        # if no green for ring out or time out, then can check round over from p2 bar
        # this is assuming that green check will be less time consuming than getting the time in the first place

        # also may want to break this process_fight into two stages - find endround and then process endround?

        # print(f"\tprocessing fight {self.cap.frames_read - self.round_start_count}  {(self.cap.frames_read - self.round_start_count) / self.frame_rate}")
        try:
            debug_endround_other = False
            if not possible_to_or_ro and is_endround_other:
                if self.old_time_seconds is None:
                    try:
                        self.old_time_seconds = self.time_cv.get_time_seconds()
                    except vf_cv.UnrecognizeTimeDigitException as e:
                        self.save_cam_frame("unrecognized_time_digit")

                    self.time_seconds = self.old_time_seconds
                    print(f"\t\tset old time seconds {self.old_time_seconds}")
                    self.count += 10

                    if self.config.save_all_images:
                        self.save_cam_frame(
                            "process_before_endround_other_endround_count_plus_10"
                        )

                    return False

                self.time_seconds = self.old_time_seconds
                self.time_matches = 2

                if self.config.save_all_images:
                    self.save_cam_frame(
                        f"\t\tprocess_before_endround_{self.timestr}_endround"
                    )

                self.count += int(self.frame_rate * 0.10)

                self.state = State.ENDROUND
                print(
                    f"\tState = ENDROUND (finish up round with who won) with count + {int(self.frame_rate * 0.10)} "
                )

                if self.config.save_all_images:
                    self.save_cam_frame(
                        "process_before_endround_other_endround_set_to_endround"
                    )

                return False

            if not possible_to_or_ro:
                self.count += int(self.frame_rate * 0.25)
                del self.frame
                del self.original_frame

                if self.config.save_all_images:
                    self.save_cam_frame("process_before_endround_skipping")

                return False

            try:
                self.time_seconds = self.time_cv.get_time_seconds()
            except vf_cv.UnrecognizeTimeDigitException as e:
                self.save_cam_frame("unrecognized_time_digit")
                return e

        except Exception as a:
            print(f"Exception getting time {a}")
            self.save_cam_frame("invalid_time")
            raise a

        if self.old_time_seconds == "endround":
            self.old_time_seconds = self.time_seconds

        if (
            self.time_seconds is not None
            and self.old_time_seconds is not None
            and not self.old_time_seconds == "endround"
            and not self.time_seconds == "endround"
            and int(self.old_time_seconds) != int(self.time_seconds)
            and int(self.old_time_seconds) != int(self.time_seconds) + 1
        ):
            self.save_cam_frame("invalid_time")
            raise UnexpectedTimeException(
                f"Unexpected time seconds old {self.old_time_seconds}   new {self.time_seconds}"
            )

    @profile
    def process_endround(self):
        # time_ms = self.time_cv.get_time_ms()

        self.old_time = self.timestr
        # self.timestr = f"{self.time_seconds}.{time_ms}"
        self.timestr = f"{self.time_seconds}"

        player_num = 0

        self.winning_frame.set_frame(self.frame)
        self.time_cv.set_frame(self.frame)

        if self.time_cv.is_endround_other():
            self.count = self.count + 1

            if self.config.save_all_images:
                self.save_cam_frame(
                    f"process_endround_is_endround_other_{self.time_cv.message}"
                )

            return

        try:
            self.time_seconds = self.time_cv.get_time_seconds()
        except vf_cv.UnrecognizeTimeDigitException as e:
            self.save_cam_frame("unrecognized_time_digit")
            raise e

        is_ro = self.winning_frame.is_ringout()
        self.winning_round.set_frame(self.frame)
        player_num = self.winning_round.is_winning_round(False, self.match.stage)

        if player_num == 0:
            self.count += 1
            if self.config.save_all_images and not self.config.dont_save_any_images:
                self.save_cam_frame(
                    f"process_endround_{self.timestr}_{self.time_seconds}_endround_no_winner_zero_{player_num}_{self.time_matches}_KO{self.winning_frame.is_ko()}_RO{self.winning_frame.is_ringout()}_EX{self.winning_frame.is_excellent()}_TO{self.winning_frame.is_timeout()}"
                )

            del self.frame
            del self.original_frame

            return False

        is_excellent = not is_ro and self.winning_frame.is_excellent()
        is_ko = not is_excellent and not is_ro and self.winning_frame.is_ko()
        is_to = self.winning_frame.is_timeout(False)

        self.current_round.winning_player_num = player_num
        if is_to:
            is_ro = False
            is_ko = False
            is_excellent = False
            self.current_round.victory = vf_data.Round.TO
            self.save_cam_frame(f"endround_to_{self.timestr}_player[{player_num}]")
        elif is_ro:
            self.current_round.victory = vf_data.Round.RO
            self.save_cam_frame(f"endround_ro_{self.timestr}_ro_{player_num}")
        elif is_excellent:
            self.current_round.victory = vf_data.Round.EX
            self.save_cam_frame(f"endround_ex_{self.timestr}_ex_{player_num}")
        elif is_ko:
            self.current_round.victory = vf_data.Round.KO
            self.save_cam_frame(f"endround_ko_{self.timestr}_ko_{player_num}")
        else:
            self.count = self.count + 1
            self.current_round.winning_player_num = 0
            # print(f"{self.count} unknown way to victory for {player_num} skipping")
            self.count += int(self.frame_rate * self.interval)

            self.save_cam_frame(f"endround_{self.timestr}_winning_unknown{player_num}")

            del self.frame
            del self.original_frame
            return False

        try:
            self.timestr = None
            try:
                time_ms = "00"
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
            elif is_to:
                suffix = f"{p1r}_{self.match.player1character}_vs_{p2r}_{self.match.player2character}_timeout_for_player{player_num}"
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

        try:
            self.current_round.seconds = int(self.cap.frames_read / self.frame_rate)
        except Exception as e:
            self.logger.debug("skipping because of cam")

        self.current_round.remaining_time = self.timestr

        self.match.add_finished_round(self.current_round)

        if self.match.count_rounds_won(1) < 3 and self.match.count_rounds_won(2) < 3:
            print(f"\t\tcreating new round {self.current_round.num}")
            old_round_frames = len(self.current_round.frames)

            try:
                image_filename = (
                    self.win_probability.generate_win_prob_chart_with_single_line(
                        round_number=(self.match.get_round_num() - 1),
                        stage=self.match.stage,
                        frame_data=self.current_round.frames,
                        frame_num=0,
                        save_to_file=True,
                        p1character=self.match.player1character,
                        p2character=self.match.player2character,
                        winner_player_number=self.current_round.winning_player_num,
                    )
                )
            except:
                self.logger.error("could not save with winner")

            self.current_round = vf_data.Round()

            self.hide_win_prob_later(3)

            if hasattr(self.cap, "frames_read"):
                self.current_round.start_frame_num = self.cap.frames_read
            else:
                self.current_round.start_frame_num = old_round_frames

            self.time_matches = 0
            self.time_seconds = None
            self.old_time_seconds = None
            try:
                self.round_start_count = self.cap.frames_read
            except Exception as e:
                self.logger.debug("skipping because of cam")
            self.state = State.BEFORE_FIGHT
            print("\tState = BEFORE_FIGHT (start looking for start of fight)")

            try:
                self.obs_helper.hide_text_overlay(1)
                self.obs_helper.hide_text_overlay(2)
            except Exception as e:
                self.logger.debug(f"OBS exception occured {e}")

        else:
            self.count += 1
            try:
                self.obs_helper.hide_text_overlay(1)
                self.obs_helper.hide_text_overlay(2)
                self.hide_win_prob_later(5)
            except Exception as e:
                self.logger.debug(f"OBS exception occured {e}")

            return True

        if self.match.get_round_num() > 5:
            raise Exception(f"Invalid round number {self.current_round.num}")

        # print(f"advancing {int(self.frame_rate * 0.5)} frames at end")
        self.count += int(self.frame_rate * 0.5)
        del self.frame
        del self.original_frame
        return False

    def process_fight_shun_drinks(self, actual_count):
        if self.state != State.BEFORE_FIGHT:
            return False
        if (
            self.match.player1character != "Shun"
            and self.match.player2character != "Shun"
        ):
            return False
        if self.current_round.player1_drink_points_at_start is not None:
            return False
        if self.current_round.player2_drink_points_at_start is not None:
            return False

        original_height = self.frame.shape[0]
        if original_height != 720:
            self.frame = cv2.resize(self.frame, (1280, 720))

        if self.match.get_round_num() == 1:
            if self.match.player1character == "Shun":
                self.current_round.player1_drink_points_at_start = 0
            if self.match.player2character == "Shun":
                self.current_round.player2_drink_points_at_start = 0

            return False
        if (self.count - actual_count) > 70:
            return False

        self.time_cv.set_frame(self.frame)

        try:
            time_seconds = self.time_cv.get_time_seconds()
            if time_seconds != "45":
                return False
        except Exception as a:
            return False

        print(
            f"\t\tprocessing drinks for round {self.match.get_round_num()} and time 45 seconds"
        )
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

        print(f"\t\tProcessed shun drinks and returning true")

        return True
        # self.count += int(self.frame_rate * 4)

    def remaining_video(self):
        return self.cap.queue.qsize() > 0

    def hide_win_prob_later(self, delay):
        def target():
            time.sleep(delay)  # Wait for the specified delay
            self.obs_helper.win_probability_visibility(False)

        thread = threading.Thread(target=target)
        thread.start()


class PrematureMatchFinishException(Exception):
    pass


class UnexpectedTimeException(Exception):
    pass
