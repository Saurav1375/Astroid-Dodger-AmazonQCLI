import pygame
import random

class Star:
    def __init__(self, x, y, size, speed, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.color = color
        self.brightness = random.randint(100, 255)
        self.twinkle_direction = random.choice([-1, 1])
        self.twinkle_speed = random.uniform(0.5, 2.0)
    
    def update(self, dt):
        # Move the star downward (simulating ship movement)
        self.y += self.speed * dt * 60
        
        # Twinkle effect
        self.brightness += self.twinkle_direction * self.twinkle_speed
        if self.brightness >= 255:
            self.brightness = 255
            self.twinkle_direction = -1
        elif self.brightness <= 100:
            self.brightness = 100
            self.twinkle_direction = 1
    
    def draw(self, screen):
        # Calculate color with brightness
        r = min(255, int(self.color[0] * self.brightness / 255))
        g = min(255, int(self.color[1] * self.brightness / 255))
        b = min(255, int(self.color[2] * self.brightness / 255))
        
        # Draw the star as a small circle
        pygame.draw.circle(screen, (r, g, b), (int(self.x), int(self.y)), self.size)


class Starfield:
    def __init__(self, width, height, num_stars):
        self.width = width
        self.height = height
        self.stars = []
        self.dust_clouds = []
        self.star_color = (255, 255, 255)
        self.dust_color = (50, 50, 100, 30)
        
        # Create initial stars
        for _ in range(num_stars):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            speed = 0.2 + (size * 0.1)  # Larger stars move faster (parallax effect)
            self.stars.append(Star(x, y, size, speed, self.star_color))
        
        # Create dust clouds
        for _ in range(10):
            self.dust_clouds.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'size': random.randint(50, 150),
                'speed': random.uniform(0.05, 0.15),
                'alpha': random.randint(20, 50)
            })
    
    def set_colors(self, star_color, dust_color):
        """Set colors for the starfield"""
        self.star_color = star_color
        self.dust_color = dust_color
        
        # Update existing stars
        for star in self.stars:
            star.color = star_color
    
    def update(self, dt):
        # Update all stars
        for star in self.stars:
            star.update(dt)
            
            # If star goes off screen, reset it at the top
            if star.y > self.height:
                star.y = 0
                star.x = random.randint(0, self.width)
                star.color = self.star_color
        
        # Update dust clouds
        for cloud in self.dust_clouds:
            cloud['y'] += cloud['speed'] * dt * 60
            
            # If cloud goes off screen, reset it at the top
            if cloud['y'] - cloud['size'] > self.height:
                cloud['y'] = -cloud['size']
                cloud['x'] = random.randint(0, self.width)
    
    def draw(self, screen):
        # Draw dust clouds
        for cloud in self.dust_clouds:
            # Create a surface with per-pixel alpha
            cloud_surface = pygame.Surface((cloud['size'] * 2, cloud['size'] * 2), pygame.SRCALPHA)
            
            # Draw the cloud with alpha
            pygame.draw.circle(cloud_surface, self.dust_color, 
                              (cloud['size'], cloud['size']), cloud['size'])
            
            # Blit the cloud surface onto the screen
            screen.blit(cloud_surface, (int(cloud['x'] - cloud['size']), int(cloud['y'] - cloud['size'])))
        
        # Draw all stars
        for star in self.stars:
            star.draw(screen)
