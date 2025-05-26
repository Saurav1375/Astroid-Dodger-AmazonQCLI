import pygame
import math

class Projectile:
    def __init__(self, x, y, angle, speed=10, color=(255, 255, 0), radius=3):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.color = color
        self.radius = radius
        self.lifetime = 1.5  # Projectiles disappear after 1.5 seconds
        
        # Calculate velocity components
        self.velocity_x = math.sin(angle) * speed
        self.velocity_y = -math.cos(angle) * speed
    
    def update(self, dt):
        # Update position
        self.x += self.velocity_x * dt * 60
        self.y += self.velocity_y * dt * 60
        
        # Update lifetime
        self.lifetime -= dt
    
    def is_offscreen(self, screen_width, screen_height):
        """Check if the projectile is off the screen or expired"""
        return (self.x < 0 or 
                self.x > screen_width or 
                self.y < 0 or 
                self.y > screen_height or
                self.lifetime <= 0)
    
    def draw(self, screen):
        # Draw the projectile
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw a trail
        trail_length = 10
        trail_end_x = self.x - self.velocity_x / self.speed * trail_length
        trail_end_y = self.y - self.velocity_y / self.speed * trail_length
        
        pygame.draw.line(screen, self.color, (self.x, self.y), (trail_end_x, trail_end_y), 2)


class Weapon:
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager
        self.cooldown = 0
        self.cooldown_time = 0.25  # 4 shots per second
    
    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt
    
    def fire_normal(self, x, y, angle):
        """Fire a single projectile"""
        if self.cooldown <= 0:
            self.cooldown = self.cooldown_time
            self.sound_manager.play_sound("laser")
            return [Projectile(x, y, angle)]
        return []
    
    def fire_rapid(self, x, y, angle):
        """Fire multiple projectiles in a spread pattern"""
        if self.cooldown <= 0:
            self.cooldown = self.cooldown_time / 3  # Faster firing rate
            self.sound_manager.play_sound("laser")
            
            # Create three projectiles in a spread
            spread = 0.1  # Spread angle in radians
            return [
                Projectile(x, y, angle - spread, color=(255, 200, 0)),
                Projectile(x, y, angle, color=(255, 255, 0)),
                Projectile(x, y, angle + spread, color=(255, 200, 0))
            ]
        return []
