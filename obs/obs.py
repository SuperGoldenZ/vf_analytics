import obsws_python as obs
import traceback
import threading


class ObsHelper:
    SECRET = "iiXm59Yq0HOTSvYj"
    SCENE_NAME = "REVO"

    def __init__(self, display_text=False, win_probability=True):
        self.cl = obs.ReqClient(
            host="192.168.56.1", port=4455, password=self.SECRET, timeout=3
        )
        self.display_text = display_text
        self.win_probability = win_probability
        self.visibility = [False, False]
        self.win_probability_visibility_flag = False
        self.vs_win_probability_visibility_flag = False

    def set_item_visible(
        self, visibility=True, scene_name=SCENE_NAME, item_name="P1Text"
    ):
        scene_items = self.cl.get_scene_item_list(scene_name).scene_items
        item_id = None
        for item in scene_items:
            if item["sourceName"] == item_name:
                item_id = item["sceneItemId"]

        self.cl.set_scene_item_enabled(
            scene_name=scene_name, item_id=item_id, enabled=visibility
        )
        return None

    def set_item_source(self, item_name="P1Text", text="Default", color="0x000000FF"):
        input_settings = self.cl.get_input_settings(item_name).input_settings
        input_settings["text"] = text
        input_settings["color"] = int(color, 16)
        input_settings["color1"] = int(color, 16)
        input_settings["color2"] = int(color, 16)

        self.cl.set_input_settings(
            name=item_name, settings=input_settings, overlay=True
        )
        return None

    def start_recording(self):
        self.cl.start_record()

    def stop_recording(self):
        status = self.cl.get_record_status()
        if not status.output_active:
            return False

        stop_result = self.cl.stop_record()
        if not hasattr(stop_result, "output_path"):
            print(f"{stop_result} does not have output path!")
        return stop_result.output_path

    def first_strike(self, playernum):
        if not self.display_text:
            return

        def target():
            self.set_item_source(
                f"P{playernum}Text", "First\nStrike!", color="0xFF000000"
            )
            self.set_item_source(f"P{playernum}Text Background", color="0x7DD1D1D1")

        thread = threading.Thread(target=target)
        thread.start()

        if not self.visibility[playernum - 1]:
            self.set_item_visible(
                scene_name=ObsHelper.SCENE_NAME, item_name=f"P{playernum}Text"
            )
            self.set_item_visible(
                scene_name=ObsHelper.SCENE_NAME,
                item_name=f"P{playernum}Text Background",
            )
            self.visibility[playernum - 1] = True

        thread.join()

    def catbas(self, playernum):
        self.set_item_source(f"P{playernum}Text", "CAT\nBAS", color="0xFF0000FF")
        self.set_item_visible(
            scene_name=ObsHelper.SCENE_NAME, item_name=f"P{playernum}Text"
        )
        self.set_item_visible(
            scene_name=ObsHelper.SCENE_NAME, item_name=f"P{playernum}Text Background"
        )

    def combo(self, playernum, hits, damage):
        if not self.display_text:
            return

        # print(f"\t\tP{playernum} {hits} hit\n{damage}%")
        if hits == 1:
            self.set_item_source(
                f"P{playernum}Text", f"{hits} hit\n{damage}%", color="0xFFFFFFFF"
            )
            self.set_item_source(
                f"P{playernum}Text Background",
                f"{hits} hit\n{damage}%",
                color="0xFF0000FF",
            )
        else:
            self.set_item_source(
                f"P{playernum}Text", f"{hits} hits\n{damage}%", color="0xFF000000"
            )
            self.set_item_source(
                f"P{playernum}Text Background",
                f"{hits} hit\n{damage}%",
                color="0x7DD1D1D1",
            )

        if not self.visibility[playernum - 1]:
            self.set_item_visible(
                scene_name=ObsHelper.SCENE_NAME, item_name=f"P{playernum}Text"
            )
            self.set_item_visible(
                scene_name=ObsHelper.SCENE_NAME,
                item_name=f"P{playernum}Text Background",
            )
            self.visibility[playernum - 1] = True

    def hide_text_overlay(self, playernum):
        if self.visibility[playernum - 1]:
            self.set_item_visible(
                scene_name=ObsHelper.SCENE_NAME,
                item_name=f"P{playernum}Text",
                visibility=False,
            )
            self.set_item_visible(
                scene_name=ObsHelper.SCENE_NAME,
                item_name=f"P{playernum}Text Background",
                visibility=False,
            )
            self.visibility[playernum - 1] = False

    def vs_win_probability(self, p1probability, p2probability):
        self.set_item_source("P1 VS Text", f"{p1probability}% WP")
        self.set_item_source("P2 VS Text", f"{p2probability}% WP")

    def vs_win_probability_visibility(self, visibility):
        if self.vs_win_probability_visibility_flag != visibility:
            try:
                self.set_item_visible(
                    scene_name=ObsHelper.SCENE_NAME,
                    item_name=f"P1 VS Text",
                    visibility=visibility,
                )

                self.set_item_visible(
                    scene_name=ObsHelper.SCENE_NAME,
                    item_name=f"P2 VS Text",
                    visibility=visibility,
                )

                self.set_item_visible(
                    scene_name=ObsHelper.SCENE_NAME,
                    item_name=f"P1 VS Text Background",
                    visibility=visibility,
                )

                self.set_item_visible(
                    scene_name=ObsHelper.SCENE_NAME,
                    item_name=f"P2 VS Text Background",
                    visibility=visibility,
                )

            except Exception as e:
                return

            self.vs_win_probability_visibility_flag = visibility

    def win_probability_visibility(self, visibility):
        if self.win_probability_visibility_flag != visibility:
            try:
                self.set_item_visible(
                    scene_name=ObsHelper.SCENE_NAME,
                    item_name=f"Win Probability",
                    visibility=visibility,
                )

                self.set_item_visible(
                    scene_name=ObsHelper.SCENE_NAME,
                    item_name=f"Match Win Probability",
                    visibility=visibility,
                )

                self.set_item_visible(
                    scene_name=ObsHelper.SCENE_NAME,
                    item_name=f"Match Win Text",
                    visibility=visibility,
                )
            except Exception as e:
                return
            self.win_probability_visibility_flag = visibility
