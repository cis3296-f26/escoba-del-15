WINNING_SCORE = 21


class GameState:
    def __init__(self, players, deck, table, turn=0):
        self.players = players
        self.deck = deck
        self.table = table
        self.turn = turn
        # running game total for every player
        self.scores = {player: 0 for player in players}
        

    def next_turn(self):
        self.turn = (self.turn + 1) % len(self.players)

    def add_round_scores(self, round_scores):
        # round_scores maps each player to the points they counted this round
        for player, points in round_scores.items():
            self.scores[player] += points

    def winner(self):
        # highest total at or above the threshold wins; None means start a new round
        best = max(self.scores.values())
        leaders = [player for player, score in self.scores.items() if score == best]

        if best < WINNING_SCORE or len(leaders) > 1:
            return None

        return leaders[0]

    def is_game_over(self):
        return self.winner() is not None
