import traceback
import sys
import os
import time
import cv2

import vf_data.match
import vf_analytics
import vf_cv.winning_frame
import vf_cv.winning_round
import vf_cv.character


class MatchAnalyzer:

    DONT_SAVE = False
    SAVE_PIC_ALL = False

    def __init__(self, cap, logger, jpg_folder, interval, frame_rate):
        self.match = vf_data.Match()
        self.cap = cap
        self.logger = logger

        self.character = vf_cv.Character()
        self.time_cv = vf_cv.Timer()
        self.winning_round = vf_cv.WinningRound()
        self.winning_frame = vf_cv.WinningFrame()
        self.player_rank = vf_cv.PlayerRank()
        self.character = vf_cv.Character()
        self.frame = None
        self.frame_height = 0
        self.frame_rate = 0
        self.count = 0
        self.state = None
        self.jpg_folder = jpg_folder
        self.matches_processed = 0
        self.original_frame = None
        self.interval = interval
        self.frame_rate = frame_rate

    def analyze_next_match(
        self,
        video_id="n/a",
        cam=-1,
        frame_count=None,
        start_frame=0,
    ):

        end_frame = None
        if end_frame is None or end_frame > frame_count:
            end_frame = frame_count

        self.count = start_frame + 1

        self.state = "before"
        current_round = vf_data.Round()
        self.match.video_id = video_id

        skip_frames = 0

        if cam != -1:
            jpg_folder = "assets/jpg/cam"
            if not os.path.exists(jpg_folder):
                os.makedirs(jpg_folder)

        vf_analytics.resolution = "480p"
        actual_count = self.count - 1

        old_time = None
        timestr = None
        time_matches = 0

        time_seconds = None

        while self.count < end_frame or cam != -1:
            count_int = int(self.count)

            # use epoch time for cam
            if cam != -1:
                count_int = int(time.time() * 1000)
                self.count = count_int

            self.frame = None
            if skip_frames > 0 and cam != -1:
                skip_frames -= 1
                if cam != -1:
                    self.cap.read()
                    time.sleep(self.interval)

                continue

            if skip_frames > 0 and cam == -1:
                self.count += int((self.frame_rate * self.interval) * skip_frames)
                count_int = int(self.count)
                skip_frames = 0

            self.original_frame = None

            if (
                self.DONT_SAVE is False
                and cam == -1
                and os.path.isfile(
                    self.jpg_folder + "/" + str(f"{count_int:13d}") + ".jpg"
                )
            ):
                try:
                    filename = self.jpg_folder + "/" + str(f"{count_int:13d}") + ".jpg"
                    self.frame = cv2.imread(filename)
                except Exception as e:
                    self.logger.error(
                        f"{video_id} {self.count:13d} [ERROR] - error reading from image file",
                        file=sys.stderr,
                    )
                    self.logger.error(repr(e))
                    continue
            else:
                self.frame = None

                if cam != -1:
                    actual_count = self.count - 1

                while actual_count < count_int:
                    self.frame = self.cap.read()
                    if self.frame is None:
                        break
                    actual_count = actual_count + 1
                if self.frame is None:
                    self.logger.warning(
                        f"Skipping frame {self.count:13d} because no return"
                    )
                    print("skipping frame because no return")
                    continue

                # if (cam == -1):
                # frame = vf_analytics.remove_black_border(frame, resize_height=480)
                # else:

            if self.frame is None:
                self.count += 1
                print("self.frame none continue")
                continue

            self.original_frame = self.frame
            self.frame_height = self.frame.shape[0]  # Get the dimensions of the frame

            if self.state == "before":
                self.process_before_vs()
                continue
            if self.state == "vs":
                if self.match.player1character is None:
                    self.character.set_frame(self.frame)
                    player1character = self.character.get_character_name(1)
                    if player1character is not None:
                        self.match.player1character = player1character
                        self.logger.debug(
                            f"{video_id} {self.count:13d} - player 1 character {player1character}"
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
                            f"{video_id} {self.count:13d} - player 2 character {player2character}"
                        )
                        self.save_cam_frame(
                            f"player2_character-{player2character}",
                        )

                if self.match.player1ringname is None:
                    player1ringname = vf_analytics.get_ringname(1, self.frame)
                    self.match.player1ringname = player1ringname
                    self.logger.debug(
                        f"{video_id} {self.count:13d} - player 1 is {player1ringname}"
                    )

                if self.match.player2ringname is None:
                    player2ringname = vf_analytics.get_ringname(2, self.frame)
                    self.match.player2ringname = player2ringname
                    self.logger.debug(
                        f"{video_id} {self.count:13d} - player 2 is {player2ringname}"
                    )

                if self.match.stage is None:
                    self.logger.debug(
                        f"{video_id} {self.count:13d} - looking for stage"
                    )
                    stage = vf_analytics.get_stage(self.frame)
                    if stage is not None:
                        self.match.stage = stage
                        self.logger.debug(
                            f"{video_id} {self.count:13d} - stage {stage}"
                        )

                if self.match.got_all_vs_info():
                    self.state = "fight"
                    self.logger.debug(f"{video_id} {self.count:13d} - fight")
                    got_all_frame_count = self.count

                    skip_frames = (int)(25 / self.interval)
                    # skipFrames for 1
                    # skipFrames=28
                    print(f"got all match info: {self.count:13d} - fight")
                    self.save_cam_frame("start")

                    del self.frame
                    del self.original_frame

                    continue
                # else:
                # save_cam_frame(jpg_folder, original_frame, frame, count, "vs")

            if self.state == "fight":
                old_time_seconds = time_seconds

                self.time_cv.set_frame(self.frame)
                time_seconds = self.time_cv.get_time_seconds()

                if (
                    (
                        time_seconds == "43"
                        or time_seconds == "44"
                        or time_seconds == "45"
                    )
                    or (time_seconds != old_time_seconds)
                    or old_time_seconds is None
                ):
                    self.count += int(self.frame_rate * self.interval)

                    del self.frame
                    del self.original_frame
                    continue

                time_ms = self.time_cv.get_time_ms()

                old_time = timestr
                timestr = f"{time_seconds}.{time_ms}"

                if self.SAVE_PIC_ALL:
                    self.save_cam_frame(f"fight_{timestr}_")

                #            print(timestr)
                #            cv2.imshow("image", frame)
                # cv2.waitKey()

                if old_time == timestr and timestr != "45.00" and time_seconds != "":
                    time_matches = time_matches + 1
                else:
                    time_matches = 0

                player_num = 0

                if time_matches >= 4:
                    self.winning_round.set_frame(self.frame)
                    player_num = self.winning_round.is_winning_round(False)
                else:
                    self.count += 1
                    del self.frame
                    del self.original_frame
                    continue

                if player_num == 0:
                    # logger.debug(f"{count_int} could not determine which player won so skipping")
                    # save_cam_frame(jpg_folder, original_frame, frame, count, f"fight_{time_seconds}_{time_ms}")
                    self.count += 1
                    del self.frame
                    del self.original_frame
                    continue

                self.winning_frame.set_frame(self.frame)
                is_ro = self.winning_frame.is_ringout()
                is_excellent = not is_ro and self.winning_frame.is_excellent()
                is_ko = not is_excellent and not is_ro and self.winning_frame.is_ko()

                self.player_rank.set_frame(self.frame)
                if self.match.player1rank == 0:
                    try:
                        player1rank = self.player_rank.get_player_rank(1)
                        self.match.player1rank = player1rank
                        self.logger.debug(
                            f"{video_id} {self.count:13d} - player1rank {player1rank}"
                        )
                        if player1rank == 0:
                            self.save_cam_frame(
                                "_rank_0_for_player1",
                            )
                    except:
                        self.match.player1rank = 0

                if self.match.player2rank == 0:
                    player2rank = self.player_rank.get_player_rank(2)
                    self.match.player2rank = player2rank
                    self.logger.debug(
                        f"{video_id} {self.count:13d} - player2rank {player2rank}"
                    )
                    if player2rank == 0:
                        self.save_cam_frame(
                            "_rank_0_for_player2",
                        )

                if timestr != old_time:
                    self.count += int(self.frame_rate * self.interval) * 3
                    del self.frame
                    del self.original_frame
                    continue

                self.logger.debug(
                    f"{video_id} {self.count:013d} - player {player_num} won the match"
                )

                current_round.winning_player_num = player_num
                if is_ro:
                    current_round.victory = vf_data.Round.RO
                    print(f"{self.count} got RO for player {player_num}")
                    self.save_cam_frame("ro")
                elif is_excellent:
                    current_round.victory = vf_data.Round.EX
                    print(f"{self.count} got EX for player {player_num}")
                    self.save_cam_frame("ex")
                elif is_ko:
                    current_round.victory = vf_data.Round.KO
                    print(f"{self.count} got KO for player {player_num}")
                    self.save_cam_frame("ko")
                else:
                    current_round.winning_player_num = 0
                    print(
                        f"{self.count} unknown way to victory for {player_num} skipping"
                    )
                    self.count += int(self.frame_rate * self.interval)

                    self.save_cam_frame("unknown_skip")

                    del self.frame
                    del self.original_frame
                    continue

                try:
                    timestr = None
                    try:
                        time_seconds = self.time_cv.get_time_seconds(self.frame)
                        time_ms = self.time_cv.get_time_ms()
                        timestr = f"{time_seconds}.{time_ms}"
                    except Exception as a:
                        self.logger.error(
                            f"Exception occured getting time frame: {frame_count} error: {a}"
                        )
                        self.logger.error(traceback.format_exc())
                        timestr = "na"

                    suffix = ""
                    p1r = self.match.player1rank
                    p2r = self.match.player2rank

                    if is_excellent:
                        suffix = f"{p1r}_{player1character}_vs_{p2r}_{player2character}_excellent_for_player{player_num}"
                    elif is_ro:
                        suffix = f"{p1r}_{player1character}_vs_{p2r}_{player2character}_ringout_for_player{player_num}"
                    elif is_ko:
                        suffix = f"{p1r}_{player1character}_vs_{p2r}_{player2character}_knockout_for_player{player_num}"
                    else:
                        suffix = f"{p1r}_{player1character}_vs_{p2r}_{player2character}_unknownwin_for_player{player_num}"

                    self.save_cam_frame(
                        f"{0}_{1}_{suffix}_{timestr}",
                    )
                except:
                    self.logger.error(f"{video_id} {self.count:13d} ERROR write to csv")
                    self.logger.error(traceback.format_exc())

                self.logger.debug(
                    f"{video_id} {self.count:13d} - round {self.match.get_round_num()} finished player {player_num} won"
                )

                if self.match.player1rank == 0:
                    self.logger.error(
                        f"{video_id} {self.count:13d} - round is over but player 1 rank is 0"
                    )

                if self.match.player2rank == 0:
                    self.logger.error(
                        f"{video_id} {self.count:13d} - round is over but player 2 rank is 0"
                    )

                current_round.seconds = int(self.count / self.frame_rate)

                self.match.add_finished_round(current_round)
                if (
                    self.match.count_rounds_won(1) < 3
                    and self.match.count_rounds_won(2) < 3
                ):
                    current_round = vf_data.Round()

                    if cam == -1:
                        skip_frames = 10 / self.interval
                    time_matches = 0
                else:
                    return self.count

            self.count += int(self.frame_rate * self.interval)
            del self.frame
            del self.original_frame
        if self.state != "before":
            self.logger.error(f"{video_id} {self.count:13d} - premature match aborted")

        return 0

    def save_cam_frame(self, suffix):
        if self.DONT_SAVE:
            return
        if not os.path.exists(self.jpg_folder + "/original/"):
            os.makedirs(self.jpg_folder + "/original/")

        original_out_filename = (
            self.jpg_folder + "/original/" + str(f"{self.count}_{suffix}") + ".png"
        )

        if not os.path.isfile(original_out_filename):
            cv2.imwrite(original_out_filename, self.frame)

    def process_before_vs(self):
        self.logger.debug(f"BEFORE - searching for vs frame count {self.count}")
        stage = None
        if vf_analytics.is_vs(self.frame):
            if self.frame_height != 480:
                frame_480p = cv2.resize(self.frame, (854, 480))
            else:
                frame_480p = self.frame

            stage = vf_analytics.get_stage(frame_480p)
            if stage is None:
                self.save_cam_frame("invalid_is_vs")

        if self.SAVE_PIC_ALL:
            self.save_cam_frame("invalid_is_vs")

        if stage is not None:
            formatted_match_id = "%02d" % (self.matches_processed + 1,)
            self.match.id = f"{self.match.video_id}-{formatted_match_id}"
            self.match.stage = stage
            self.match.vs_frame_seconds = int(self.count / self.frame_rate)

            self.state = "vs"
            self.logger.debug(
                f"{self.match.video_id} {self.count:13d} - got stage {stage} and setting to vs"
            )

            print(
                f"{self.match.video_id} {self.count:13d} - got stage {stage} and setting to vs"
            )
        else:
            self.count += int(self.frame_rate * self.interval * 40)
            del self.frame
            del self.original_frame

        self.count += 1
