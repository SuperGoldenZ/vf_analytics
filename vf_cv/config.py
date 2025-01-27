import configparser


class Config:
    def __init__(self):
        self.images_output_folder = None
        self.save_all_images = False
        self.dont_save_any_images = False
        self.save_video_snippets = False
        self.auto_record = False
        self.cam_int = -1
        self.process_streamed_videos = True
        self.video_download_folder = None
        self.save_image_format = None
        self.save_win_probability_image = False

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

        config.auto_record = config_parser.getboolean("OBS", "auto_record")

        config.process_streamed_videos = config_parser.getboolean(
            "YouTube", "process_streamed_videos"
        )

        config.video_download_folder = config_parser.get(
            "YouTube", "video_download_folder"
        )

        config.save_image_format = config_parser.get("Settings", "save_image_format")

        config.save_win_probability_image = config_parser.get(
            "Settings", "save_win_probability_image"
        )
        return config
