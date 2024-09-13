class Round:
    KO = 1
    RO = 2
    EX = 3

    VICTORIES = {
        KO: "KO",
        RO: "RO",
        EX: "EX"
    }
    def __init__(self):
        self.winning_player_num = 0
        self.remaining_time = 0
        self.victory = 0
        self.num = 0
        self.seconds = 0

    def get_victory(self):
        return self.VICTORIES[self.victory]
    
    def get_youtube_url(self, video_id):
        return f"https://www.youtube.com/watch?v={video_id}&t={self.seconds}"