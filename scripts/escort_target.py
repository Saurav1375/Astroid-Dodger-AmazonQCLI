import pygame
import math

class EscortTarget:
    def __init__(self, x, y, dest_x, dest_y):
        self.x = x
        self.y = y
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.radius = 25
        self.speed = 0.8
        self.health = 5
        self.max_health = 5
        self.reached_destination = False
        self.invulnerable = False
        self.invulnerable_timer = 0
        
        # Visual properties
        self.color = (0, 200, 200)  # Cyan
        self.rotation = 0
        self.rotation_speed = 0.01
        
        # Generate shape
        self.points = self.generate_points()
    
    def generate_points(self):
        """Generate a shape for the escort target"""
        points = []
        num_points = 6  # Hexagon
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = math.cos(angle) * self.radius
            y = math.sin(angle) * self.radius
            points.append((x, y))
        return points
    
    def update(self, dt):
        # Update rotation
        self.rotation += self.rotation_speed * dt * 60
        
        # Move towards destination
        dx = self.dest_x - self.x
        dy = self.dest_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 5:
            # Move towards destination
            self.x += dx / distance * self.speed * dt * 60
            self.y += dy / distance * self.speed * dt * 60
        else:
            # Reached destination
            self.reached_destination = True
        
        # Update invulnerability
        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
    
    def take_damage(self, damage=1):
        """Take damage if not invulnerable"""
        if not self.invulnerable:
            self.health -= damage
            self.invulnerable = True
            self.invulnerable_timer = 1.0  # 1 second of invulnerability
    
    def draw(self, screen):
        # Draw health bar
        health_percent = self.health / self.max_health
        bar_width = self.radius * 2
        bar_height = 6
        
        # Background bar (red)
        pygame.draw.rect(screen, (255, 0, 0), 
                        (self.x - bar_width/2, self.y - self.radius - 15, 
                         bar_width, bar_height))
        
        # Health bar (green)
        pygame.draw.rect(screen, (0, 255, 0), 
                        (self.x - bar_width/2, self.y - self.radius - 15, 
                         bar_width * health_percent, bar_height))
        
        # Draw "ESCORT" text
        font = pygame.font.SysFont(None, 20)
        text = font.render("ESCORT", True, (255, 255, 255))
        screen.blit(text, (self.x - text.get_width() // 2, self.y - self.radius - 30))
        
        # Transform points based on position and rotation
        transformed_points = []
        for point in self.points:
            # Rotate
            rotated_x = point[0] * math.cos(self.rotation) - point[1] * math.sin(self.rotation)
            rotated_y = point[0] * math.sin(self.rotation) + point[1] * math.cos(self.rotation)
            
            # Translate
            transformed_points.append((rotated_x + self.x, rotated_y + self.y))
        
        # Draw the target
        color = self.color
        if self.invulnerable:
            # Flash when invulnerable
            if int(pygame.time.get_ticks() / 100) % 2 == 0:
                color = (255, 255, 255)
        
        pygame.draw.polygon(screen, color, transformed_points)
        pygame.draw.polygon(screen, (255, 255, 255), transformed_points, 2)
        
        # Draw core
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), int(self.radius * 0.3))
        
        # Draw destination marker
        pygame.draw.circle(screen, (0, 200, 200, 100), (int(self.dest_x), int(self.dest_y)), 10, 2)
        pygame.draw.line(screen, (0, 200, 200, 100), 
                        (self.dest_x - 15, self.dest_y), (self.dest_x + 15, self.dest_y), 2)
        pygame.draw.line(screen, (0, 200, 200, 100), 
                        (self.dest_x, self.dest_y - 15), (self.dest_x, self.dest_y + 15), 2)
