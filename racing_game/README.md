# 2D Racing Game

A simple 2D racing game built with Pygame.

## Features

- Player-controlled car with realistic physics
- Multiple AI opponents
- Collision detection
- Lap counting and timing
- Various track designs
- Car sprites and sound effects
- Menu system
- Score and time tracking

## Installation

1. Make sure you have Python installed (Python 3.6 or higher recommended)
2. Install Pygame:
   ```
   pip install pygame
   ```
3. Optional: To create custom sound effects, install NumPy and SciPy:
   ```
   pip install numpy scipy
   ```

## How to Play

1. Run the game:
   ```
   python main.py
   ```
2. Use the arrow keys to control your car:
   - UP: Accelerate
   - DOWN: Brake/Reverse
   - LEFT/RIGHT: Steer

## Creating Assets

The game includes a script to generate basic assets:

```
python create_assets.py
```

This will create:
- Car sprites with different colors
- Basic sound effects

## Game Structure

- `main.py`: Entry point for the game
- `game.py`: Contains the main game classes (Car, Track, Game)
- `create_assets.py`: Script to generate game assets
- `assets/`: Directory containing images and sounds

## Customization

You can customize the game by:
- Adding your own car sprites in `assets/images/`
- Adding your own sound effects in `assets/sounds/`
- Modifying track generation in the `Track` class
- Adjusting car physics in the `Car` class

## License

This project is open source and available for anyone to use and modify.

## Credits

Created with the help of Amazon Q.
