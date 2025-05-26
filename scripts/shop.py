import pygame
import math

class ShopItem:
    def __init__(self, name, description, cost, max_level, current_level=0):
        self.name = name
        self.description = description
        self.base_cost = cost
        self.max_level = max_level
        self.current_level = current_level
    
    def get_cost(self):
        """Calculate cost based on current level"""
        return self.base_cost * (self.current_level + 1)
    
    def can_upgrade(self, points):
        """Check if player has enough points and item is not maxed"""
        return (self.current_level < self.max_level and 
                points >= self.get_cost())
    
    def upgrade(self):
        """Upgrade the item and return the cost"""
        if self.current_level < self.max_level:
            cost = self.get_cost()
            self.current_level += 1
            return cost
        return 0


class Shop:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Shop state
        self.active = False
        self.selected_item = 0
        self.points = 0
        self.wave = 1
        
        # Load fonts
        self.font_title = pygame.font.SysFont(None, 48)
        self.font_large = pygame.font.SysFont(None, 36)
        self.font_medium = pygame.font.SysFont(None, 28)
        self.font_small = pygame.font.SysFont(None, 20)
        
        # Create shop items
        self.items = [
            ShopItem("Ship Speed", "Increases maximum ship speed", 500, 5),
            ShopItem("Weapon Damage", "Increases damage dealt to asteroids", 600, 5),
            ShopItem("Shield Capacity", "Increases shield duration", 700, 3),
            ShopItem("Extra Life", "Adds an additional life", 1000, 2),
            ShopItem("Spread Shot", "Unlocks spread shot weapon", 1500, 1),
            ShopItem("Homing Missiles", "Unlocks homing missile weapon", 2000, 1),
            ShopItem("Rapid Fire", "Decreases weapon cooldown", 800, 3),
            ShopItem("Fuel Efficiency", "Increases thruster efficiency", 400, 3)
        ]
        
        # Create buttons
        self.continue_button = {
            'rect': pygame.Rect(width // 2 - 100, height - 80, 200, 50),
            'text': "Continue to Wave " + str(self.wave + 1),
            'hover': False
        }
        
        # Debug flag
        self.debug_mode = True
    
    def set_points(self, points):
        """Set available points for shopping"""
        self.points = points
    
    def set_wave(self, wave):
        """Set the current wave number"""
        self.wave = wave
        self.continue_button['text'] = f"Continue to Wave {wave + 1}"
    
    def handle_event(self, event):
        if not self.active:
            return None
        
        if event.type == pygame.MOUSEMOTION:
            # Check item hover
            mouse_pos = event.pos
            self.check_hover(mouse_pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check item selection and purchase
            mouse_pos = event.pos
            
            # Check if continue button was clicked
            if self.continue_button['rect'].collidepoint(mouse_pos):
                return "continue"
            
            # Check if an item was clicked
            item_clicked = self.get_clicked_item(mouse_pos)
            if item_clicked is not None:
                self.selected_item = item_clicked
                
                # Check for purchase (right side of item)
                if self.is_buy_button_clicked(mouse_pos, item_clicked):
                    self.purchase_item(item_clicked)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.items)
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.items)
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.purchase_item(self.selected_item)
            elif event.key == pygame.K_ESCAPE:
                return "continue"
            # Debug: Force continue with F5
            elif event.key == pygame.K_F5:
                print("Debug: Forcing continue to next wave")
                return "continue"
        
        return None
    
    def check_hover(self, mouse_pos):
        """Check if mouse is hovering over items or buttons"""
        # Check continue button
        self.continue_button['hover'] = self.continue_button['rect'].collidepoint(mouse_pos)
    
    def get_clicked_item(self, mouse_pos):
        """Return the index of the clicked item, or None"""
        item_height = 60
        item_start_y = 150
        
        for i in range(len(self.items)):
            item_y = item_start_y + i * item_height
            item_rect = pygame.Rect(100, item_y, self.width - 200, item_height)
            
            if item_rect.collidepoint(mouse_pos):
                return i
        
        return None
    
    def is_buy_button_clicked(self, mouse_pos, item_index):
        """Check if the buy button for an item was clicked"""
        item_height = 60
        item_start_y = 150
        item_y = item_start_y + item_index * item_height
        
        buy_button_rect = pygame.Rect(self.width - 150, item_y + 15, 100, 30)
        return buy_button_rect.collidepoint(mouse_pos)
    
    def purchase_item(self, item_index):
        """Attempt to purchase the selected item"""
        item = self.items[item_index]
        
        if item.can_upgrade(self.points):
            cost = item.upgrade()
            self.points -= cost
            return True
        
        return False
    
    def get_upgrades(self):
        """Return a dictionary of all upgrades and their levels"""
        upgrades = {}
        for item in self.items:
            upgrades[item.name] = item.current_level
        return upgrades
    
    def draw(self, screen):
        if not self.active:
            return
        
        print("Drawing shop screen")
        
        # Draw semi-transparent background
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Draw shop title
        title_text = self.font_title.render("UPGRADE SHOP", True, (255, 255, 255))
        screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 50))
        
        # Draw available points
        points_text = self.font_large.render(f"Available Points: {self.points}", True, (255, 255, 0))
        screen.blit(points_text, (self.width // 2 - points_text.get_width() // 2, 100))
        
        # Draw items
        self.draw_items(screen)
        
        # Draw continue button
        self.draw_continue_button(screen)
    
    def draw_items(self, screen):
        item_height = 60
        item_start_y = 150
        
        for i, item in enumerate(self.items):
            item_y = item_start_y + i * item_height
            
            # Highlight selected item
            if i == self.selected_item:
                pygame.draw.rect(screen, (50, 50, 80), 
                                (100, item_y, self.width - 200, item_height))
                pygame.draw.rect(screen, (100, 100, 150), 
                                (100, item_y, self.width - 200, item_height), 2)
            else:
                pygame.draw.rect(screen, (30, 30, 50), 
                                (100, item_y, self.width - 200, item_height))
                pygame.draw.rect(screen, (70, 70, 100), 
                                (100, item_y, self.width - 200, item_height), 1)
            
            # Draw item name
            name_text = self.font_medium.render(item.name, True, (255, 255, 255))
            screen.blit(name_text, (120, item_y + 10))
            
            # Draw item level
            level_text = self.font_small.render(f"Level: {item.current_level}/{item.max_level}", 
                                              True, (200, 200, 200))
            screen.blit(level_text, (120, item_y + 35))
            
            # Draw item description
            desc_text = self.font_small.render(item.description, True, (200, 200, 200))
            screen.blit(desc_text, (300, item_y + 20))
            
            # Draw buy button
            buy_color = (0, 200, 0) if item.can_upgrade(self.points) else (100, 100, 100)
            pygame.draw.rect(screen, buy_color, (self.width - 150, item_y + 15, 100, 30))
            
            cost_text = self.font_small.render(f"Buy: {item.get_cost()}", True, (255, 255, 255))
            screen.blit(cost_text, (self.width - 140, item_y + 20))
    
    def draw_continue_button(self, screen):
        # Draw button
        button_color = (0, 150, 200) if self.continue_button['hover'] else (0, 100, 150)
        pygame.draw.rect(screen, button_color, self.continue_button['rect'])
        pygame.draw.rect(screen, (100, 200, 255), self.continue_button['rect'], 2)
        
        # Draw text
        text = self.font_medium.render(self.continue_button['text'], True, (255, 255, 255))
        text_rect = text.get_rect(center=self.continue_button['rect'].center)
        screen.blit(text, text_rect)
