"""Tests for changing match data to a UUID"""
import vf_data.match
import vf_data.round

def test_get_id():
    match = vf_data.match.Match()
    
    match.date = "2024/11/01"
    assert("a7690ef1011c3d91fd6aad26cf6f618e" == match.make_id())
    

    match.date = "2024/11/02"    
    assert("3e5443a59fd1d9e7890426145a515cbd" == match.make_id())

    match.player1character = "Shun"
    match.player2character = "Akira"
    match.date = "12/12/2024"

    assert("e4c9e09b27e9ed234e0f678ab1a5da03" == match.make_id())


    match.player1character = "Shun"
    match.player2character = "Akira"
    match.player1ringname = "[Gx2] Namflow"
    match.player2ringname = "[Gx2] SuperGolden"
    match.date = "12/12/2024"
    match.player1rank = 10
    match.player2rank = 20
    assert("9d44c2d1d5b659ab3a1026c351e568b7" == match.make_id())


    round = vf_data.round.Round()
    round.remaining_time = 8
    round.victory = round.EX
    round.winning_player_num = 1

    match.add_finished_round(round)

    round = vf_data.round.Round()
    round.remaining_time = 8
    round.victory = round.KO
    round.winning_player_num = 1

    match.add_finished_round(round)

    round = vf_data.round.Round()
    round.remaining_time = 8
    round.victory = round.RO
    round.winning_player_num = 2

    match.add_finished_round(round)
    
    assert("f963d04b670a7e56f005c62c6e2c4aae" == match.make_id())