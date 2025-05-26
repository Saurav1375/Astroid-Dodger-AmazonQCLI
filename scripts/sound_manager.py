import pygame
import os
import math

class SoundManager:
    def __init__(self):
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Sound effects dictionary
        self.sounds = {}
        
        # Load sound effects
        self.load_sounds()
        
        # Set volume
        self.volume = 0.7
        self.update_volume()
    
    def load_sounds(self):
        """Load all sound effects"""
        # Define sound file paths
        sound_files = {
            "laser": "assets/sounds/laser.wav",
            "explosion": "assets/sounds/explosion.wav",
            "player_hit": "assets/sounds/player_hit.wav",
            "powerup": "assets/sounds/powerup.wav",
            "wave": "assets/sounds/wave.wav",
            "game_over": "assets/sounds/game_over.wav",
            "menu_select": "assets/sounds/menu_select.wav"
        }
        
        # Create placeholder sounds if files don't exist
        for name, path in sound_files.items():
            try:
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                else:
                    # Create a placeholder sound (a short beep)
                    self.sounds[name] = self.create_placeholder_sound(name)
            except Exception as e:
                print(f"Error loading sound {name}: {e}")
                # Create a very simple sound as fallback
                self.sounds[name] = pygame.mixer.Sound(buffer=bytearray(1000))
    
    def create_placeholder_sound(self, name):
        """Create a placeholder sound with different tones based on the name"""
        # Create a short sound buffer
        sample_rate = 22050
        buffer_size = 4410  # 0.2 seconds at 22050Hz
        
        # Different frequencies for different sound types
        frequencies = {
            "laser": 440,      # A4 note
            "explosion": 100,   # Low rumble
            "player_hit": 220,  # A3 note
            "powerup": 880,     # A5 note
            "wave": 660,        # E5 note
            "game_over": 165,   # E3 note
            "menu_select": 330  # E4 note
        }
        
        frequency = frequencies.get(name, 440)
        
        # Create a simple sine wave
        buffer = bytearray(buffer_size)
        for i in range(buffer_size):
            # Simple fade out
            amplitude = 127 * (1 - i / buffer_size)
            buffer[i] = 128 + int(amplitude * math.sin(2 * 3.14159 * frequency * i / sample_rate))
        
        # Create a sound object from the buffer
        sound = pygame.mixer.Sound(buffer=buffer)
        
        return sound
    
    def play_sound(self, name):
        """Play a sound effect by name"""
        if name in self.sounds:
            self.sounds[name].play()
    
    def set_volume(self, volume):
        """Set the volume for all sounds (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        self.update_volume()
    
    def update_volume(self):
        """Update the volume of all sounds"""
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
