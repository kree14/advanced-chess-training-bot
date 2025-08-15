# Advanced Chess Training Bot

A comprehensive Chess Training Bot built with Python and PyQt5, featuring advanced Stockfish engine integration, puzzle training, opening repertoire building, and sophisticated analysis tools for serious chess improvement.

## 🚀 Features

### Core Training Features
- **Adjustable Bot Strength**: Set ELO rating from 800 to 2500 with realistic play patterns
- **Smart Move Suggestions**: Multi-PV analysis with move explanations and alternatives
- **Natural Play**: Bot makes human-like mistakes based on ELO level to avoid detection
- **Advanced Analysis**: Comprehensive position evaluation with tactical and strategic insights
- **Game Phase Detection**: Automatic detection of opening, middlegame, and endgame phases

### Advanced Training Modules
- **Puzzle Trainer**: Tactical puzzle solving with theme-based training and progress tracking
- **Opening Trainer**: Learn and practice opening repertoires with move explanations
- **Position Analysis**: Deep positional evaluation including king safety, pawn structure, and material balance
- **Training Statistics**: Detailed performance tracking and improvement metrics

### User Interface & Experience
- **Modern GUI**: Clean, dark-themed interface with tabbed layout
- **Multi-threaded Analysis**: Background analysis keeps the interface responsive
- **Personality Configuration**: Customize bot playing style (aggressive, positional, tactical)
- **Progress Tracking**: Save and load training progress across sessions
- **Hint System**: Context-aware hints and training suggestions

### Technical Features
- **Opening Book Integration**: Support for polyglot opening books
- **Background Analysis**: Non-blocking engine analysis with progress indicators
- **Settings Persistence**: Save preferences and training data
- **Error Handling**: Robust error handling with user-friendly messages
- **Resource Management**: Proper cleanup of engine resources

## 📋 Requirements

- **Python 3.7 or higher**
- **PyQt5** - GUI framework
- **python-chess** - Chess logic and engine communication
- **Stockfish chess engine** - Analysis engine

## 🔧 Installation

### 1. Install Python Dependencies

```bash
pip install PyQt5 python-chess
```

### 2. Install Stockfish Engine

