"""
vf_cv: A library for extracing information from 
"""

__title__ = "vf_cv"
__author__ = "Alexander Golden"
__license__ = "MIT"
__js__ = None
__js_url__ = None

from vf_cv.timer import Timer
from vf_cv.cv_helper import CvHelper
from vf_cv.winning_round import WinningRound
from vf_cv.player_rank import PlayerRank
from vf_cv.player_rank import UnrecognizePlayerRankException
from vf_cv.character import Character
from vf_cv.winning_frame import WinningFrame
from vf_cv.match_analyzer import MatchAnalyzer
from vf_cv.match_analyzer import PrematureMatchFinishException
from vf_cv.stage import Stage

from vf_cv.version import __version__
