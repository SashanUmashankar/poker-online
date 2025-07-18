from flask import Flask, render_template, request, jsonify
import random
import json
from enum import Enum
from typing import List, Dict, Tuple, Optional

app = Flask(__name__)

class Suit(Enum):
    HEARTS = "hearts"
    DIAMONDS = "diamonds"
    CLUBS = "clubs"
    SPADES = "spades"

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14  # Ace is high in poker

class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank.name} of {self.suit.value}"
    
    def to_dict(self):
        return {
            "suit": self.suit.value,
            "rank": self.rank.value,
            "display": str(self)
        }

class Deck:
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        self.cards = [Card(suit, rank) for suit in Suit for rank in Rank]
        random.shuffle(self.cards)
    
    def deal(self) -> Card:
        return self.cards.pop()

class HandRank(Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

class PokerHand:
    def __init__(self, cards: List[Card]):
        self.cards = cards
        self.rank, self.value = self.evaluate()
    
    def evaluate(self) -> Tuple[HandRank, List[int]]:
        # only numerical values and suits
        ranks = [card.rank.value for card in self.cards]
        suits = [card.suit for card in self.cards]
        rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}
        
        is_flush = len(set(suits)) == 1
        is_straight = self.is_straight(ranks)

        # checking for best hands first
        if is_straight and is_flush:
            if min(ranks) == 10:
                return HandRank.ROYAL_FLUSH, [14]
            return HandRank.STRAIGHT_FLUSH, [max(ranks)]
        
        counts = sorted(rank_counts.values(), reverse=True)
        
        if counts[0] == 4: # four of a kind
            four_kind = [rank for rank, count in rank_counts.items() if count == 4][0]
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            return HandRank.FOUR_OF_A_KIND, [four_kind, kicker]
        
        if counts[0] == 3 and counts[1] == 2: # full house
            three_kind = [rank for rank, count in rank_counts.items() if count == 3][0]
            pair = [rank for rank, count in rank_counts.items() if count == 2][0]
            return HandRank.FULL_HOUSE, [three_kind, pair]
        
        if is_flush:
            return HandRank.FLUSH, sorted(ranks, reverse=True)
        
        if is_straight:
            return HandRank.STRAIGHT, [max(ranks)]
        
        if counts[0] == 3: # three of a kind
            three_kind = [rank for rank, count in rank_counts.items() if count == 3][0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandRank.THREE_OF_A_KIND, [three_kind] + kickers
        
        if counts.count(2) == 2: # two pair
            pairs = sorted([rank for rank, count in rank_counts.items() if count == 2], reverse=True)
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            return HandRank.TWO_PAIR, pairs + [kicker]
        
        if counts[0] == 2: # pair
            pair = [rank for rank, count in rank_counts.items() if count == 2][0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandRank.PAIR, [pair] + kickers
        
        return HandRank.HIGH_CARD, sorted(ranks, reverse=True)
    
    def is_straight(self, ranks: List[int]) -> bool:
        sorted_ranks = sorted(set(ranks))
        if len(sorted_ranks) != 5:
            return False
        
        # Check for regular straight
        if sorted_ranks[-1] - sorted_ranks[0] == 4:
            return True
        
        # Check for A-2-3-4-5 straight
        if sorted_ranks == [2, 3, 4, 5, 14]:
            return True
        
        return False

class Player:
    def __init__(self, name: str, chips: int = 1000):
        self.name = name
        self.chips = chips
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False
    
    def to_dict(self):
        return {
            "name": self.name,
            "chips": self.chips,
            "hand": [card.to_dict() for card in self.hand],
            "current_bet": self.current_bet,
            "folded": self.folded,
            "all_in": self.all_in
        }

class PokerGame:
    def __init__(self):
        self.players = []
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.current_player = 0
        self.game_stage = "waiting"  # 6 stages: waiting, preflop, flop, turn, river, showdown
        self.small_blind = 10
        self.big_blind = 20
    
    def add_player(self, name: str):
        if len(self.players) < 6:
            self.players.append(Player(name))
            return True
        return False
    
    def start_game(self):
        if len(self.players) < 2:
            return False
        
        self.deck.reset()
        self.community_cards = []
        self.pot = 0
        self.current_bet = self.big_blind
        self.game_stage = "preflop"
        
        # Reset players
        for player in self.players:
            player.hand = []
            player.current_bet = 0
            player.folded = False
            player.all_in = False
        
        # Deal hole cards
        for _ in range(2):
            for player in self.players:
                player.hand.append(self.deck.deal())
        
        # Post blinds
        self.players[0].current_bet = self.small_blind
        self.players[0].chips -= self.small_blind
        self.players[1].current_bet = self.big_blind
        self.players[1].chips -= self.big_blind
        self.pot = self.small_blind + self.big_blind
        
        self.current_player = 2 if len(self.players) > 2 else 0
        return True
    
    def player_action(self, player_index: int, action: str, amount: int = 0):
        if player_index != self.current_player or self.players[player_index].folded:
            return False
        
        player = self.players[player_index]
        
        if action == "fold":
            player.folded = True
        elif action == "call":
            call_amount = min(self.current_bet - player.current_bet, player.chips)
            player.chips -= call_amount
            player.current_bet += call_amount
            self.pot += call_amount
            if player.chips == 0:
                player.all_in = True
        elif action == "raise":
            raise_amount = min(amount, player.chips)
            self.current_bet = player.current_bet + raise_amount
            player.chips -= raise_amount
            player.current_bet += raise_amount
            self.pot += raise_amount
            if player.chips == 0:
                player.all_in = True
        
        self.next_player()
        return True
    
    def next_player(self):
        active_players = [i for i, p in enumerate(self.players) if not p.folded]
        
        if len(active_players) == 1:
            self.game_stage = "showdown"
            return
        
        # Check if betting round is complete
        if self.is_betting_round_complete():
            self.advance_stage()
        else:
            self.current_player = (self.current_player + 1) % len(self.players)
            while self.players[self.current_player].folded:
                self.current_player = (self.current_player + 1) % len(self.players)
    
    def is_betting_round_complete(self):
        active_players = [p for p in self.players if not p.folded]
        return all(p.current_bet == self.current_bet or p.all_in for p in active_players)
    
    def advance_stage(self):
        # Reset betting for next round
        for player in self.players:
            player.current_bet = 0
        self.current_bet = 0
        self.current_player = 0
        while self.players[self.current_player].folded:
            self.current_player = (self.current_player + 1) % len(self.players)
        
        if self.game_stage == "preflop":
            self.game_stage = "flop"
            for _ in range(3):
                self.community_cards.append(self.deck.deal())
        elif self.game_stage == "flop":
            self.game_stage = "turn"
            self.community_cards.append(self.deck.deal())
        elif self.game_stage == "turn":
            self.game_stage = "river"
            self.community_cards.append(self.deck.deal())
        elif self.game_stage == "river":
            self.game_stage = "showdown"
    
    def get_best_hand(self, player: Player) -> PokerHand:
        all_cards = player.hand + self.community_cards
        best_hand = None
        
        # Try all combinations of 5 cards
        from itertools import combinations
        for combo in combinations(all_cards, 5):
            hand = PokerHand(list(combo))
            if best_hand is None or self.compare_hands(hand, best_hand) > 0:
                best_hand = hand
        
        return best_hand
    
    def compare_hands(self, hand1: PokerHand, hand2: PokerHand) -> int:
        if hand1.rank.value > hand2.rank.value:
            return 1
        elif hand1.rank.value < hand2.rank.value:
            return -1
        else:
            for v1, v2 in zip(hand1.value, hand2.value):
                if v1 > v2:
                    return 1
                elif v1 < v2:
                    return -1
            return 0
    
    def determine_winner(self):
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) == 1:
            return active_players[0]
        
        best_player = None
        best_hand = None
        
        for player in active_players:
            hand = self.get_best_hand(player)
            if best_hand is None or self.compare_hands(hand, best_hand) > 0:
                best_hand = hand
                best_player = player
        
        return best_player
    
    def to_dict(self):
        return {
            "players": [p.to_dict() for p in self.players],
            "community_cards": [card.to_dict() for card in self.community_cards],
            "pot": self.pot,
            "current_bet": self.current_bet,
            "current_player": self.current_player,
            "game_stage": self.game_stage,
            "small_blind": self.small_blind,
            "big_blind": self.big_blind
        }

# Global game instance
game = PokerGame()

@app.route('/')
def index():
    return render_template('interface.html')

@app.route('/api/join', methods=['POST'])
def join_game():
    data = request.json
    name = data.get('name')
    
    if game.add_player(name):
        return jsonify({"success": True, "message": f"{name} joined the game"})
    else:
        return jsonify({"success": False, "message": "Game is full"})

@app.route('/api/start', methods=['POST'])
def start_game():
    if game.start_game():
        return jsonify({"success": True, "message": "Game started"})
    else:
        return jsonify({"success": False, "message": "Need at least 2 players"})

@app.route('/api/action', methods=['POST'])
def player_action():
    data = request.json
    player_index = data.get('player_index')
    action = data.get('action')
    amount = data.get('amount', 0)
    
    if game.player_action(player_index, action, amount):
        if game.game_stage == "showdown":
            winner = game.determine_winner()
            winner.chips += game.pot
            game.pot = 0
        
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid action"})

@app.route('/api/game_state')
def get_game_state():
    return jsonify(game.to_dict())

@app.route('/api/reset', methods=['POST'])
def reset_game():
    global game
    game = PokerGame()
    return jsonify({"success": True, "message": "Game reset"})

if __name__ == '__main__':
    app.run(debug=True)
