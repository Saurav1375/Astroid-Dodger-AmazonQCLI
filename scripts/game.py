import pygame
import random
import math
from .player import Player
from .asteroid import Asteroid
from .powerup import PowerUp
from .particle import ParticleSystem
from .starfield import Starfield
from .hud import HUD
from .weapon import Weapon
from .sound_manager import SoundManager
from .enemy import HomingMissile, SpinningBlade, CrystalAsteroid
from .boss import Boss
from .hazard import BlackHole, SpaceStorm, Wormhole
from .shop import Shop

class Game:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        
        # Load game assets
        self.load_assets()
        
        # Create game objects
        self.reset()
    
    def load_assets(self):
        # Initialize sound manager
        self.sound_manager = SoundManager()
        
        # Load images and other assets here
        # This would typically load sprites for the player, asteroids, etc.
        
        # Create shop system
        self.shop = Shop(self.width, self.height)
        
    def reset(self):
        # Create the player
        self.player = Player(self.width // 2, self.height // 2, self.width, self.height)
        
        # Create the weapon system
        self.weapon = Weapon(self.sound_manager)
        
        # Create the starfield background
        self.starfield = Starfield(self.width, self.height, 100)
        
        # Create the particle system
        self.particle_system = ParticleSystem()
        
        # Create the HUD
        self.hud = HUD(self.width, self.height)
        
        # Game state variables
        self.asteroids = []
        self.powerups = []
        self.projectiles = []
        self.enemies = []  # New enemies list (homing missiles, etc.)
        self.hazards = []  # Environmental hazards
        self.boss = None   # Current boss (if any)
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.wave = 1
        self.wave_timer = 0
        self.wave_completed = False
        self.wave_transition_timer = 0
        self.game_over = False
        self.paused = False
        self.shop_active = False
        
        # Game mode
        self.game_mode = "arcade"  # "arcade" or "campaign"
        self.current_sector = None
        self.mission_type = "standard"  # "standard", "escort", "survival"
        self.mission_timer = 0
        self.mission_target = None
        
        # Difficulty settings
        self.asteroid_spawn_rate = 2.0  # seconds
        self.asteroid_spawn_timer = 0
        self.max_asteroids = 10
        self.boss_wave_interval = 5
        
        # Power-up settings
        self.powerup_spawn_rate = 15.0  # seconds
        self.powerup_spawn_timer = 0
        
        # Active power-ups
        self.active_powerups = {
            "shield": 0,
            "rapid_fire": 0,
            "slow_motion": 0,
            "size_shrink": 0
        }
        
        # Upgrades from shop
        self.upgrades = {
            "Ship Speed": 0,
            "Weapon Damage": 0,
            "Shield Capacity": 0,
            "Extra Life": 0,
            "Spread Shot": 0,
            "Homing Missiles": 0,
            "Rapid Fire": 0,
            "Fuel Efficiency": 0
        }
        
        # Apply initial upgrades to player
        self.apply_upgrades()
        
        # Spawn initial asteroids
        for _ in range(5):
            self.spawn_asteroid()
    
    def handle_event(self, event):
        # Handle shop events if shop is active
        if self.shop_active:
            shop_action = self.shop.handle_event(event)
            if shop_action == "continue":
                self.shop_active = False
                self.start_next_wave()
                self.apply_upgrades()
            return None
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "pause"
            elif event.key == pygame.K_SPACE:
                self.fire_weapon()
        
        # Let the player handle its own input
        self.player.handle_input(event)
        
        return None
    
    def update(self):
        if self.game_over:
            return "game_over"
            
        # If shop is active, only update shop
        if self.shop_active:
            return None
        
        # Calculate delta time (in seconds)
        dt = 1 / 60  # Assuming 60 FPS
        
        # Apply slow motion if active
        if self.active_powerups["slow_motion"] > 0:
            dt *= 0.5
            self.active_powerups["slow_motion"] -= dt
        
        # Update timers
        self.update_timers(dt)
        
        # Update player
        self.player.update(dt)
        
        # Update weapon and projectiles
        self.update_weapons(dt)
        
        # Spawn and update asteroids
        self.update_asteroids(dt)
        
        # Spawn and update enemies
        self.update_enemies(dt)
        
        # Update boss if present
        self.update_boss(dt)
        
        # Spawn and update power-ups
        self.update_powerups(dt)
        
        # Update environmental hazards
        self.update_hazards(dt)
        
        # Update particle effects
        self.particle_system.update(dt)
        
        # Update starfield
        self.starfield.update(dt)
        
        # Check for collisions
        self.check_collisions()
        
        # Count remaining enemies
        enemies_remaining = len(self.asteroids) + len(self.enemies)
        if self.boss:
            enemies_remaining += 1
        
        # Update HUD
        self.hud.update(self.player.health, self.score, self.wave, self.active_powerups, enemies_remaining)
        
        # Debug: Force wave completion if F10 is pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_F10]:
            print("DEBUG: Force completing wave")
            self.asteroids.clear()
            self.enemies.clear()
            self.boss = None
            self.wave_completed = True
            self.wave_transition_timer = 3.0
        
        # Check if wave is completed
        if self.wave_completed:
            self.wave_transition_timer -= dt
            if self.wave_transition_timer <= 0:
                self.show_shop()
                # Force a key press to ensure the shop is shown
                if not self.shop_active:
                    print("ERROR: Shop not showing, forcing activation")
                    self.shop_active = True
                    self.shop.active = True
            return None
        
        # Check if game is over
        if self.player.health <= 0:
            self.game_over = True
            return "game_over"
        
        # Check mission objectives
        self.check_mission_objectives(dt)
        
        return None
    
    def update_timers(self, dt):
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= dt
        else:
            self.combo = 0
        
        # Update wave timer
        self.wave_timer += dt
        
        # Check for wave completion
        if not self.wave_completed:
            if self.is_wave_completed():
                print(f"Wave {self.wave} completed! Timer: {self.wave_timer:.1f}s")
                self.wave_completed = True
                self.wave_transition_timer = 3.0  # 3 seconds before showing shop
                
                # Play wave complete sound
                self.sound_manager.play_sound("wave")
                
                # Clear any remaining asteroids and enemies
                self.asteroids.clear()
                self.enemies.clear()
        
        # Update power-up timers
        for powerup in list(self.active_powerups.keys()):
            if self.active_powerups[powerup] > 0:
                self.active_powerups[powerup] -= dt
    
    def is_wave_completed(self):
        """Check if the current wave is completed"""
        # For boss waves, check if boss is defeated
        if self.wave % self.boss_wave_interval == 0:
            return self.boss is None
            
        # Force completion after 60 seconds
        if self.wave_timer >= 60:
            return True
            
        # For standard waves, check if all asteroids and enemies are cleared
        # Also require at least 10 seconds to have passed in the wave
        return len(self.asteroids) == 0 and len(self.enemies) == 0 and self.wave_timer >= 10.0
    
    def show_shop(self):
        """Show the shop between waves"""
        print("Opening shop...")
        self.shop_active = True
        self.shop.active = True  # Make sure the shop knows it's active
        self.shop.set_points(self.score)
        self.shop.set_wave(self.wave)
    
    def start_next_wave(self):
        """Start the next wave after shopping"""
        self.wave += 1
        self.wave_timer = 0
        self.wave_completed = False
        
        # Increase difficulty
        self.asteroid_spawn_rate = max(0.5, self.asteroid_spawn_rate * 0.9)
        self.max_asteroids += 2
        
        # Check if it's a boss wave
        if self.wave % self.boss_wave_interval == 0:
            self.spawn_boss()
        else:
            # Spawn initial asteroids for the new wave
            for _ in range(5):
                self.spawn_asteroid()
                
        print(f"Starting Wave {self.wave}")
    
    def apply_upgrades(self):
        """Apply purchased upgrades to the player and weapons"""
        # Ship speed upgrade
        speed_level = self.upgrades.get("Ship Speed", 0)
        self.player.max_speed = 5 + speed_level * 0.5
        
        # Weapon damage upgrade
        # This will be applied when creating projectiles
        
        # Shield capacity upgrade
        shield_level = self.upgrades.get("Shield Capacity", 0)
        # Will be applied when activating shield powerup
        
        # Extra life upgrade
        extra_lives = self.upgrades.get("Extra Life", 0)
        self.player.health = min(3 + extra_lives, self.player.health)
        
        # Rapid fire upgrade
        rapid_fire_level = self.upgrades.get("Rapid Fire", 0)
        self.weapon.cooldown_time = 0.25 * (1 - rapid_fire_level * 0.15)
        
        # Fuel efficiency upgrade
        fuel_level = self.upgrades.get("Fuel Efficiency", 0)
        self.player.friction = 0.98 + fuel_level * 0.005
    
    def update_weapons(self, dt):
        # Update weapon cooldown
        self.weapon.update(dt)
        
        # Update existing projectiles
        for proj in list(self.projectiles):
            proj.update(dt)
            if proj.is_offscreen(self.width, self.height):
                self.projectiles.remove(proj)
    
    def update_asteroids(self, dt):
        # Don't spawn new asteroids if wave is completed
        if self.wave_completed:
            return
            
        # Spawn new asteroids
        self.asteroid_spawn_timer += dt
        if (self.asteroid_spawn_timer >= self.asteroid_spawn_rate and 
                len(self.asteroids) < self.max_asteroids):
            self.spawn_asteroid()
            self.asteroid_spawn_timer = 0
        
        # Update existing asteroids
        for asteroid in list(self.asteroids):
            asteroid.update(dt)
            if asteroid.is_offscreen(self.width, self.height, buffer=100):
                self.asteroids.remove(asteroid)
        
        # Force wave completion after 60 seconds
        if self.wave_timer > 60 and not self.wave_completed:
            print("Forcing wave completion due to time limit")
            self.wave_completed = True
            self.wave_transition_timer = 3.0
            self.sound_manager.play_sound("wave")
    
    def update_enemies(self, dt):
        """Update special enemies like homing missiles"""
        # Don't spawn new enemies if wave is completed
        if self.wave_completed:
            return
            
        # Spawn new enemies occasionally based on wave number
        if random.random() < 0.005 * self.wave and len(self.enemies) < self.wave:
            self.spawn_enemy()
        
        # Update existing enemies
        for enemy in list(self.enemies):
            # For homing missiles, pass the player as target
            if isinstance(enemy, HomingMissile):
                if enemy.update(dt, self.particle_system):
                    self.enemies.remove(enemy)
            else:
                enemy.update(dt)
                if enemy.is_offscreen(self.width, self.height, buffer=100):
                    self.enemies.remove(enemy)
    
    def update_boss(self, dt):
        """Update boss if present"""
        if self.boss:
            # Update boss and get any new objects it creates
            new_objects = self.boss.update(dt, self.player, self.particle_system)
            
            # Add any new objects to the game
            if new_objects:
                for obj in new_objects:
                    if isinstance(obj, HomingMissile):
                        self.enemies.append(obj)
    
    def update_hazards(self, dt):
        """Update environmental hazards"""
        # Update existing hazards
        for hazard in list(self.hazards):
            if isinstance(hazard, BlackHole):
                # Black holes affect all objects
                game_objects = self.asteroids + self.enemies + [self.player]
                hazard.update(dt, game_objects)
                if not hazard.active:
                    self.hazards.remove(hazard)
                    
            elif isinstance(hazard, SpaceStorm):
                hazard.update(dt)
                if not hazard.active:
                    self.hazards.remove(hazard)
                    
            elif isinstance(hazard, Wormhole):
                hazard.update(dt, self.asteroids)
                if not hazard.active:
                    self.hazards.remove(hazard)
        
        # Spawn new hazards occasionally based on wave and sector
        if self.game_mode == "campaign" and self.current_sector:
            if self.current_sector.special_feature == "black_holes":
                if random.random() < 0.001 * self.wave and len(self.hazards) < 2:
                    self.spawn_black_hole()
                    
            elif self.current_sector.special_feature == "wormholes":
                if random.random() < 0.001 * self.wave and len(self.hazards) < 2:
                    self.spawn_wormhole()
                    
            elif self.current_sector.special_feature == "space_storm":
                if not any(isinstance(h, SpaceStorm) for h in self.hazards) and random.random() < 0.0005 * self.wave:
                    self.spawn_space_storm()
    
    def update_powerups(self, dt):
        # Spawn new power-ups
        self.powerup_spawn_timer += dt
        if self.powerup_spawn_timer >= self.powerup_spawn_rate:
            self.spawn_powerup()
            self.powerup_spawn_timer = 0
        
        # Update existing power-ups
        for powerup in list(self.powerups):
            powerup.update(dt)
            if powerup.is_offscreen(self.width, self.height):
                self.powerups.remove(powerup)
    
    def spawn_asteroid(self):
        # Determine asteroid type
        asteroid_types = ["small", "medium", "large"]
        weights = [0.4, 0.4, 0.2]  # 40% small, 40% medium, 20% large
        
        # Add special types based on wave
        if self.wave >= 3:
            asteroid_types.append("crystal")
            weights.append(0.1)
            
        if self.wave >= 5:
            asteroid_types.append("blade")
            weights.append(0.1)
            
        # Adjust weights to sum to 1
        total = sum(weights)
        weights = [w/total for w in weights]
        
        asteroid_type = random.choices(asteroid_types, weights=weights)[0]
        
        # Check for boss wave
        if self.wave % self.boss_wave_interval == 0:
            # Don't spawn regular asteroids on boss waves
            return
        
        # Determine spawn position (from outside the screen)
        side = random.choice(["top", "right", "bottom", "left"])
        if side == "top":
            x = random.randint(0, self.width)
            y = -50
            angle = random.uniform(math.pi / 4, 3 * math.pi / 4)
        elif side == "right":
            x = self.width + 50
            y = random.randint(0, self.height)
            angle = random.uniform(3 * math.pi / 4, 5 * math.pi / 4)
        elif side == "bottom":
            x = random.randint(0, self.width)
            y = self.height + 50
            angle = random.uniform(5 * math.pi / 4, 7 * math.pi / 4)
        else:  # left
            x = -50
            y = random.randint(0, self.height)
            angle = random.uniform(7 * math.pi / 4, 9 * math.pi / 4)
        
        # Create the asteroid
        if asteroid_type == "crystal":
            asteroid = CrystalAsteroid(x, y, self.wave)
        elif asteroid_type == "blade":
            asteroid = SpinningBlade(x, y, self.wave)
        else:
            asteroid = Asteroid(x, y, asteroid_type, angle, self.wave)
            
        # Make sure the asteroid is moving toward the screen
        if side == "top" and asteroid.angle > math.pi:
            asteroid.angle = random.uniform(math.pi / 4, 3 * math.pi / 4)
        elif side == "right" and (asteroid.angle < math.pi/2 or asteroid.angle > 3*math.pi/2):
            asteroid.angle = random.uniform(3 * math.pi / 4, 5 * math.pi / 4)
        elif side == "bottom" and asteroid.angle < math.pi:
            asteroid.angle = random.uniform(5 * math.pi / 4, 7 * math.pi / 4)
        elif side == "left" and (asteroid.angle > math.pi/2 and asteroid.angle < 3*math.pi/2):
            asteroid.angle = random.uniform(7 * math.pi / 4, 9 * math.pi / 4)
            
        self.asteroids.append(asteroid)
    
    def spawn_enemy(self):
        """Spawn a special enemy"""
        # Only spawn homing missiles after wave 3
        if self.wave < 3:
            return
            
        # Create a homing missile targeting the player
        side = random.choice(["top", "right", "bottom", "left"])
        if side == "top":
            x = random.randint(0, self.width)
            y = -50
        elif side == "right":
            x = self.width + 50
            y = random.randint(0, self.height)
        elif side == "bottom":
            x = random.randint(0, self.width)
            y = self.height + 50
        else:  # left
            x = -50
            y = random.randint(0, self.height)
            
        missile = HomingMissile(x, y, self.player, self.wave)
        self.enemies.append(missile)
    
    def spawn_boss(self):
        """Spawn a boss for the current wave"""
        # Create boss at the top of the screen
        self.boss = Boss(self.width // 2, 100, self.wave, self.width, self.height)
        
        # Play boss music/sound
        self.sound_manager.play_sound("wave")
    
    def spawn_black_hole(self):
        """Spawn a black hole hazard"""
        # Spawn away from the player
        min_distance = 200
        while True:
            x = random.randint(100, self.width - 100)
            y = random.randint(100, self.height - 100)
            
            # Check distance from player
            dx = x - self.player.x
            dy = y - self.player.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > min_distance:
                break
                
        black_hole = BlackHole(x, y)
        self.hazards.append(black_hole)
    
    def spawn_wormhole(self):
        """Spawn a pair of connected wormholes"""
        # Spawn entry point
        x1 = random.randint(100, self.width - 100)
        y1 = random.randint(100, self.height - 100)
        
        # Spawn exit point away from entry
        while True:
            x2 = random.randint(100, self.width - 100)
            y2 = random.randint(100, self.height - 100)
            
            # Check distance between points
            dx = x2 - x1
            dy = y2 - y1
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 200:
                break
                
        wormhole = Wormhole(x1, y1, x2, y2)
        self.hazards.append(wormhole)
    
    def spawn_space_storm(self):
        """Spawn a space storm that covers the screen"""
        storm = SpaceStorm(self.width, self.height)
        self.hazards.append(storm)
    
    def spawn_powerup(self):
        # Determine power-up type
        powerup_type = random.choice(["shield", "rapid_fire", "slow_motion", "size_shrink"])
        
        # Determine spawn position (random on screen)
        x = random.randint(50, self.width - 50)
        y = random.randint(50, self.height - 50)
        
        # Create the power-up
        powerup = PowerUp(x, y, powerup_type)
        self.powerups.append(powerup)
    
    def fire_weapon(self):
        if self.active_powerups["rapid_fire"] > 0:
            projectiles = self.weapon.fire_rapid(self.player.x, self.player.y, self.player.angle)
        else:
            projectiles = self.weapon.fire_normal(self.player.x, self.player.y, self.player.angle)
        
        self.projectiles.extend(projectiles)
    
    def check_collisions(self):
        # Player-Asteroid collisions
        player_radius = self.player.get_collision_radius()
        if self.active_powerups["size_shrink"] > 0:
            player_radius *= 0.5
        
        for asteroid in list(self.asteroids):
            # Check if player has shield
            if self.active_powerups["shield"] > 0:
                shield_radius = player_radius * 1.5
                if self.check_circle_collision(self.player.x, self.player.y, shield_radius,
                                             asteroid.x, asteroid.y, asteroid.radius):
                    # Shield blocks asteroid
                    self.destroy_asteroid(asteroid)
                    continue
            
            # Check player collision
            if not self.player.invulnerable and self.check_circle_collision(
                    self.player.x, self.player.y, player_radius,
                    asteroid.x, asteroid.y, asteroid.radius):
                self.player.take_damage()
                self.combo = 0
                self.sound_manager.play_sound("player_hit")
                
                # Create explosion particles
                self.particle_system.create_explosion(self.player.x, self.player.y, (255, 200, 0))
                
                # Remove the asteroid
                self.asteroids.remove(asteroid)
        
        # Projectile-Asteroid collisions
        for proj in list(self.projectiles):
            for asteroid in list(self.asteroids):
                if self.check_circle_collision(proj.x, proj.y, proj.radius,
                                             asteroid.x, asteroid.y, asteroid.radius):
                    # Hit asteroid
                    self.destroy_asteroid(asteroid)
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                    break
        
        # Player-PowerUp collisions
        for powerup in list(self.powerups):
            if self.check_circle_collision(self.player.x, self.player.y, player_radius,
                                         powerup.x, powerup.y, powerup.radius):
                # Activate power-up
                self.activate_powerup(powerup.type)
                self.powerups.remove(powerup)
                self.sound_manager.play_sound("powerup")
    
    def check_circle_collision(self, x1, y1, r1, x2, y2, r2):
        # Check if two circles are colliding
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return distance < (r1 + r2)
    
    def destroy_asteroid(self, asteroid):
        # Remove the asteroid
        if asteroid in self.asteroids:
            self.asteroids.remove(asteroid)
        
        # Create explosion particles
        self.particle_system.create_explosion(asteroid.x, asteroid.y, asteroid.color)
        
        # Play sound
        self.sound_manager.play_sound("explosion")
        
        # Add score based on asteroid type
        points = {
            "small": 100,
            "medium": 50,
            "large": 25,
            "boss": 500
        }
        base_points = points.get(asteroid.type, 50)
        
        # Apply combo multiplier
        self.combo += 1
        self.combo_timer = 3.0  # Reset combo timer (3 seconds)
        combo_multiplier = min(5, 1 + (self.combo - 1) * 0.1)  # Max 5x multiplier
        
        # Add score
        score_gain = int(base_points * combo_multiplier)
        self.score += score_gain
        
        # Spawn smaller asteroids if it was a large or medium one
        if asteroid.type == "large":
            for _ in range(2):
                new_asteroid = Asteroid(
                    asteroid.x + random.uniform(-20, 20),
                    asteroid.y + random.uniform(-20, 20),
                    "medium",
                    random.uniform(0, 2 * math.pi),
                    self.wave
                )
                self.asteroids.append(new_asteroid)
        elif asteroid.type == "medium":
            for _ in range(2):
                new_asteroid = Asteroid(
                    asteroid.x + random.uniform(-10, 10),
                    asteroid.y + random.uniform(-10, 10),
                    "small",
                    random.uniform(0, 2 * math.pi),
                    self.wave
                )
                self.asteroids.append(new_asteroid)
    
    def activate_powerup(self, powerup_type):
        # Set duration based on power-up type
        durations = {
            "shield": 10.0,
            "rapid_fire": 8.0,
            "slow_motion": 5.0,
            "size_shrink": 15.0
        }
        
        # Activate the power-up
        self.active_powerups[powerup_type] = durations.get(powerup_type, 10.0)
    
    def check_mission_objectives(self, dt):
        """Check and update mission objectives for campaign mode"""
        if self.game_mode != "campaign":
            return
            
        # Update mission timer
        self.mission_timer += dt
        
        # Handle different mission types
        if self.mission_type == "escort":
            # Update escort target
            if self.mission_target:
                # Move escort target
                self.mission_target.update(dt)
                
                # Check if escort target is destroyed
                if self.mission_target.health <= 0:
                    self.game_over = True
                    
                # Check if escort mission is complete (reached destination)
                if self.mission_target.reached_destination:
                    self.wave_completed = True
                    self.wave_transition_timer = 3.0
                    
        elif self.mission_type == "survival":
            # Check if survival time is reached
            survival_time = 60.0  # 60 seconds
            if self.mission_timer >= survival_time:
                self.wave_completed = True
                self.wave_transition_timer = 3.0
    
    def set_campaign_mission(self, sector):
        """Set up a campaign mission based on the sector"""
        self.current_sector = sector
        self.game_mode = "campaign"
        
        # Set mission type based on sector
        if sector.special_feature == "escort":
            self.mission_type = "escort"
            self.setup_escort_mission()
        elif sector.special_feature == "survival":
            self.mission_type = "survival"
            self.mission_timer = 0
        else:
            self.mission_type = "standard"
        
        # Apply sector-specific settings
        asteroid_props = sector.get_asteroid_properties()
        self.asteroid_spawn_rate *= asteroid_props["spawn_rate_multiplier"]
        
        # Set background colors based on sector
        bg_colors = sector.get_background_colors()
        self.starfield.set_colors(bg_colors["stars"], bg_colors["dust"])
    
    def setup_escort_mission(self):
        """Set up an escort mission with a target to protect"""
        from .escort_target import EscortTarget
        
        # Create escort target at the left side of the screen
        self.mission_target = EscortTarget(50, self.height // 2, self.width - 100, self.height // 2)
        
        # Reset mission timer
        self.mission_timer = 0
    
    def draw(self):
        # Clear the screen
        self.screen.fill((0, 0, 0))
        
        # Draw the starfield background
        self.starfield.draw(self.screen)
        
        # Draw environmental hazards
        for hazard in self.hazards:
            hazard.draw(self.screen)
        
        # Draw particles
        self.particle_system.draw(self.screen)
        
        # Draw projectiles
        for proj in self.projectiles:
            proj.draw(self.screen)
        
        # Draw asteroids
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw boss if present
        if self.boss:
            self.boss.draw(self.screen)
        
        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # Draw mission target if in escort mission
        if self.mission_type == "escort" and self.mission_target:
            self.mission_target.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen, self.active_powerups)
        
        # Draw HUD
        self.hud.draw(self.screen)
        
        # Draw mission info for campaign mode
        if self.game_mode == "campaign":
            self.draw_mission_info()
        
        # Draw wave completion message
        if self.wave_completed:
            self.draw_wave_complete()
        
        # Draw shop if active
        if self.shop_active:
            self.shop.draw(self.screen)
    
    def draw_mission_info(self):
        """Draw mission information for campaign mode"""
        font = pygame.font.SysFont(None, 24)
        
        # Draw sector name
        if self.current_sector:
            sector_text = font.render(f"Sector: {self.current_sector.name}", True, (200, 200, 255))
            self.screen.blit(sector_text, (20, 60))
        
        # Draw mission type
        mission_name = self.mission_type.capitalize()
        mission_text = font.render(f"Mission: {mission_name}", True, (200, 200, 255))
        self.screen.blit(mission_text, (20, 85))
        
        # Draw mission-specific info
        if self.mission_type == "survival":
            time_left = max(0, 60 - self.mission_timer)
            time_text = font.render(f"Survive: {time_left:.1f}s", True, (255, 200, 100))
            self.screen.blit(time_text, (20, 110))
    
    def draw_wave_complete(self):
        """Draw wave completion message"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((self.width, 100), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, self.height // 2 - 50))
        
        # Draw wave complete text
        font_large = pygame.font.SysFont(None, 48)
        text = font_large.render("WAVE COMPLETE!", True, (255, 255, 0))
        self.screen.blit(text, (self.width // 2 - text.get_width() // 2, self.height // 2 - 25))
        
        # Draw "Shop opening..." text
        font_medium = pygame.font.SysFont(None, 32)
        text2 = font_medium.render(f"Shop opening in {self.wave_transition_timer:.1f}s", True, (255, 255, 255))
        self.screen.blit(text2, (self.width // 2 - text2.get_width() // 2, self.height // 2 + 15))
