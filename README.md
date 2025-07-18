# Texas Hold'em Poker Game

full-stack Texas Hold'em poker game built with Python Flask backend and HTML/CSS/JavaScript frontend.

## Features

  - All standard poker hands (Royal Flush to High Card)
  - Betting rounds: Preflop, Flop, Turn, River
  - Automatic hand evaluation and winner determination

- **Multi-player**
  - Up to 6 players per game
  - Real-time game state updates

## Quick Start

### Prerequisites
- Python 3.7+ installed
- Web browser

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/poker-game.git
   cd poker-game
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv poker_env
   
   # Activate virtual environment
   # Windows:
   poker_env\Scripts\activate
   # Mac/Linux:
   source poker_env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   gambling.py
   ```

5. **Open your browser and go to:**
   ```
   http://localhost:5000
   ```

## How to Play

1. **Join Game:** Enter your name and click "Join Game"
2. **Start Game:** Once 2+ players have joined, click "Start Game"  
3. **Take Actions:** When it's your turn (highlighted in yellow):
   - **Fold:** Give up your hand
   - **Call:** Match the current bet
   - **Raise:** Increase the bet (enter amount)

### Game Flow
- **Preflop:** Each player gets 2 hole cards
- **Flop:** 3 community cards revealed
- **Turn:** 4th community card revealed  
- **River:** 5th community card revealed
- **Showdown:** Best 5-card hand wins the pot

## Multiplayer Setup

### Local Network Play
To play with friends on the same network:

1. **Modify `gambling.py`:**
   ```python
   if __name__ == '__main__':
       app.run(debug=True, host='0.0.0.0', port=5000)
   ```

2. **Find your IP address:**
   ```bash
   # Windows:
   ipconfig
   # Mac/Linux:
   ifconfig
   ```

3. **Share with friends:**
   ```
   http://YOUR_IP_ADDRESS:5000
   ```

## Technical Details

### Backend (Python Flask)
- **Card Management:** Deck shuffling, dealing, hand evaluation
- **Game Logic:** Betting rounds, pot management, winner determination
- **API Endpoints:** RESTful API for all game actions
- **Hand Rankings:** Complete poker hand evaluation system

### Frontend (HTML/CSS/JavaScript)
- **Real-time Updates:** Auto-refresh every 2 seconds
- **Responsive Design:** Works on desktop and mobile
- **Interactive UI:** Visual feedback for all game states

### Project Structure
```
poker-game/
├── app.py              # Flask backend with game logic
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Frontend interface
└── README.md          # This file
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/join` | POST | Join game with player name |
| `/api/start` | POST | Start the game |
| `/api/action` | POST | Make player action (fold/call/raise) |
| `/api/game_state` | GET | Get current game state |
| `/api/reset` | POST | Reset the game |

## Game Rules

- **Starting Chips:** $1000 per player
- **Blinds:** Small blind $10, Big blind $20
- **Minimum Players:** 2
- **Maximum Players:** 6
- **Betting:** No limit Texas Hold'em style

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Soon soon

- [ ] Player statistics tracking
- [ ] Chat system

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Flask web framework
- Inspired by classic Texas Hold'em poker

