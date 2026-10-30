class GameState:
    def __init__(self, players, deck, table, turn=0):
        self.players = players
        self.deck = deck
        self.table = table
        self.turn = turn
        

    def next_turn(self):
        self.turn = (self.turn + 1) % len(self.players)
