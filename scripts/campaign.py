import pygame
import random
import math
from .particle import ParticleSystem

class Sector:
    def __init__(self, name, description, difficulty, background_type, special_feature=None):
        self.name = name
        self.description = description
        self.difficulty = difficulty  # 1-5 scale
        self.background_type = background_type
        self.special_feature = special_feature
        self.completed = False
        self.stars = 0  # Performance rating (0-3 stars)
    
    def get_asteroid_properties(self):
        """Return modified asteroid properties based on sector difficulty"""
        return {
            "speed_multiplier": 1.0 + (self.difficulty - 1) * 0.2,
            "spawn_rate_multiplier": 1.0 + (self.difficulty - 1) * 0.15,
            "health_multiplier": 1.0 + (self.difficulty - 1) * 0.25,
            "special_types": self.get_special_asteroid_types()
        }
    
    def get_special_asteroid_types(self):
        """Return special asteroid types that appear in this sector"""
        special_types = []
        
        # Add special types based on difficulty
        if self.difficulty >= 2:
            special_types.append("crystal")
        if self.difficulty >= 3:
            special_types.append("blade")
        if self.difficulty >= 4:
            special_types.append("homing")
        
        return special_types
    
    def get_background_colors(self):
        """Return background colors based on sector type"""
        if self.background_type == "nebula":
            return {
                "stars": (255, 255, 255),
                "dust": (200, 100, 200, 50),  # Purple nebula
                "accent": (150, 50, 200)
            }
        elif self.background_type == "ice":
            return {
                "stars": (200, 220, 255),
                "dust": (100, 150, 200, 50),  # Blue ice field
                "accent": (50, 150, 255)
            }
        elif self.background_type == "fire":
            return {
                "stars": (255, 220, 150),
                "dust": (200, 100, 50, 50),  # Red fire field
                "accent": (255, 100, 50)
            }
        elif self.background_type == "toxic":
            return {
                "stars": (200, 255, 150),
                "dust": (100, 200, 50, 50),  # Green toxic field
                "accent": (100, 255, 50)
            }
        else:  # default space
            return {
                "stars": (255, 255, 255),
                "dust": (50, 50, 100, 30),  # Dark blue space
                "accent": (100, 100, 200)
            }


