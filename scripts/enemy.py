import pygame
import math
import random
from .asteroid import Asteroid

class HomingMissile:
    def __init__(self, x, y, target, wave):
        self.x = x
        self.y = y
        self.target = target  # The player object to track
        self.radius = 8
        self.speed = 2.0 + (wave * 0.1)  # Increases with wave number
        self.max_speed = 4.0 + (wave * 0.1)
        self.turn_rate = 0.03  # How quickly it can change direction
        self.angle = random.uniform(0, 2 * math.pi)  # Initial random direction
        self.health = 1
        self.damage = 1
        self.fuel = 10.0  # Seconds of fuel before it self-destructs
        self.color = (255, 100, 0)  # Orange
        
        # Thruster particles
        self.thruster_timer = 0
        self.thruster_interval = 0.05
    
    def update(self, dt, particle_system):
        # Calculate angle to target
        target_angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
        
        # Gradually turn towards target
        angle_diff = (target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        if abs(angle_diff) < self.turn_rate:
            self.angle = target_angle
        elif angle_diff > 0:
            self.angle += self.turn_rate
        else:
            self.angle -= self.turn_rate
        
        # Accelerate in the current direction
        self.speed = min(self.speed + 0.05, self.max_speed)
        
        # Move
        self.x += math.cos(self.angle) * self.speed * dt * 60
        self.y += math.sin(self.angle) * self.speed * dt * 60
        
        # Update fuel
        self.fuel -= dt
        
        # Create thruster particles
        self.thruster_timer -= dt
        if self.thruster_timer <= 0:
            self.thruster_timer = self.thruster_interval
            particle_system.create_thruster(
                self.x - math.cos(self.angle) * 10,
                self.y - math.sin(self.angle) * 10,
                self.angle + math.pi,
                (255, 100, 0)
            )
        
        return self.fuel <= 0  # Return True if missile should self-destruct
    
    def draw(self, screen):
        # Draw missile body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw direction indicator (nose cone)
        nose_x = self.x + math.cos(self.angle) * self.radius
        nose_y = self.y + math.sin(self.angle) * self.radius
        pygame.draw.line(screen, (255, 255, 255), (self.x, self.y), (nose_x, nose_y), 3)
        
        # Draw fuel indicator
        fuel_percent = self.fuel / 10.0
        bar_width = self.radius * 2
        bar_height = 2
        
        pygame.draw.rect(screen, (255, 0, 0), 
                        (self.x - bar_width/2, self.y - self.radius - 5, 
                         bar_width, bar_height))
        
        pygame.draw.rect(screen, (0, 255, 0), 
                        (self.x - bar_width/2, self.y - self.radius - 5, 
                         bar_width * fuel_percent, bar_height))


class SpinningBlade(Asteroid):
    def __init__(self, x, y, wave):
        # Initialize with medium asteroid properties
        super().__init__(x, y, "medium", random.uniform(0, 2 * math.pi), wave)
        
        # Override some properties
        self.type = "blade"
        self.radius = 25
        self.speed = 1.5 + (wave * 0.05)
        self.color = (200, 100, 200)  # Purple
        self.health = 3
        self.rotation_speed = 0.1  # Faster rotation
        
        # Create blade shape
        self.points = self.generate_blade_points()
    
    def generate_blade_points(self):
        """Generate a blade-like shape"""
        points = []
        num_points = 8
        angle_step = 2 * math.pi / num_points
        
        for i in range(num_points):
            angle = i * angle_step
            # Create alternating long and short points
            r = self.radius * (1.5 if i % 2 == 0 else 0.7)
            x = math.cos(angle) * r
            y = math.sin(angle) * r
            points.append((x, y))
        
        return points
    
    def split(self, wave):
        """Split into smaller blades when destroyed"""
        fragments = []
        for _ in range(3):
            # Create smaller blade fragments
            fragment = SpinningBladeFragment(
                self.x + random.uniform(-10, 10),
                self.y + random.uniform(-10, 10),
                wave
            )
            fragments.append(fragment)
        return fragments


class SpinningBladeFragment(Asteroid):
    def __init__(self, x, y, wave):
        # Initialize with small asteroid properties
        super().__init__(x, y, "small", random.uniform(0, 2 * math.pi), wave)
        
        # Override some properties
        self.type = "blade_fragment"
        self.radius = 10
        self.speed = 3.0 + (wave * 0.1)
        self.color = (200, 100, 200)  # Purple
        self.health = 1
        self.rotation_speed = 0.2  # Even faster rotation
        
        # Create blade fragment shape
        self.points = self.generate_blade_fragment_points()
    
    def generate_blade_fragment_points(self):
        """Generate a blade fragment shape"""
        points = []
        num_points = 5
        angle_step = 2 * math.pi / num_points
        
        for i in range(num_points):
            angle = i * angle_step
            # Create jagged shape
            r = self.radius * (1.3 if i % 2 == 0 else 0.8)
            x = math.cos(angle) * r
            y = math.sin(angle) * r
            points.append((x, y))
        
        return points


class CrystalAsteroid(Asteroid):
    def __init__(self, x, y, wave):
        # Initialize with medium asteroid properties
        super().__init__(x, y, "medium", random.uniform(0, 2 * math.pi), wave)
        
        # Override some properties
        self.type = "crystal"
        self.radius = 20
        self.speed = 1.0 + (wave * 0.03)
        self.base_color = (100, 200, 255)  # Light blue
        self.color = self.base_color
        self.health = 5  # Harder to destroy
        self.points_value = 500  # Higher score value
        self.rotation_speed = 0.01  # Slow rotation
        
        # Create crystal shape
        self.points = self.generate_crystal_points()
        
        # Shimmer effect
        self.shimmer_time = 0
    
    def generate_crystal_points(self):
        """Generate a crystal-like shape"""
        points = []
        num_points = 6
        angle_step = 2 * math.pi / num_points
        
        for i in range(num_points):
            angle = i * angle_step
            # Create crystal shape with some randomness
            r = self.radius * (1.0 + random.uniform(-0.1, 0.3))
            x = math.cos(angle) * r
            y = math.sin(angle) * r
            points.append((x, y))
        
        return points
    
    def update(self, dt):
        # Call parent update method
        super().update(dt)
        
        # Update shimmer effect
        self.shimmer_time += dt
        shimmer = (math.sin(self.shimmer_time * 5) + 1) / 2  # 0 to 1
        
        # Make the crystal shimmer by adjusting its color
        r = min(255, int(self.base_color[0] + shimmer * 50))
        g = min(255, int(self.base_color[1] + shimmer * 50))
        b = min(255, int(self.base_color[2] + shimmer * 50))
        self.color = (r, g, b)
    
    def draw(self, screen):
        # Draw the crystal with a glow effect
        glow_radius = self.radius * 1.2
        glow_surface = pygame.Surface((int(glow_radius * 2), int(glow_radius * 2)), pygame.SRCALPHA)
        
        # Draw glow
        for i in range(3):
            alpha = 100 - i * 30
            r = glow_radius - i * 2
            pygame.draw.circle(glow_surface, (*self.color, alpha), 
                              (int(glow_radius), int(glow_radius)), int(r))
        
        # Blit the glow
        screen.blit(glow_surface, (int(self.x - glow_radius), int(self.y - glow_radius)))
        
        # Draw the crystal itself (using parent method)
        super().draw(screen)
