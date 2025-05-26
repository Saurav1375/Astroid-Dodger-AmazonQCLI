import pygame
import math
import random

class Asteroid:
    def __init__(self, x, y, asteroid_type, angle, wave):
        self.x = x
        self.y = y
        self.type = asteroid_type
        self.angle = angle  # Direction of movement
        self.lifetime = 30.0  # Maximum lifetime in seconds
        
        # Set properties based on type
        if asteroid_type == "small":
            self.radius = 10
            self.speed = 3.0 + (wave * 0.1)  # Small asteroids are fast
            self.color = (200, 200, 200)  # Light gray
            self.points = self.generate_asteroid_points(self.radius, 5, 0.3)
            self.health = 1
        elif asteroid_type == "medium":
            self.radius = 20
            self.speed = 2.0 + (wave * 0.05)  # Medium speed
            self.color = (150, 150, 150)  # Medium gray
            self.points = self.generate_asteroid_points(self.radius, 8, 0.4)
            self.health = 2
        elif asteroid_type == "boss":
            self.radius = 50
            self.speed = 1.0 + (wave * 0.02)  # Slow but dangerous
            self.color = (255, 100, 100)  # Reddish
            self.points = self.generate_asteroid_points(self.radius, 12, 0.2)
            self.health = 10
        else:  # large
            self.radius = 30
            self.speed = 1.0 + (wave * 0.03)  # Large asteroids are slow
            self.color = (100, 100, 100)  # Dark gray
            self.points = self.generate_asteroid_points(self.radius, 10, 0.5)
            self.health = 3
        
        # Add some rotation
        self.rotation = 0
        self.rotation_speed = random.uniform(-0.02, 0.02)
    
    def generate_asteroid_points(self, radius, num_points, irregularity):
        """Generate irregular asteroid shape with the given radius and number of points"""
        points = []
        angle_step = 2 * math.pi / num_points
        
        for i in range(num_points):
            angle = i * angle_step
            # Add some irregularity to the radius
            r = radius * (1 + random.uniform(-irregularity, irregularity))
            x = math.cos(angle) * r
            y = math.sin(angle) * r
            points.append((x, y))
        
        return points
    
    def update(self, dt):
        # Move the asteroid
        self.x += math.cos(self.angle) * self.speed * dt * 60
        self.y += math.sin(self.angle) * self.speed * dt * 60
        
        # Rotate the asteroid
        self.rotation += self.rotation_speed * dt * 60
        
        # Update lifetime
        if hasattr(self, 'lifetime'):
            self.lifetime -= dt
    
    def is_offscreen(self, screen_width, screen_height, buffer=0):
        """Check if the asteroid is completely off the screen"""
        # Add a time-based check to ensure asteroids don't stay forever
        if hasattr(self, 'lifetime'):
            if self.lifetime <= 0:
                return True
        
        return (self.x + self.radius + buffer < 0 or 
                self.x - self.radius - buffer > screen_width or 
                self.y + self.radius + buffer < 0 or 
                self.y - self.radius - buffer > screen_height)
    
    def draw(self, screen):
        # Transform asteroid points based on position and rotation
        transformed_points = []
        for point in self.points:
            # Rotate
            rotated_x = point[0] * math.cos(self.rotation) - point[1] * math.sin(self.rotation)
            rotated_y = point[0] * math.sin(self.rotation) + point[1] * math.cos(self.rotation)
            
            # Translate
            transformed_points.append((rotated_x + self.x, rotated_y + self.y))
        
        # Draw the asteroid
        pygame.draw.polygon(screen, self.color, transformed_points)
        
        # Draw outline for better visibility
        pygame.draw.polygon(screen, (255, 255, 255), transformed_points, 1)
        
        # For boss asteroids, draw a health indicator
        if self.type == "boss":
            health_percent = self.health / 10  # Assuming boss starts with 10 health
            bar_width = self.radius * 2
            bar_height = 4
            
            # Background bar (red)
            pygame.draw.rect(screen, (255, 0, 0), 
                            (self.x - bar_width/2, self.y - self.radius - 10, 
                             bar_width, bar_height))
            
            # Health bar (green)
            pygame.draw.rect(screen, (0, 255, 0), 
                            (self.x - bar_width/2, self.y - self.radius - 10, 
                             bar_width * health_percent, bar_height))
