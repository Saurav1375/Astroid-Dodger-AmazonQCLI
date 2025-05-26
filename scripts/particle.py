import pygame
import random
import math

class Particle:
    def __init__(self, x, y, velocity_x, velocity_y, color, size, lifetime):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        
        # Ensure color is a valid RGB tuple
        if isinstance(color, tuple) and len(color) >= 3:
            self.color = (int(color[0]), int(color[1]), int(color[2]))
        else:
            self.color = (255, 255, 255)  # Default to white
            
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
    
    def update(self, dt):
        # Update position
        self.x += self.velocity_x * dt * 60
        self.y += self.velocity_y * dt * 60
        
        # Update lifetime
        self.lifetime -= dt
        
        # Shrink particle as it ages
        self.size = max(0, self.size * (self.lifetime / self.max_lifetime))
    
    def is_dead(self):
        return self.lifetime <= 0 or self.size <= 0.5
    
    def draw(self, screen):
        # Simple drawing method without alpha blending
        size_int = max(1, int(self.size))
        
        # Calculate brightness based on remaining lifetime
        brightness = self.lifetime / self.max_lifetime
        r = min(255, max(0, int(self.color[0] * brightness)))
        g = min(255, max(0, int(self.color[1] * brightness)))
        b = min(255, max(0, int(self.color[2] * brightness)))
        
        # Draw a simple circle
        try:
            pygame.draw.circle(screen, (r, g, b), (int(self.x), int(self.y)), size_int)
        except ValueError:
            # Fallback to white if there's an error
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), size_int)


class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def update(self, dt):
        # Update all particles
        for particle in list(self.particles):
            particle.update(dt)
            if particle.is_dead():
                self.particles.remove(particle)
    
    def create_explosion(self, x, y, color, num_particles=20):
        """Create an explosion of particles at the given position"""
        for _ in range(num_particles):
            # Random velocity in all directions
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            
            # Random size and lifetime
            size = random.uniform(2, 5)
            lifetime = random.uniform(0.5, 1.5)
            
            # Vary the color slightly
            r = min(255, color[0] + random.randint(-20, 20))
            g = min(255, color[1] + random.randint(-20, 20))
            b = min(255, color[2] + random.randint(-20, 20))
            
            # Create the particle
            particle = Particle(x, y, velocity_x, velocity_y, (r, g, b), size, lifetime)
            self.particles.append(particle)
    
    def create_thruster(self, x, y, angle, color=(255, 150, 0)):
        """Create thruster particles behind a ship"""
        # Number of particles to create
        num_particles = 3
        
        for _ in range(num_particles):
            # Velocity in the opposite direction of the ship's angle
            base_angle = angle + math.pi + random.uniform(-0.2, 0.2)
            speed = random.uniform(1, 3)
            velocity_x = math.cos(base_angle) * speed
            velocity_y = math.sin(base_angle) * speed
            
            # Random size and lifetime
            size = random.uniform(1, 3)
            lifetime = random.uniform(0.2, 0.5)
            
            # Vary the color slightly
            r = min(255, color[0] + random.randint(-20, 20))
            g = min(255, color[1] + random.randint(-20, 20))
            b = min(255, color[2] + random.randint(-20, 20))
            
            # Create the particle
            particle = Particle(x, y, velocity_x, velocity_y, (r, g, b), size, lifetime)
            self.particles.append(particle)
    
    def create_healing_particle(self, x, y):
        """Create healing particles (green sparkles)"""
        # Random velocity upward with some spread
        angle = -math.pi/2 + random.uniform(-0.5, 0.5)  # Mostly upward
        speed = random.uniform(1, 3)
        velocity_x = math.cos(angle) * speed
        velocity_y = math.sin(angle) * speed
        
        # Green color with some variation
        r = random.randint(50, 150)
        g = random.randint(200, 255)
        b = random.randint(50, 150)
        
        # Create the particle
        size = random.uniform(1, 3)
        lifetime = random.uniform(0.5, 1.0)
        particle = Particle(x, y, velocity_x, velocity_y, (r, g, b), size, lifetime)
        self.particles.append(particle)
    
    def create_ambient_particle(self, x, y, color):
        """Create ambient background particles for visual effect"""
        # Slow random movement
        velocity_x = random.uniform(-0.5, 0.5)
        velocity_y = random.uniform(-0.5, 0.5)
        
        # Vary the color slightly
        r = min(255, color[0] + random.randint(-20, 20))
        g = min(255, color[1] + random.randint(-20, 20))
        b = min(255, color[2] + random.randint(-20, 20))
        
        # Create the particle with longer lifetime
        size = random.uniform(1, 2)
        lifetime = random.uniform(2.0, 5.0)
        particle = Particle(x, y, velocity_x, velocity_y, (r, g, b), size, lifetime)
        self.particles.append(particle)
    
    def create_shield_particles(self, x, y, radius):
        """Create particles around a shield perimeter"""
        # Create particles at random positions on the shield perimeter
        angle = random.uniform(0, 2 * math.pi)
        shield_x = x + math.cos(angle) * radius
        shield_y = y + math.sin(angle) * radius
        
        # Velocity slightly outward
        velocity_x = math.cos(angle) * random.uniform(0.5, 1.5)
        velocity_y = math.sin(angle) * random.uniform(0.5, 1.5)
        
        # Blue-white color
        r = random.randint(100, 200)
        g = random.randint(150, 250)
        b = 255
        
        # Create the particle
        size = random.uniform(1, 2)
        lifetime = random.uniform(0.3, 0.8)
        particle = Particle(shield_x, shield_y, velocity_x, velocity_y, (r, g, b), size, lifetime)
        self.particles.append(particle)
    
    def create_warp_effect(self, x, y, angle, count=20):
        """Create a warp/teleport effect"""
        for _ in range(count):
            # Particles emanate in all directions
            particle_angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            velocity_x = math.cos(particle_angle) * speed
            velocity_y = math.sin(particle_angle) * speed
            
            # Cyan/blue color
            r = random.randint(0, 100)
            g = random.randint(150, 255)
            b = random.randint(200, 255)
            
            # Create the particle
            size = random.uniform(2, 4)
            lifetime = random.uniform(0.5, 1.0)
            particle = Particle(x, y, velocity_x, velocity_y, (r, g, b), size, lifetime)
            self.particles.append(particle)
    
    def draw(self, screen):
        # Draw all particles
        for particle in self.particles:
            particle.draw(screen)
