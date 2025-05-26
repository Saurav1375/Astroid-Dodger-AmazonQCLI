import pygame
import math
import random
from .enemy import HomingMissile

class Boss:
    def __init__(self, x, y, wave, screen_width, screen_height):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.wave = wave
        
        # Boss properties
        self.type = f"boss_{(wave // 5) % 3 + 1}"  # 3 different boss types
        self.radius = 60
        self.max_health = 20 + (wave // 5) * 10
        self.health = self.max_health
        self.speed = 0.8
        self.damage = 2
        
        # Movement pattern
        self.target_x = screen_width // 2
        self.target_y = screen_height // 3
        self.movement_timer = 0
        self.movement_change = random.uniform(3, 6)
        
        # Attack patterns
        self.attack_timer = 0
        self.attack_cooldown = 2.0
        self.attack_pattern = 0
        self.missiles = []
        
        # Visual properties
        self.rotation = 0
        self.rotation_speed = 0.01
        self.color = self.get_boss_color()
        self.points = self.generate_boss_points()
        
        # Special abilities based on boss type
        self.special_timer = 0
        self.special_cooldown = 10.0
    
    def get_boss_color(self):
        if self.type == "boss_1":
            return (255, 50, 50)  # Red
        elif self.type == "boss_2":
            return (50, 50, 255)  # Blue
        else:
            return (255, 200, 50)  # Gold
    
    def generate_boss_points(self):
        """Generate boss shape based on type"""
        points = []
        
        if self.type == "boss_1":
            # Star-shaped boss
            num_points = 10
            angle_step = 2 * math.pi / num_points
            
            for i in range(num_points):
                angle = i * angle_step
                # Create alternating long and short points
                r = self.radius * (1.2 if i % 2 == 0 else 0.8)
                x = math.cos(angle) * r
                y = math.sin(angle) * r
                points.append((x, y))
                
        elif self.type == "boss_2":
            # Hexagon boss with protrusions
            num_points = 6
            angle_step = 2 * math.pi / num_points
            
            for i in range(num_points):
                angle = i * angle_step
                # Main hexagon point
                r = self.radius
                x = math.cos(angle) * r
                y = math.sin(angle) * r
                points.append((x, y))
                
                # Add a protrusion
                angle_mid = angle + angle_step / 2
                r_mid = self.radius * 0.6
                x_mid = math.cos(angle_mid) * r_mid
                y_mid = math.sin(angle_mid) * r_mid
                points.append((x_mid, y_mid))
                
        else:  # boss_3
            # Circular boss with inward spikes
            num_points = 16
            angle_step = 2 * math.pi / num_points
            
            for i in range(num_points):
                angle = i * angle_step
                # Alternating outer and inner points
                if i % 2 == 0:
                    r = self.radius
                else:
                    r = self.radius * 0.7
                x = math.cos(angle) * r
                y = math.sin(angle) * r
                points.append((x, y))
        
        return points
    
    def update(self, dt, player, particle_system):
        # Update rotation
        self.rotation += self.rotation_speed
        
        # Update movement
        self.movement_timer += dt
        if self.movement_timer >= self.movement_change:
            self.movement_timer = 0
            self.movement_change = random.uniform(3, 6)
            self.target_x = random.randint(self.radius, self.screen_width - self.radius)
            self.target_y = random.randint(self.radius, self.screen_height // 2)
        
        # Move towards target position
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 5:
            self.x += dx / distance * self.speed * dt * 60
            self.y += dy / distance * self.speed * dt * 60
        
        # Update attack timer
        self.attack_timer += dt
        if self.attack_timer >= self.attack_cooldown:
            self.attack_timer = 0
            self.attack_cooldown = random.uniform(1.5, 3.0)
            self.perform_attack(player, particle_system)
        
        # Update special ability timer
        self.special_timer += dt
        if self.special_timer >= self.special_cooldown:
            self.special_timer = 0
            self.perform_special_ability(player, particle_system)
        
        # Update missiles
        for missile in list(self.missiles):
            if missile.update(dt, particle_system):
                self.missiles.remove(missile)
        
        # Return any new objects that need to be added to the game
        return []
    
    def perform_attack(self, player, particle_system):
        """Perform a basic attack based on the current pattern"""
        self.attack_pattern = (self.attack_pattern + 1) % 3
        
        if self.attack_pattern == 0:
            # Single missile attack
            missile = HomingMissile(self.x, self.y, player, self.wave)
            self.missiles.append(missile)
            
        elif self.attack_pattern == 1:
            # Triple missile attack
            for i in range(3):
                angle = random.uniform(0, 2 * math.pi)
                offset_x = math.cos(angle) * self.radius
                offset_y = math.sin(angle) * self.radius
                missile = HomingMissile(self.x + offset_x, self.y + offset_y, player, self.wave)
                self.missiles.append(missile)
                
        else:
            # Circle of particles
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                particle_system.create_explosion(
                    self.x + math.cos(rad) * self.radius,
                    self.y + math.sin(rad) * self.radius,
                    self.color
                )
    
    def perform_special_ability(self, player, particle_system):
        """Perform a special ability based on boss type"""
        if self.type == "boss_1":
            # Boss 1: Ring of fire - create a ring of explosion particles
            for angle in range(0, 360, 10):
                rad = math.radians(angle)
                particle_system.create_explosion(
                    self.x + math.cos(rad) * self.radius * 1.5,
                    self.y + math.sin(rad) * self.radius * 1.5,
                    (255, 100, 0),
                    30
                )
                
        elif self.type == "boss_2":
            # Boss 2: Shield regeneration - recover some health
            heal_amount = self.max_health * 0.1
            self.health = min(self.max_health, self.health + heal_amount)
            
            # Visual effect for healing
            for _ in range(20):
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, self.radius)
                particle_system.create_healing_particle(
                    self.x + math.cos(angle) * distance,
                    self.y + math.sin(angle) * distance
                )
                
        else:  # boss_3
            # Boss 3: Missile barrage - launch many missiles
            for _ in range(5):
                angle = random.uniform(0, 2 * math.pi)
                offset_x = math.cos(angle) * self.radius
                offset_y = math.sin(angle) * self.radius
                missile = HomingMissile(self.x + offset_x, self.y + offset_y, player, self.wave)
                self.missiles.append(missile)
    
    def take_damage(self, damage, particle_system):
        """Take damage and create particles"""
        self.health -= damage
        
        # Create damage particles
        particle_system.create_explosion(self.x, self.y, (255, 255, 255), 5)
        
        # Check if destroyed
        if self.health <= 0:
            # Create big explosion
            particle_system.create_explosion(self.x, self.y, self.color, 50)
            return True
        
        return False
    
    def draw(self, screen):
        # Draw health bar
        health_percent = self.health / self.max_health
        bar_width = self.radius * 2
        bar_height = 8
        
        # Background bar (red)
        pygame.draw.rect(screen, (255, 0, 0), 
                        (self.x - bar_width/2, self.y - self.radius - 20, 
                         bar_width, bar_height))
        
        # Health bar (green)
        pygame.draw.rect(screen, (0, 255, 0), 
                        (self.x - bar_width/2, self.y - self.radius - 20, 
                         bar_width * health_percent, bar_height))
        
        # Draw boss name
        font = pygame.font.SysFont(None, 24)
        name_text = font.render(f"{self.type.upper()}", True, (255, 255, 255))
        screen.blit(name_text, (self.x - name_text.get_width() // 2, self.y - self.radius - 40))
        
        # Draw the boss
        transformed_points = []
        for point in self.points:
            # Rotate
            rotated_x = point[0] * math.cos(self.rotation) - point[1] * math.sin(self.rotation)
            rotated_y = point[0] * math.sin(self.rotation) + point[1] * math.cos(self.rotation)
            
            # Translate
            transformed_points.append((rotated_x + self.x, rotated_y + self.y))
        
        # Draw the boss shape
        pygame.draw.polygon(screen, self.color, transformed_points)
        pygame.draw.polygon(screen, (255, 255, 255), transformed_points, 2)
        
        # Draw core
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), int(self.radius * 0.3))
        
        # Draw missiles
        for missile in self.missiles:
            missile.draw(screen)
    
    def get_drop_items(self):
        """Return power-ups and points when boss is defeated"""
        return {
            "points": 5000 + (self.wave // 5) * 1000,
            "powerup_types": ["shield", "rapid_fire", "slow_motion", "size_shrink"],
            "powerup_count": 2
        }
