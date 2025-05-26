import pygame
import math
import random

class BlackHole:
    def __init__(self, x, y, radius=30):
        self.x = x
        self.y = y
        self.radius = radius
        self.pull_radius = radius * 5  # Area of effect
        self.pull_strength = 0.5
        self.rotation = 0
        self.rotation_speed = 0.02
        self.active = True
        self.lifetime = random.uniform(15, 30)  # Black holes exist for limited time
        
        # Visual properties
        self.color = (20, 20, 40)
        self.ring_colors = [
            (100, 50, 150),  # Purple
            (50, 50, 100),   # Dark blue
            (20, 20, 40)     # Almost black
        ]
    
    def update(self, dt, game_objects):
        # Update rotation
        self.rotation += self.rotation_speed * dt * 60
        
        # Update lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
        
        # Apply gravitational pull to nearby objects
        for obj in game_objects:
            if hasattr(obj, 'x') and hasattr(obj, 'y'):
                # Calculate distance
                dx = self.x - obj.x
                dy = self.y - obj.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Apply pull if within range
                if distance < self.pull_radius and distance > 0:
                    # Pull strength decreases with distance
                    pull_factor = (1 - distance / self.pull_radius) * self.pull_strength
                    
                    # Apply pull
                    if hasattr(obj, 'velocity_x') and hasattr(obj, 'velocity_y'):
                        obj.velocity_x += dx / distance * pull_factor * dt * 60
                        obj.velocity_y += dy / distance * pull_factor * dt * 60
                    
                    # If object is very close, damage it
                    if distance < self.radius * 1.2:
                        if hasattr(obj, 'take_damage'):
                            obj.take_damage(1)
    
    def draw(self, screen):
        # Draw outer rings
        for i, color in enumerate(self.ring_colors):
            ring_radius = self.radius * (1 + i * 0.5)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(ring_radius))
        
        # Draw the black hole core
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), int(self.radius * 0.8))
        
        # Draw swirl effect
        for i in range(8):
            angle = self.rotation + i * math.pi / 4
            end_x = self.x + math.cos(angle) * self.radius * 0.7
            end_y = self.y + math.sin(angle) * self.radius * 0.7
            pygame.draw.line(screen, (100, 100, 150), 
                            (self.x, self.y), (end_x, end_y), 2)
        
        # Draw pull radius indicator (faint circle)
        if self.lifetime < 5.0 and int(self.lifetime * 5) % 2 == 0:  # Flash when about to disappear
            pygame.draw.circle(screen, (100, 50, 150, 30), 
                              (int(self.x), int(self.y)), int(self.pull_radius), 1)