class Campaign:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.current_sector_index = 0
        self.sectors = self.create_sectors()
        self.map_scroll_x = 0
        self.selected_sector = 0
        
        # Load fonts
        self.font_title = pygame.font.SysFont(None, 48)
        self.font_large = pygame.font.SysFont(None, 36)
        self.font_medium = pygame.font.SysFont(None, 28)
        self.font_small = pygame.font.SysFont(None, 20)
        
        # Create buttons
        self.start_button = {
            'rect': pygame.Rect(width // 2 - 100, height - 80, 200, 50),
            'text': "Start Mission",
            'hover': False
        }
        
        self.back_button = {
            'rect': pygame.Rect(50, height - 80, 150, 50),
            'text': "Back to Menu",
            'hover': False
        }
        
        # Create particle system for map
        self.particle_system = ParticleSystem()
        
        # Create background stars
        self.background_stars = []
        for _ in range(100):
            self.background_stars.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'size': random.randint(1, 3),
                'brightness': random.randint(100, 255)
            })
    
    def create_sectors(self):
        """Create all campaign sectors"""
        sectors = [
            Sector("Training Grounds", "Learn the basics of asteroid dodging", 1, "space"),
            Sector("Asteroid Belt", "Navigate through a dense asteroid field", 2, "space"),
            Sector("Nebula Cloud", "Limited visibility in a colorful nebula", 3, "nebula", "low_visibility"),
            Sector("Ice Field", "Slippery controls in an icy environment", 3, "ice", "slippery_controls"),
            Sector("Fire Sector", "Avoid solar flares and hot asteroids", 4, "fire", "solar_flares"),
            Sector("Toxic Zone", "Poisonous gas clouds slow your ship", 4, "toxic", "toxic_clouds"),
            Sector("Black Hole Cluster", "Navigate around dangerous black holes", 5, "space", "black_holes"),
            Sector("Wormhole Nexus", "Unpredictable wormholes teleport asteroids", 5, "nebula", "wormholes")
        ]
        
        # Add special mission types
        sectors[2].special_feature = "escort"  # Escort mission in Nebula Cloud
        sectors[5].special_feature = "survival"  # Survival mission in Toxic Zone
        
        return sectors
    
    def get_current_sector(self):
        """Return the currently selected sector"""
        if 0 <= self.selected_sector < len(self.sectors):
            return self.sectors[self.selected_sector]
        return None
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Check button hover
            mouse_pos = event.pos
            self.start_button['hover'] = self.start_button['rect'].collidepoint(mouse_pos)
            self.back_button['hover'] = self.back_button['rect'].collidepoint(mouse_pos)
            
            # Check sector hover
            self.check_sector_hover(mouse_pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Check start button
            if self.start_button['rect'].collidepoint(mouse_pos):
                # Can only start if the sector is available
                if self.is_sector_available(self.selected_sector):
                    return "start_mission"
            
            # Check back button
            if self.back_button['rect'].collidepoint(mouse_pos):
                return "back_to_menu"
            
            # Check sector selection
            sector_clicked = self.get_clicked_sector(mouse_pos)
            if sector_clicked is not None:
                self.selected_sector = sector_clicked
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected_sector = max(0, self.selected_sector - 1)
            elif event.key == pygame.K_RIGHT:
                self.selected_sector = min(len(self.sectors) - 1, self.selected_sector + 1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.is_sector_available(self.selected_sector):
                    return "start_mission"
            elif event.key == pygame.K_ESCAPE:
                return "back_to_menu"
        
        return None
    
    def check_sector_hover(self, mouse_pos):
        """Check if mouse is hovering over a sector"""
        for i, sector in enumerate(self.sectors):
            sector_x = 150 + i * 200 - self.map_scroll_x
            sector_y = self.height // 2
            
            # Check if mouse is over sector
            distance = math.sqrt((mouse_pos[0] - sector_x) ** 2 + (mouse_pos[1] - sector_y) ** 2)
            if distance < 50:
                self.selected_sector = i
                return
    
    def get_clicked_sector(self, mouse_pos):
        """Return the index of the clicked sector, or None"""
        for i, sector in enumerate(self.sectors):
            sector_x = 150 + i * 200 - self.map_scroll_x
            sector_y = self.height // 2
            
            # Check if mouse is over sector
            distance = math.sqrt((mouse_pos[0] - sector_x) ** 2 + (mouse_pos[1] - sector_y) ** 2)
            if distance < 50:
                return i
        
        return None
    
    def is_sector_available(self, sector_index):
        """Check if a sector is available to play"""
        # First sector is always available
        if sector_index == 0:
            return True
        
        # Other sectors require previous sector to be completed
        return self.sectors[sector_index - 1].completed
    
    def update(self, dt):
        # Adjust map scroll to keep selected sector visible
        target_scroll_x = max(0, self.selected_sector * 200 - self.width // 2 + 150)
        self.map_scroll_x += (target_scroll_x - self.map_scroll_x) * 0.1
        
        # Update particle effects
        self.particle_system.update(dt)
        
        # Create ambient particles
        if random.random() < 0.05:
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            color = (100, 100, 200)
            self.particle_system.create_ambient_particle(x, y, color)
    
    def complete_sector(self, sector_index, stars):
        """Mark a sector as completed with a star rating"""
        if 0 <= sector_index < len(self.sectors):
            self.sectors[sector_index].completed = True
            self.sectors[sector_index].stars = stars
            
            # Automatically select the next sector if available
            if sector_index + 1 < len(self.sectors):
                self.selected_sector = sector_index + 1
    
    def draw(self, screen):
        # Draw background
        screen.fill((0, 0, 20))
        
        # Draw stars
        for star in self.background_stars:
            pygame.draw.circle(screen, (star['brightness'], star['brightness'], star['brightness']), 
                              (star['x'], star['y']), star['size'])
        
        # Draw particles
        self.particle_system.draw(screen)
        
        # Draw campaign title
        title_text = self.font_title.render("CAMPAIGN MODE", True, (255, 255, 255))
        screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 50))
        
        # Draw sector map
        self.draw_sector_map(screen)
        
        # Draw selected sector details
        self.draw_sector_details(screen)
        
        # Draw buttons
        self.draw_buttons(screen)
    
    def draw_sector_map(self, screen):
        # Draw connecting lines between sectors
        for i in range(len(self.sectors) - 1):
            start_x = 150 + i * 200 - self.map_scroll_x
            end_x = 150 + (i + 1) * 200 - self.map_scroll_x
            y = self.height // 2
            
            # Line color based on completion
            if self.sectors[i].completed:
                line_color = (100, 255, 100)  # Green if completed
            else:
                line_color = (100, 100, 100)  # Gray if not completed
            
            pygame.draw.line(screen, line_color, (start_x, y), (end_x, y), 3)
        
        # Draw each sector
        for i, sector in enumerate(self.sectors):
            x = 150 + i * 200 - self.map_scroll_x
            y = self.height // 2
            
            # Skip if off screen
            if x + 50 < 0 or x - 50 > self.width:
                continue
            
            # Determine sector color based on status
            if i == self.selected_sector:
                outer_color = (255, 255, 0)  # Yellow for selected
                inner_color = (100, 100, 0)
            elif sector.completed:
                outer_color = (0, 255, 0)  # Green for completed
                inner_color = (0, 100, 0)
            elif self.is_sector_available(i):
                outer_color = (0, 150, 255)  # Blue for available
                inner_color = (0, 50, 100)
            else:
                outer_color = (100, 100, 100)  # Gray for locked
                inner_color = (50, 50, 50)
            
            # Draw sector circle
            pygame.draw.circle(screen, inner_color, (int(x), int(y)), 40)
            pygame.draw.circle(screen, outer_color, (int(x), int(y)), 40, 3)
            
            # Draw sector number
            num_text = self.font_large.render(str(i + 1), True, (255, 255, 255))
            screen.blit(num_text, (x - num_text.get_width() // 2, y - num_text.get_height() // 2))
            
            # Draw stars if completed
            if sector.completed:
                for j in range(3):
                    star_color = (255, 255, 0) if j < sector.stars else (100, 100, 100)
                    star_x = x - 20 + j * 20
                    star_y = y + 30
                    
                    # Draw a simple star
                    points = []
                    for k in range(5):
                        angle = math.pi / 2 + k * 2 * math.pi / 5
                        points.append((star_x + math.cos(angle) * 8, star_y + math.sin(angle) * 8))
                        angle += math.pi / 5
                        points.append((star_x + math.cos(angle) * 4, star_y + math.sin(angle) * 4))
                    
                    pygame.draw.polygon(screen, star_color, points)
    
    def draw_sector_details(self, screen):
        sector = self.get_current_sector()
        if sector:
            # Draw sector name
            name_text = self.font_large.render(sector.name, True, (255, 255, 255))
            screen.blit(name_text, (self.width // 2 - name_text.get_width() // 2, self.height - 200))
            
            # Draw sector description
            desc_text = self.font_medium.render(sector.description, True, (200, 200, 200))
            screen.blit(desc_text, (self.width // 2 - desc_text.get_width() // 2, self.height - 160))
            
            # Draw difficulty
            diff_text = self.font_medium.render(f"Difficulty: {'★' * sector.difficulty}", True, (255, 200, 0))
            screen.blit(diff_text, (self.width // 2 - diff_text.get_width() // 2, self.height - 130))
            
            # Draw special feature if any
            if sector.special_feature:
                feature_name = sector.special_feature.replace('_', ' ').title()
                feature_text = self.font_medium.render(f"Special: {feature_name}", True, (0, 200, 255))
                screen.blit(feature_text, (self.width // 2 - feature_text.get_width() // 2, self.height - 100))
    
    def draw_buttons(self, screen):
        # Draw start button
        start_color = (0, 200, 0) if self.start_button['hover'] and self.is_sector_available(self.selected_sector) else (0, 100, 0)
        if not self.is_sector_available(self.selected_sector):
            start_color = (100, 100, 100)  # Gray if not available
            
        pygame.draw.rect(screen, start_color, self.start_button['rect'])
        pygame.draw.rect(screen, (100, 255, 100), self.start_button['rect'], 2)
        
        start_text = self.font_medium.render(self.start_button['text'], True, (255, 255, 255))
        start_text_rect = start_text.get_rect(center=self.start_button['rect'].center)
        screen.blit(start_text, start_text_rect)
        
        # Draw back button
        back_color = (200, 0, 0) if self.back_button['hover'] else (100, 0, 0)
        pygame.draw.rect(screen, back_color, self.back_button['rect'])
        pygame.draw.rect(screen, (255, 100, 100), self.back_button['rect'], 2)
        
        back_text = self.font_medium.render(self.back_button['text'], True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=self.back_button['rect'].center)
        screen.blit(back_text, back_text_rect)
