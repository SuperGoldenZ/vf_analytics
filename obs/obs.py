import obsws_python as obs


class ObsHelper:
    SECRET = "aYohxiPj0IIS58Nt"

    def __init__(self):
        self.cl = obs.ReqClient(
            host="localhost", port=4455, password=self.SECRET, timeout=3
        )

    def set_item_visible(
        self, visibility=True, scene_name="vf no text", item_name="P1Text"
    ):
        scene_items = self.cl.get_scene_item_list("vf no text").scene_items
        item_id = None
        for item in scene_items:
            if item["sourceName"] == item_name:
                item_id = item["sceneItemId"]

        self.cl.set_scene_item_enabled(
            scene_name=scene_name, item_id=item_id, enabled=visibility
        )
        return None

    def set_item_source(self, item_name="P1Text", text="Default", color = "0x000000FF"):
        input_settings = self.cl.get_input_settings(item_name).input_settings        
        input_settings["text"] = text
        input_settings["color"] = int(color,16)
        input_settings["color1"] = int(color,16)
        input_settings["color2"] = int(color,16)
        
        self.cl.set_input_settings(
            name=item_name, settings=input_settings, overlay=True
        )
        return None

    def start_recording(self):
        self.cl.start_record()

    def stop_recording(self):
        stop_result = self.cl.stop_record()
        return stop_result.output_path

    def first_strike(self, playernum):
        self.set_item_source(f"P{playernum}Text", "First\nStrike!", color="0xFF000000")
        self.set_item_source(f"P{playernum}Text Background", color="0x7DD1D1D1")
        self.set_item_visible(scene_name="vf no text", item_name=f"P{playernum}Text")
        self.set_item_visible(
            scene_name="vf no text", item_name=f"P{playernum}Text Background"
        )

    def catbas(self, playernum):
        self.set_item_source(f"P{playernum}Text", "CAT\nBAS", color="0xFF0000FF")
        self.set_item_visible(scene_name="vf no text", item_name=f"P{playernum}Text")
        self.set_item_visible(
            scene_name="vf no text", item_name=f"P{playernum}Text Background"
        )        

    def combo(self, playernum, hits, damage):
        if (hits == 1):
            self.set_item_source(f"P{playernum}Text", f"{hits} hit\n{damage}%", color="0xFFFFFFFF")
            self.set_item_source(f"P{playernum}Text Background", f"{hits} hit\n{damage}%", color="0xFF0000FF")
        else:
            self.set_item_source(f"P{playernum}Text", f"{hits} hits\n{damage}%", color="0xFF000000")  
            self.set_item_source(f"P{playernum}Text Background", f"{hits} hit\n{damage}%", color="0x7DD1D1D1")

        self.set_item_visible(scene_name="vf no text", item_name=f"P{playernum}Text")
        self.set_item_visible(
            scene_name="vf no text", item_name=f"P{playernum}Text Background"
        )

    def hide_text_overlay(self, playernum):
        self.set_item_visible(
            scene_name="vf no text", item_name=f"P{playernum}Text", visibility=False
        )
        self.set_item_visible(
            scene_name="vf no text",
            item_name=f"P{playernum}Text Background",
            visibility=False,
        )

    def win_probability_visibility(self, visibility):
        try:
            self.set_item_visible(
                scene_name="vf no text",
                item_name=f"Win Probability",
                visibility=visibility,
            )
        except:
            return
