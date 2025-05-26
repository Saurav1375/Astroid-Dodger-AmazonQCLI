import pygame
import math

class PowerUp:
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.radius = 15
        self.velocity_x = 0
        self.velocity_y = 0
        self.lifetime = 10.0  # Power-ups disappear after 10 seconds
        
        # Set color and symbol based on type
        if powerup_type == "shield":
            self.color = (100, 150, 255)  # Light blue
            self.symbol = "S"
        elif powerup_type == "rapid_fire":
            self.color = (255, 100, 100)  # Red
            self.symbol = "R"
        elif powerup_type == "slow_motion":
            self.color = (100, 255, 100)  # Green
            self.symbol = "T"  # T for time
        elif powerup_type == "size_shrink":
            self.color = (255, 255, 100)  # Yellow
            self.symbol = "Z"  # Z for zoom/shrink
        else:
            self.color = (200, 200, 200)  # Gray
            self.symbol = "?"
        
        # Animation variables
        self.pulse = 0
        self.pulse_direction = 1
    
    def update(self, dt):
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Update lifetime
        self.lifetime -= dt
        
        # Update pulse animation
        self.pulse += 0.05 * self.pulse_direction
        if self.pulse >= 1.0:
            self.pulse = 1.0
            self.pulse_direction = -1
        elif self.pulse <= 0.0:
            self.pulse = 0.0
            self.pulse_direction = 1
    
    def is_offscreen(self, screen_width, screen_height):
        """Check if the power-up is completely off the screen"""
        return (self.x + self.radius < 0 or 
                self.x - self.radius > screen_width or 
                self.y + self.radius < 0 or 
                self.y - self.radius > screen_height or
                self.lifetime <= 0)
    
    def draw(self, screen):
        # Draw the power-up circle
        pulse_radius = self.radius * (1 + self.pulse * 0.2)
        
        # Draw outer glow
        for i in range(3):
            alpha = 100 - i * 30
            glow_radius = pulse_radius + i * 2
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color, alpha), 
                              (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (self.x - glow_radius, self.y - glow_radius))
        
        # Draw main circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(pulse_radius))
        
        # Draw white border
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), int(pulse_radius), 2)
        
        # Draw symbol
        font = pygame.font.SysFont(None, 24)
        text = font.render(self.symbol, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)
        
        # Draw lifetime indicator if less than 3 seconds
        if self.lifetime < 3.0:
            # Flashing effect
            if int(self.lifetime * 5) % 2 == 0:
                indicator_radius = self.radius + 5
                pygame.draw.circle(screen, (255, 255, 255), 
                                  (int(self.x), int(self.y)), int(indicator_radius), 1)