**Option A: Download from Official Website (Recommended)**
1. Visit [Stockfish Official Website](https://stockfishchess.org/download/)
2. Download the appropriate version for your operating system
3. Extract the executable to a folder in your PATH, or note the full path

**Option B: Package Manager Installation**

**Windows (using Chocolatey):**
```bash
choco install stockfish
```

**macOS (using Homebrew):**
```bash
brew install stockfish
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install stockfish
```

### 3. Configure Stockfish Path (if needed)

If Stockfish is not in your system PATH, edit the `STOCKFISH_PATH` variable in `chess_engine.py`:

```python
STOCKFISH_PATH = "/path/to/your/stockfish/executable"
```

### 4. Optional: Download Opening Books

For enhanced opening training, download polyglot opening books:
- Create a `books/` directory in the project folder
- Download `.bin` files from chess programming sites
- Popular books: `performance.bin`, `human.bin`, `computer.bin`

## 🎮 Usage

### Basic Version
```bash
python main.py
```

### Advanced Version (Recommended)
```bash
python main_advanced.py
```

### Command Line Options
```bash
python main_advanced.py --basic      # Launch basic version
python main_advanced.py --advanced   # Launch advanced version (default)
python main_advanced.py --version    # Show version information
```

## 🎯 Training Modes

### 1. **Position Analysis Training**
- Set desired ELO level (800-2500)
- Get move suggestions with detailed explanations
- View comprehensive position evaluations
- Practice with different bot personalities

### 2. **Puzzle Training**
- Solve tactical puzzles by theme (forks, pins, mates, etc.)
- Adaptive difficulty based on performance
- Track solving statistics and rating progression
- Get hints when stuck

### 3. **Opening Training**
- Learn popular openings with move-by-move explanations
- Practice opening lines with immediate feedback
- Build personal opening repertoire
- Study typical plans and pawn structures

### 4. **Analysis Mode**
- Deep position analysis with multiple candidate moves
- Tactical motif detection (pins, forks, skewers)
- Strategic evaluation (king safety, pawn structure)
- Move accuracy classification (excellent, good, inaccuracy, mistake, blunder)

## 🧠 How the Advanced Engine Works

### ELO-Based Move Selection
The bot uses sophisticated algorithms to simulate realistic play at different skill levels:

- **2200-2500 ELO**: 85% best moves, occasional strategic inaccuracies
- **1800-2200 ELO**: 70% best moves, more tactical oversights
- **1400-1800 ELO**: 55% best moves, positional mistakes
- **1000-1400 ELO**: 40% best moves, frequent tactical errors
- **800-1000 ELO**: 25% best moves, beginner-level mistakes

### Personality System
Configure bot behavior with personality traits:
- **Aggression**: Passive to highly aggressive play
- **Positional Play**: Tactical focus vs. positional understanding
- **Tactical Awareness**: Ability to spot tactical motifs
- **Endgame Skill**: Endgame technique level
- **Opening Knowledge**: Depth of opening preparation

### Multi-PV Analysis
- Analyzes multiple candidate moves simultaneously
- Provides move rankings with evaluations
- Shows principal variations for top moves
- Calculates move accuracy percentages

## 📁 Project Structure

```
advanced-chess-training-bot/
├── main.py                    # Basic version entry point
├── main_advanced.py           # Advanced version entry point
├── chess_engine.py            # Advanced Stockfish integration
├── chess_gui.py              # Basic GUI implementation
├── chess_gui_advanced.py     # Advanced GUI with tabs and features
├── puzzle_trainer.py         # Tactical puzzle training system
├── opening_trainer.py        # Opening repertoire trainer
├── requirements.txt          # Python dependencies
├── plan.md                   # Development plan
├── TODO.md                   # Implementation tracker
└── README.md                 # This file

Optional directories:
├── books/                    # Opening book files (.bin)
├── puzzles/                  # Additional puzzle databases
└── games/                    # Saved games and analysis
```

## 🎨 Interface Overview

### Main Window Tabs
1. **Training**: Core training controls and ELO settings
2. **Analysis**: Detailed move analysis and position evaluation
3. **Statistics**: Performance tracking and improvement metrics
4. **Settings**: Bot personality, engine configuration, preferences

### Key Features
- **Interactive Chess Board**: Click-to-move interface with coordinate display
- **Real-time Analysis**: Background engine analysis with progress bars
- **Move Highlighting**: Visual feedback for suggested moves and last moves
- **Game Phase Display**: Shows current phase (opening/middlegame/endgame)
- **Training Hints**: Context-aware suggestions for improvement

## 📊 Training Statistics

The bot tracks comprehensive statistics:
- **Overall Performance**: Accuracy, games played, moves analyzed
- **By Opening**: Success rates for different openings
- **By Puzzle Theme**: Tactical pattern recognition progress
- **ELO Progression**: Rating changes over time
- **Mistake Analysis**: Classification of errors for targeted improvement

## 🔧 Troubleshooting

### Common Issues

**"Stockfish not found" error:**
- Ensure Stockfish is installed and accessible
- Check the `STOCKFISH_PATH` in `chess_engine.py`
- Try using the full path to the Stockfish executable
- Test Stockfish installation: `stockfish` in terminal/command prompt

**GUI not displaying properly:**
- Ensure PyQt5 is properly installed: `pip install --upgrade PyQt5`
- Check Python version compatibility (3.7+)
- Try running with `python -m PyQt5.QtWidgets` to test PyQt5

**Analysis running slowly:**
- Reduce analysis time in settings (default: 3 seconds)
- Lower engine hash size if memory is limited
- Reduce number of threads in engine settings

**Import errors:**
- Install all dependencies: `pip install -r requirements.txt`
- Check Python path and virtual environment
- Ensure all project files are in the same directory

**Opening book not loading:**
- Check that book files are in the correct directory
- Ensure book files are valid polyglot format (.bin)
- Books are optional - the engine will work without them

### Performance Optimization

**For better performance:**
- Increase engine hash size (Settings tab)
- Use more CPU threads for analysis
- Close other resource-intensive applications
- Use SSD storage for faster file access

**For lower resource usage:**
- Decrease analysis time
- Reduce engine hash size
- Use fewer threads
- Disable auto-analysis features

## 🤝 Contributing

This is an open-source project. Contributions are welcome:
- Report bugs and suggest features
- Improve documentation
- Add new puzzle themes or openings
- Enhance the analysis algorithms
- Create additional training modules

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Stockfish Team** - For the powerful chess engine
- **python-chess developers** - For the excellent chess library
- **PyQt5 Team** - For the GUI framework
- **Chess community** - For opening theory and puzzle databases

---

**Happy Training! 🏆**

*Improve your chess with advanced AI-powered training tools designed for serious players.*
