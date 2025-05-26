import pygame

class HUD:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Load fonts
        self.font_large = pygame.font.SysFont(None, 48)
        self.font_medium = pygame.font.SysFont(None, 32)
        self.font_small = pygame.font.SysFont(None, 24)
        
        # HUD elements
        self.health = 3
        self.score = 0
        self.wave = 1
        self.active_powerups = {}
        self.enemies_remaining = 0
        
        # Power-up icons
        self.powerup_icons = {
            "shield": "S",
            "rapid_fire": "R",
            "slow_motion": "T",
            "size_shrink": "Z"
        }
        
        # Power-up colors
        self.powerup_colors = {
            "shield": (100, 150, 255),
            "rapid_fire": (255, 100, 100),
            "slow_motion": (100, 255, 100),
            "size_shrink": (255, 255, 100)
        }
    
    def update(self, health, score, wave, active_powerups, enemies_remaining=0):
        self.health = health
        self.score = score
        self.wave = wave
        self.active_powerups = active_powerups
        self.enemies_remaining = enemies_remaining
    
    def draw(self, screen):
        # Draw health
        self.draw_health(screen)
        
        # Draw score
        self.draw_score(screen)
        
        # Draw wave
        self.draw_wave(screen)
        
        # Draw enemies remaining
        self.draw_enemies_remaining(screen)
        
        # Draw active power-ups
        self.draw_powerups(screen)
    
    def draw_health(self, screen):
        # Draw health as hearts
        heart_width = 30
        heart_spacing = 10
        start_x = 20
        start_y = 20
        
        for i in range(3):
            color = (255, 50, 50) if i < self.health else (100, 100, 100)
            
            # Draw a heart shape
            heart_x = start_x + (heart_width + heart_spacing) * i
            
            # Simple heart using two circles and a triangle
            pygame.draw.circle(screen, color, (heart_x + 7, start_y + 7), 7)
            pygame.draw.circle(screen, color, (heart_x + 23, start_y + 7), 7)
            
            points = [
                (heart_x, start_y + 7),
                (heart_x + 15, start_y + 25),
                (heart_x + 30, start_y + 7)
            ]
            pygame.draw.polygon(screen, color, points)
    
    def draw_score(self, screen):
        # Draw score in the top right
        score_text = self.font_medium.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (self.width - score_text.get_width() - 20, 20))
    
    def draw_wave(self, screen):
        # Draw wave in the top center
        wave_text = self.font_medium.render(f"Wave {self.wave}", True, (255, 255, 255))
        screen.blit(wave_text, (self.width // 2 - wave_text.get_width() // 2, 20))
    
    def draw_enemies_remaining(self, screen):
        # Draw enemies remaining count below the wave number
        enemies_text = self.font_small.render(f"Enemies Remaining: {self.enemies_remaining}", True, (255, 200, 100))
        screen.blit(enemies_text, (self.width // 2 - enemies_text.get_width() // 2, 50))
    
    def draw_powerups(self, screen):
        # Draw active power-ups in the bottom left
        powerup_size = 30
        powerup_spacing = 10
        start_x = 20
        start_y = self.height - 50
        
        # Draw each active power-up
        i = 0
        for powerup, time_left in self.active_powerups.items():
            if time_left > 0:
                color = self.powerup_colors.get(powerup, (200, 200, 200))
                icon = self.powerup_icons.get(powerup, "?")
                
                # Draw power-up icon
                powerup_x = start_x + (powerup_size + powerup_spacing) * i
                
                # Draw circle background
                pygame.draw.circle(screen, color, (powerup_x + powerup_size // 2, start_y + powerup_size // 2), 
                                  powerup_size // 2)
                
                # Draw icon
                icon_text = self.font_small.render(icon, True, (255, 255, 255))
                screen.blit(icon_text, (powerup_x + powerup_size // 2 - icon_text.get_width() // 2, 
                                       start_y + powerup_size // 2 - icon_text.get_height() // 2))
                
                # Draw time left
                time_text = self.font_small.render(f"{time_left:.1f}s", True, (255, 255, 255))
                screen.blit(time_text, (powerup_x + powerup_size // 2 - time_text.get_width() // 2, 
                                       start_y + powerup_size + 5))
                
                i += 1