class SpaceStorm:
    def __init__(self, width, height, duration=15):
        self.width = width
        self.height = height
        self.duration = duration
        self.time_left = duration
        self.active = True
        
        # Storm properties
        self.particles = []
        self.lightning_timer = 0
        self.lightning_interval = random.uniform(1, 3)
        self.lightning_duration = 0
        self.lightning_points = []
        
        # Create initial particles
        for _ in range(200):
            self.particles.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'size': random.randint(1, 3),
                'speed': random.uniform(3, 8),
                'angle': random.uniform(0, 2 * math.pi)
            })
    
    def update(self, dt):
        # Update duration
        self.time_left -= dt
        if self.time_left <= 0:
            self.active = False
        
        # Update particles
        for particle in self.particles:
            # Move particle
            particle['x'] += math.cos(particle['angle']) * particle['speed'] * dt * 60
            particle['y'] += math.sin(particle['angle']) * particle['speed'] * dt * 60
            
            # Wrap around screen
            if particle['x'] < 0:
                particle['x'] = self.width
            elif particle['x'] > self.width:
                particle['x'] = 0
            
            if particle['y'] < 0:
                particle['y'] = self.height
            elif particle['y'] > self.height:
                particle['y'] = 0
        
        # Update lightning
        self.lightning_timer += dt
        if self.lightning_timer >= self.lightning_interval:
            self.lightning_timer = 0
            self.lightning_interval = random.uniform(1, 3)
            self.lightning_duration = 0.2  # Lightning lasts for 0.2 seconds
            
            # Create new lightning bolt
            self.lightning_points = self.generate_lightning()
        
        if self.lightning_duration > 0:
            self.lightning_duration -= dt
    
    def generate_lightning(self):
        """Generate a random lightning bolt"""
        points = []
        
        # Start from a random position at the top
        x = random.randint(0, self.width)
        y = 0
        points.append((x, y))
        
        # Create a jagged path downward
        while y < self.height:
            x += random.randint(-50, 50)
            y += random.randint(20, 50)
            points.append((x, y))
        
        return points
    
    def draw(self, screen):
        # Create a semi-transparent overlay for the storm
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 50, 100))  # Blue tint with transparency
        screen.blit(overlay, (0, 0))
        
        # Draw storm particles
        for particle in self.particles:
            color = (200, 200, 255)  # Light blue
            pygame.draw.circle(screen, color, 
                              (int(particle['x']), int(particle['y'])), 
                              particle['size'])
        
        # Draw lightning if active
        if self.lightning_duration > 0:
            # Draw the main lightning bolt
            if len(self.lightning_points) > 1:
                pygame.draw.lines(screen, (255, 255, 255), False, self.lightning_points, 3)
            
            # Draw some branches
            for i in range(1, len(self.lightning_points) - 1):
                if random.random() < 0.3:  # 30% chance for each point to have a branch
                    start = self.lightning_points[i]
                    end = (start[0] + random.randint(-100, 100), 
                           start[1] + random.randint(-20, 80))
                    pygame.draw.line(screen, (200, 200, 255), start, end, 2)
        
        # Draw timer if storm is about to end
        if self.time_left < 5.0:
            font = pygame.font.SysFont(None, 36)
            text = font.render(f"Storm: {self.time_left:.1f}s", True, (255, 255, 255))
            screen.blit(text, (self.width // 2 - text.get_width() // 2, 50))


class Wormhole:
    def __init__(self, x1, y1, x2, y2, radius=25):
        # Entry point
        self.entry_x = x1
        self.entry_y = y1
        
        # Exit point
        self.exit_x = x2
        self.exit_y = y2
        
        self.radius = radius
        self.active = True
        self.cooldown = 0
        self.cooldown_time = 1.0  # Time before wormhole can teleport again
        self.lifetime = random.uniform(20, 30)
        
        # Visual properties
        self.rotation1 = 0
        self.rotation2 = math.pi  # Start at opposite rotation
        self.rotation_speed = 0.03
        self.color1 = (100, 200, 255)  # Blue
        self.color2 = (255, 100, 200)  # Pink
    
    def update(self, dt, asteroids):
        # Update rotation
        self.rotation1 += self.rotation_speed * dt * 60
        self.rotation2 += self.rotation_speed * dt * 60
        
        # Update lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
        
        # Update cooldown
        if self.cooldown > 0:
            self.cooldown -= dt
        
        # Check for asteroids to teleport
        if self.cooldown <= 0:
            for asteroid in asteroids:
                # Calculate distance to entry point
                dx = self.entry_x - asteroid.x
                dy = self.entry_y - asteroid.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Teleport if close enough
                if distance < self.radius:
                    # Teleport the asteroid
                    asteroid.x = self.exit_x
                    asteroid.y = self.exit_y
                    
                    # Reset cooldown
                    self.cooldown = self.cooldown_time
                    break
    
    def draw(self, screen):
        # Draw entry wormhole
        self.draw_wormhole(screen, self.entry_x, self.entry_y, self.rotation1, self.color1)
        
        # Draw exit wormhole
        self.draw_wormhole(screen, self.exit_x, self.exit_y, self.rotation2, self.color2)
        
        # Draw connecting line (faint)
        pygame.draw.line(screen, (150, 150, 150, 100), 
                        (self.entry_x, self.entry_y), 
                        (self.exit_x, self.exit_y), 1)
    
    def draw_wormhole(self, screen, x, y, rotation, color):
        # Draw outer ring
        pygame.draw.circle(screen, color, (int(x), int(y)), int(self.radius))
        
        # Draw inner black hole
        pygame.draw.circle(screen, (0, 0, 0), (int(x), int(y)), int(self.radius * 0.7))
        
        # Draw spiral arms
        for i in range(4):
            angle = rotation + i * math.pi / 2
            for j in range(5):
                radius_factor = 0.2 + j * 0.15
                arm_x = x + math.cos(angle + j * 0.2) * self.radius * radius_factor
                arm_y = y + math.sin(angle + j * 0.2) * self.radius * radius_factor
                size = int(3 - j * 0.5)
                pygame.draw.circle(screen, (255, 255, 255), (int(arm_x), int(arm_y)), size)
