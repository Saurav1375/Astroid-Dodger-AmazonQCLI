import pygame
import math

class Player:
    def __init__(self, x, y, screen_width, screen_height):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.angle = 0  # Angle in radians (0 = up)
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.2
        self.max_speed = 5
        self.rotation_speed = 0.1
        self.friction = 0.98
        self.health = 3
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 2.0  # 2 seconds of invulnerability after hit
        
        # Movement flags
        self.moving_forward = False
        self.moving_backward = False
        self.rotating_left = False
        self.rotating_right = False
        
        # Create a simple ship polygon
        self.ship_points = [
            (0, -15),  # Nose
            (-10, 10),  # Bottom left
            (0, 5),     # Bottom middle
            (10, 10)    # Bottom right
        ]
        
        # Thruster particles
        self.thruster_timer = 0
        self.thruster_interval = 0.05  # Emit particles every 0.05 seconds
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.moving_forward = True
            elif event.key == pygame.K_DOWN:
                self.moving_backward = True
            elif event.key == pygame.K_LEFT:
                self.rotating_left = True
            elif event.key == pygame.K_RIGHT:
                self.rotating_right = True
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self.moving_forward = False
            elif event.key == pygame.K_DOWN:
                self.moving_backward = False
            elif event.key == pygame.K_LEFT:
                self.rotating_left = False
            elif event.key == pygame.K_RIGHT:
                self.rotating_right = False
    
    def update(self, dt):
        # Handle rotation
        if self.rotating_left:
            self.angle -= self.rotation_speed * dt * 60
        if self.rotating_right:
            self.angle += self.rotation_speed * dt * 60
        
        # Normalize angle
        self.angle = self.angle % (2 * math.pi)
        
        # Handle acceleration
        if self.moving_forward:
            self.velocity_x += math.sin(self.angle) * self.acceleration * dt * 60
            self.velocity_y -= math.cos(self.angle) * self.acceleration * dt * 60
        if self.moving_backward:
            self.velocity_x -= math.sin(self.angle) * self.acceleration * dt * 60 * 0.5
            self.velocity_y += math.cos(self.angle) * self.acceleration * dt * 60 * 0.5
        
        # Apply friction
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        # Limit speed
        speed = math.sqrt(self.velocity_x ** 2 + self.velocity_y ** 2)
        if speed > self.max_speed:
            self.velocity_x = (self.velocity_x / speed) * self.max_speed
            self.velocity_y = (self.velocity_y / speed) * self.max_speed
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Wrap around screen edges
        if self.x < 0:
            self.x = self.screen_width
        elif self.x > self.screen_width:
            self.x = 0
        
        if self.y < 0:
            self.y = self.screen_height
        elif self.y > self.screen_height:
            self.y = 0
        
        # Update invulnerability
        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
    
    def take_damage(self):
        if not self.invulnerable:
            self.health -= 1
            self.invulnerable = True
            self.invulnerable_timer = self.invulnerable_duration
    
    def get_collision_radius(self):
        return 12  # Approximate radius of the ship
    
    def draw(self, screen, active_powerups):
        # Transform ship points based on position and rotation
        transformed_points = []
        
        # Apply size shrink if active
        scale = 1.0
        if active_powerups["size_shrink"] > 0:
            scale = 0.5
        
        for point in self.ship_points:
            # Scale, rotate, and translate the point
            x = point[0] * scale
            y = point[1] * scale
            
            # Rotate
            rotated_x = x * math.cos(self.angle) - y * math.sin(self.angle)
            rotated_y = x * math.sin(self.angle) + y * math.cos(self.angle)
            
            # Translate
            transformed_points.append((rotated_x + self.x, rotated_y + self.y))
        
        # Draw the ship
        ship_color = (255, 255, 255)
        if self.invulnerable:
            # Flash when invulnerable
            if int(pygame.time.get_ticks() / 100) % 2 == 0:
                ship_color = (255, 255, 255)
            else:
                ship_color = (100, 100, 255)
        
        pygame.draw.polygon(screen, ship_color, transformed_points)
        
        # Draw shield if active
        if active_powerups["shield"] > 0:
            shield_radius = self.get_collision_radius() * 1.5
            shield_color = (100, 150, 255, 128)  # Light blue with transparency
            
            # Create a surface for the shield with transparency
            shield_surface = pygame.Surface((shield_radius * 2, shield_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, shield_color, (shield_radius, shield_radius), shield_radius)
            
            # Draw the shield centered on the player
            screen.blit(shield_surface, (self.x - shield_radius, self.y - shield_radius))
        
        # Draw thruster flame if moving forward
        if self.moving_forward:
            # Calculate thruster position (back of the ship)
            thruster_x = self.x - math.sin(self.angle) * 10 * scale
            thruster_y = self.y + math.cos(self.angle) * 10 * scale
            
            # Draw a triangle for the thruster flame
            flame_length = 5 + (pygame.time.get_ticks() % 10) / 2  # Animated flame length
            flame_points = [
                (thruster_x, thruster_y),
                (thruster_x - math.sin(self.angle + 0.3) * flame_length, 
                 thruster_y + math.cos(self.angle + 0.3) * flame_length),
                (thruster_x - math.sin(self.angle) * flame_length * 2, 
                 thruster_y + math.cos(self.angle) * flame_length * 2),
                (thruster_x - math.sin(self.angle - 0.3) * flame_length, 
                 thruster_y + math.cos(self.angle - 0.3) * flame_length)
            ]
            
            # Draw the flame with a gradient color
            flame_color = (255, 150, 0)  # Orange
            pygame.draw.polygon(screen, flame_color, flame_points)
