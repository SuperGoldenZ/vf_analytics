import configparser


class Config:
    def __init__(self):
        self.images_output_folder = None
        self.save_all_images = False
        self.dont_save_any_images = False
        self.save_video_snippets = False
        self.cam_int = -1

    @staticmethod
    def load_config(file_path):
        config: Config = Config()

        config_parser = configparser.ConfigParser()

        # Read the .cfg file
        config_parser.read(file_path)

        config.images_output_folder = config_parser.get(
            "Settings", "images_output_folder"
        )
        config.save_all_images = config_parser.getboolean("Settings", "save_all_images")
        config.dont_save_any_images = config_parser.getboolean(
            "Settings", "dont_save_any_images"
        )

        config.save_video_snippets = config_parser.getboolean(
            "Settings", "save_video_snippets"
        )

        config.cam_int = config_parser.getint("Settings", "cam_int")

        return config
