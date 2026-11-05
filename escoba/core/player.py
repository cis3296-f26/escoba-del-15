
class Player:
    def __init__(self, name, is_cpu=False):
        self.name = name
        self.hand = []
        self.captured = []
        self.escobas = 0
        self.score = 0
        self.is_cpu = is_cpu

    def add_card(self, card):
        if len(self.hand) >= 3:
            raise ValueError("Player hand is full")
        self.hand.append(card)

    def remove_card(self, card):
        self.hand.remove(card)

    def has_card(self, card):
        return card in self.hand

    def add_captured(self, cards):
        self.captured.extend(cards)
