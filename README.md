# Asteroid Dodger

A pygame-based asteroid dodging game with multiple features including smooth movement, power-ups, weapon systems, and progressive difficulty.

## Features

- Spaceship controlled by arrow keys with smooth movement and rotation
- Multiple asteroid types (small fast, medium normal, large slow, boss)
- Collision detection with health system (3 lives)
- Scoring system with combo multipliers for consecutive dodges
- Power-ups including shield, rapid fire lasers, slow motion, and size shrink
- Weapon system to shoot and destroy asteroids for bonus points
- Particle effects for explosions and engine thrust
- Scrolling starfield background
- Progressive difficulty with waves and boss asteroids
- Sound effects for shooting/explosions/powerups
- Main menu with high score tracking
- Pause functionality
- Game over/restart screens
- HUD showing health, score, active powerups, and current wave

## Controls

- **Arrow Keys**: Control the spaceship (up to accelerate, down to brake, left/right to rotate)
- **Space**: Fire weapon
- **Escape**: Pause game

## Installation

1. Ensure you have Python and Pygame installed:
   ```
   pip install pygame
   ```

2. Run the game:
   ```
   python main.py
   ```

## Folder Structure

```
asteroid_dodger/
├── assets/
│   ├── images/
│   ├── sounds/
│   └── fonts/
├── scripts/
│   ├── __init__.py
│   ├── game.py
│   ├── player.py
│   ├── asteroid.py
│   ├── powerup.py
│   ├── weapon.py
│   ├── particle.py
│   ├── starfield.py
│   ├── hud.py
│   ├── menu.py
│   └── sound_manager.py
└── main.py
```

## Adding Custom Assets

You can add your own assets to enhance the game:

1. **Sound Effects**: Place .wav files in the `assets/sounds/` directory with the following names:
   - laser.wav
   - explosion.wav
   - player_hit.wav
   - powerup.wav
   - wave.wav
   - game_over.wav
   - menu_select.wav

2. **Images**: Place image files in the `assets/images/` directory.

3. **Fonts**: Place font files in the `assets/fonts/` directory.

## Extending the Game

The modular structure makes it easy to extend the game with new features:

- Add new power-up types in the `powerup.py` file
- Create new asteroid types in the `asteroid.py` file
- Implement new weapon systems in the `weapon.py` file
