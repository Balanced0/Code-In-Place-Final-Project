import pygame
import sys
import math
import random
import pygame_menu

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
MENU_WIDTH = 600
MENU_HEIGHT = 400

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
DARK_GREEN = (34, 139, 34)
BROWN = (101, 67, 33)
YELLOW = (255, 255, 0)

player1_name = "Player 1"
player2_name = "Player 2"

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racing Game - Two Players")
clock = pygame.time.Clock()

class Car:
    def __init__(self, x, y, color=RED, control_key=pygame.K_w):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 36
        self.color = color
        self.angle = 270 if color == RED else 90  # Red car: 270, Yellow car: 90
        self.speed = 0
        self.max_speed = 8
        self.acceleration = 0.15
        self.deceleration = 0.08
        self.control_key = control_key
       
        self.lap_count = 0
        self.checkpoint_passed = False
        self.current_lap_time = 0
        self.best_lap_time = float('inf')
        self.lap_start_time = pygame.time.get_ticks()
        self.last_lap_time = 0
        
        self.collision_cooldown = 0
        
        self.current_track = None

    def update(self, keys, track):
        
        self.current_track = track

       
        if self.collision_cooldown > 0:
            self.collision_cooldown -= 1

   
        if self.control_key == pygame.K_w and keys[self.control_key]:
           
            self.speed += self.acceleration
            if self.speed > self.max_speed:
                self.speed = self.max_speed
        elif self.control_key == pygame.K_UP and keys[self.control_key]:
           
            self.speed -= self.acceleration
            if self.speed < -self.max_speed:
                self.speed = -self.max_speed
        else:
           
            if self.speed > 0:
                self.speed -= self.deceleration
                if self.speed < 0:
                    self.speed = 0
            elif self.speed < 0:
                self.speed += self.deceleration
                if self.speed > 0:
                    self.speed = 0

        
        angle_rad = math.radians(self.angle)
        new_x = self.x - self.speed * math.sin(angle_rad)
        new_y = self.y - self.speed * math.cos(angle_rad)

        
        strafe_speed = 3  

        if self.color == RED:  
            if keys[pygame.K_a]:  # A key for left movement
                strafe_angle = angle_rad - math.pi/2
                new_x += strafe_speed * math.sin(strafe_angle)
                new_y += strafe_speed * math.cos(strafe_angle)
            elif keys[pygame.K_d]:  # D key for right movement
                strafe_angle = angle_rad + math.pi/2
                new_x += strafe_speed * math.sin(strafe_angle)
                new_y += strafe_speed * math.cos(strafe_angle)
        else:  # Yellow car uses arrow keys
            if keys[pygame.K_LEFT]:
                strafe_angle = angle_rad - math.pi/2
                new_x += strafe_speed * math.sin(strafe_angle)
                new_y += strafe_speed * math.cos(strafe_angle)
            elif keys[pygame.K_RIGHT]:
                strafe_angle = angle_rad + math.pi/2
                new_x += strafe_speed * math.sin(strafe_angle)
                new_y += strafe_speed * math.cos(strafe_angle)

        
        if track.is_on_track(new_x, new_y):
            # Update position if on track
            self.x = new_x
            self.y = new_y

            # Check for lap completion
            if track.check_finish_line(self.x, self.y):
                if self.checkpoint_passed:
                    # Complete a lap
                    current_time = pygame.time.get_ticks()
                    lap_time = (current_time - self.lap_start_time) / 1000.0

                    # Update lap times
                    self.last_lap_time = lap_time
                    if lap_time < self.best_lap_time:
                        self.best_lap_time = lap_time

                    # Reset for next lap
                    self.lap_count += 1
                    self.checkpoint_passed = False
                    self.lap_start_time = current_time

            # Check for checkpoint
            elif track.check_checkpoint(self.x, self.y):
                self.checkpoint_passed = True

            # Auto-adjust angle to follow the track
            self.auto_adjust_angle(track)
        else:
            # Find a valid position by sliding along the track border
            self.slide_along_border(track, angle_rad)

    def auto_adjust_angle(self, track):
        # Find the best direction to follow the track
        best_distance = 0
        best_angle_offset = 0

        for angle_offset in [-5, -2, 0, 2, 5]:
            test_angle = math.radians(self.angle + angle_offset)

            
            distance = 0
            for d in range(1, 100, 5):
                # Use same calculation for both cars
                test_x = self.x - d * math.sin(test_angle)  # Always negative for clockwise
                test_y = self.y - d * math.cos(test_angle)  # Always negative for clockwise

                if track.is_on_track(test_x, test_y):
                    distance = d
                else:
                    break

            if distance > best_distance:
                best_distance = distance
                best_angle_offset = angle_offset

        # Gradually adjust angle to follow the track
        if best_angle_offset != 0:
            self.angle += best_angle_offset * 0.2

    def slide_along_border(self, track, angle_rad):
        
        test_angles = [0, 15, -15, 30, -30, 45, -45, 60, -60]

        for angle_offset in test_angles:
            test_angle = angle_rad + math.radians(angle_offset)

           
            test_x = self.x - self.speed * 0.8 * math.sin(test_angle)  # Always negative for clockwise
            test_y = self.y - self.speed * 0.8 * math.cos(test_angle)  # Always negative for clockwise

            if track.is_on_track(test_x, test_y):
                self.angle += angle_offset
                self.x = test_x
                self.y = test_y
                self.speed *= 0.9
                return

        self.speed *= 0.7

    def check_collision(self, other_car):
       
        dx = self.x - other_car.x
        dy = self.y - other_car.y
        distance = math.sqrt(dx * dx + dy * dy)

        # If distance is less than the sum of car sizes, collision occurred
        min_distance = (self.width + other_car.width) / 2
        return distance < min_distance and self.collision_cooldown == 0 and other_car.collision_cooldown == 0

    def handle_collision(self, other_car):
        # Calculate collision angle
        dx = other_car.x - self.x
        dy = other_car.y - self.y
        collision_angle = math.atan2(dy, dx)

        # Bounce effect
        bounce_factor = 0.7  # Reduce speed after collision

        # Update speeds after collision
        self.speed *= bounce_factor
        other_car.speed *= bounce_factor

        # Push cars apart to prevent sticking
        push_distance = (self.width + other_car.width) / 2
        push_x = math.cos(collision_angle) * push_distance * 0.5
        push_y = math.sin(collision_angle) * push_distance * 0.5

        # Calculate new positions
        new_self_x = self.x - push_x
        new_self_y = self.y - push_y
        new_other_x = other_car.x + push_x
        new_other_y = other_car.y + push_y

        # Only move cars if new positions are on track
        track = self.current_track  

        # Move self car only if new position is on track
        if track and track.is_on_track(new_self_x, new_self_y):
            self.x = new_self_x
            self.y = new_self_y
        else:
            
            self.speed *= 0.3

        
        if track and track.is_on_track(new_other_x, new_other_y):
            other_car.x = new_other_x
            other_car.y = new_other_y
        else:
            other_car.speed *= 0.3

       
        angle_change = random.uniform(-10, 10)  # Reduced from -20,20
        self.angle += angle_change
        other_car.angle -= angle_change

       
        self.collision_cooldown = 15
        other_car.collision_cooldown = 15

    def draw(self, surface):
        car_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        
        pygame.draw.rect(car_surface, self.color, (0, 0, self.width, self.height), border_radius=5)

       
        pygame.draw.rect(car_surface, (50, 50, 50), (4, 8, self.width-8, self.height-16), border_radius=2)

       
        pygame.draw.polygon(car_surface, (150, 220, 255), [
            (4, 8),
            (self.width-4, 8),
            (self.width-8, 16),
            (8, 16)
        ])

        
        pygame.draw.rect(car_surface, (150, 220, 255), (4, self.height-12, self.width-8, 6), border_radius=1)

       
        pygame.draw.circle(car_surface, (255, 255, 200), (6, 6), 3)
        pygame.draw.circle(car_surface, (255, 255, 200), (self.width-6, 6), 3)

       
        pygame.draw.rect(car_surface, (255, 50, 50), (3, self.height-5, 5, 3))
        pygame.draw.rect(car_surface, (255, 50, 50), (self.width-8, self.height-5, 5, 3))

        # Rotate car
        rotated_car = pygame.transform.rotate(car_surface, self.angle)
        car_rect = rotated_car.get_rect(center=(self.x, self.y))
        surface.blit(rotated_car, car_rect.topleft)

class Track:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.outer_border = []
        self.inner_border = []
        self.track_surface = None
        self.finish_line_pos = (width // 2, height // 2 - 150)
        self.generate_track()
        self.create_track_image()

    def generate_track(self):
        center_x = self.width // 2
        center_y = self.height // 2

        # Outer border
        a_outer = 300
        b_outer = 200

        # Inner border
        a_inner = 200
        b_inner = 100

        for angle in range(0, 360, 5):
            rad = math.radians(angle)

            x_outer = center_x + int(a_outer * math.cos(rad))
            y_outer = center_y + int(b_outer * math.sin(rad))
            self.outer_border.append((x_outer, y_outer))

            x_inner = center_x + int(a_inner * math.cos(rad))
            y_inner = center_y + int(b_inner * math.sin(rad))
            self.inner_border.append((x_inner, y_inner))

    def create_track_image(self):
        self.track_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        
        self.track_surface.fill(DARK_GREEN)

        
        num_trees = 50
        for _ in range(num_trees):
            angle = random.random() * 2 * math.pi
            distance = random.randint(370, 450)
            tree_x = self.width // 2 + int(distance * math.cos(angle))
            tree_y = self.height // 2 + int(distance * math.sin(angle))

           
            pygame.draw.rect(self.track_surface, BROWN,
                           (tree_x-3, tree_y-10, 6, 15))

            
            foliage_color = (
                random.randint(0, 50),
                random.randint(100, 200),
                random.randint(0, 50)
            )
            pygame.draw.circle(self.track_surface, foliage_color,
                             (tree_x, tree_y-15), random.randint(10, 15))

        
        num_inner_trees = 20
        for _ in range(num_inner_trees):
            angle = random.random() * 2 * math.pi
            distance = random.randint(50, 90)
            tree_x = self.width // 2 + int(distance * math.cos(angle))
            tree_y = self.height // 2 + int(distance * math.sin(angle))

            
            pygame.draw.rect(self.track_surface, BROWN,
                           (tree_x-2, tree_y-7, 4, 10))

          
            foliage_color = (
                random.randint(0, 50),
                random.randint(100, 200),
                random.randint(0, 50)
            )
            pygame.draw.circle(self.track_surface, foliage_color,
                             (tree_x, tree_y-10), random.randint(6, 10))

      
        for angle in range(0, 360, 5):
            rad = math.radians(angle)
            x = self.width // 2 + int(350 * math.cos(rad))
            y = self.height // 2 + int(250 * math.sin(rad))

            pygame.draw.rect(self.track_surface, (150, 150, 150),
                           (x-10, y-10, 20, 20))

            for i in range(3):
                spectator_y = y - 5 + (i * 5)
                for j in range(2):
                    spectator_x = x - 5 + (j * 5)
                    color = (
                        random.randint(50, 255),
                        random.randint(50, 255),
                        random.randint(50, 255)
                    )
                    pygame.draw.circle(self.track_surface, color,
                                     (spectator_x, spectator_y), 2)

        
        pygame.draw.polygon(self.track_surface, GRAY, self.outer_border)
        pygame.draw.polygon(self.track_surface, DARK_GREEN, self.inner_border)

        
        for angle in range(0, 360, 5):
            rad = math.radians(angle)
            x = self.width // 2 + int(150 * math.cos(rad))
            y = self.height // 2 + int(50 * math.sin(rad))

            pygame.draw.rect(self.track_surface, (150, 150, 150),
                           (x-8, y-8, 16, 16))

            for i in range(2):
                spectator_y = y - 4 + (i * 4)
                for j in range(2):
                    spectator_x = x - 4 + (j * 4)
                    color = (
                        random.randint(50, 255),
                        random.randint(50, 255),
                        random.randint(50, 255)
                    )
                    pygame.draw.circle(self.track_surface, color,
                                     (spectator_x, spectator_y), 1)

        
        pygame.draw.polygon(self.track_surface, WHITE, self.outer_border, 4)
        pygame.draw.polygon(self.track_surface, WHITE, self.inner_border, 4)

       
        finish_line_start = (self.width // 2, self.height // 2 - 200)
        finish_line_end = (self.width // 2, self.height // 2 - 100)
        pygame.draw.line(self.track_surface, WHITE, finish_line_start, finish_line_end, 6)

     
        line_length = 100
        num_segments = 10
        segment_length = line_length / num_segments

        for i in range(num_segments):
            if i % 2 == 0:
                continue

            start_y = finish_line_start[1] + i * segment_length
            end_y = start_y + segment_length

            pygame.draw.line(self.track_surface, BLACK,
                            (finish_line_start[0], start_y),
                            (finish_line_start[0], end_y), 6)

       
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            x1 = self.width // 2 + int(250 * math.cos(rad))
            y1 = self.height // 2 + int(150 * math.sin(rad))
            x2 = self.width // 2 + int(270 * math.cos(rad))
            y2 = self.height // 2 + int(170 * math.sin(rad))
            pygame.draw.line(self.track_surface, WHITE, (x1, y1), (x2, y2), 2)

    def get_track_center_at_finish_line(self):
        return (self.width // 2, self.height // 2 - 150)

    def check_finish_line(self, x, y):
        finish_line_x = self.width // 2
        finish_line_y1 = self.height // 2 - 200
        finish_line_y2 = self.height // 2 - 100

        buffer = 10
        if (abs(x - finish_line_x) < buffer and
            y >= finish_line_y1 - buffer and
            y <= finish_line_y2 + buffer):
            return True
        return False

    def check_checkpoint(self, x, y):
        checkpoint_x = self.width // 2
        checkpoint_y1 = self.height // 2 + 100
        checkpoint_y2 = self.height // 2 + 200

        buffer = 10
        if (abs(x - checkpoint_x) < buffer and
            y >= checkpoint_y1 - buffer and
            y <= checkpoint_y2 + buffer):
            return True
        return False

    def is_on_track(self, x, y):
        def is_point_in_polygon(point, polygon):
            x, y = point
            n = len(polygon)
            inside = False

            p1x, p1y = polygon[0]
            for i in range(1, n + 1):
                p2x, p2y = polygon[i % n]
                if y > min(p1y, p2y):
                    if y <= max(p1y, p2y):
                        if x <= max(p1x, p2x):
                            if p1y != p2y:
                                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y

            return inside

        return (is_point_in_polygon((x, y), self.outer_border) and
                not is_point_in_polygon((x, y), self.inner_border))

    def draw(self, surface):
        surface.blit(self.track_surface, (0, 0))

def create_menu(surface):
    global player1_name, player2_name
    menu = pygame_menu.Menu('Racing Game', MENU_WIDTH, MENU_HEIGHT,
                          theme=pygame_menu.themes.THEME_DARK)

    def set_player1_name(value):
        global player1_name
        player1_name = value

    def set_player2_name(value):
        global player2_name
        player2_name = value

    menu.add.text_input('Player 1 Name: ', default='Player 1', onchange=set_player1_name)
    menu.add.text_input('Player 2 Name: ', default='Player 2', onchange=set_player2_name)
    menu.add.button('Play', start_game)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    return menu

def show_winner_menu(surface, winner_name):
    menu = pygame_menu.Menu('Game Over', MENU_WIDTH, MENU_HEIGHT,
                          theme=pygame_menu.themes.THEME_DARK)

    menu.add.label(f'{winner_name} Wins!')
    menu.add.button('Restart', start_game)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    return menu

def start_game():
    track = Track(SCREEN_WIDTH, SCREEN_HEIGHT)
    start_pos = track.get_track_center_at_finish_line()

    # player 1 car (red, controlled by W key)
    player1_car = Car(start_pos[0] - 20, start_pos[1], RED, pygame.K_w)
    player1_car.angle = 270
    player1_car.current_track = track

    # player 2 car (yellow, controlled by UP arrow key)
    player2_car = Car(start_pos[0] + 20, start_pos[1], YELLOW, pygame.K_UP)
    player2_car.angle = 90
    player2_car.current_track = track

    running = True
    game_over = False
    winner = None

    while running:
        if game_over:
            winner_menu = show_winner_menu(screen, winner)
            winner_menu.mainloop(screen)
            running = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset both cars
                    player1_car.x = start_pos[0] - 20
                    player1_car.y = start_pos[1]
                    player1_car.speed = 0
                    player1_car.angle = 270
                    player1_car.lap_count = 0
                    player1_car.checkpoint_passed = False
                    player1_car.current_lap_time = 0
                    player1_car.lap_start_time = pygame.time.get_ticks()

                    player2_car.x = start_pos[0] + 20
                    player2_car.y = start_pos[1]
                    player2_car.speed = 0
                    player2_car.angle = 90
                    player2_car.lap_count = 0
                    player2_car.checkpoint_passed = False
                    player2_car.current_lap_time = 0
                    player2_car.lap_start_time = pygame.time.get_ticks()

        keys = pygame.key.get_pressed()
        player1_car.update(keys, track)
        player2_car.update(keys, track)

        
        if player1_car.check_collision(player2_car):
            player1_car.handle_collision(player2_car)

        
        if player1_car.lap_count >= 5:
            winner = player1_name
            game_over = True
        elif player2_car.lap_count >= 5:
            winner = player2_name
            game_over = True

        # Update times
        current_time = pygame.time.get_ticks()
        player1_car.current_lap_time = (current_time - player1_car.lap_start_time) / 1000.0
        player2_car.current_lap_time = (current_time - player2_car.lap_start_time) / 1000.0

       
        screen.fill(DARK_GREEN)
        track.draw(screen)
        player1_car.draw(screen)
        player2_car.draw(screen)

    
        font = pygame.font.Font(None, 36)

        # Player 1 HUD
        p1_name_text = font.render(player1_name, True, RED)
        screen.blit(p1_name_text, (10, 10))

        p1_speed_text = font.render(f"Speed: {int(player1_car.speed * 10)} km/h", True, RED)
        screen.blit(p1_speed_text, (10, 40))

        p1_lap_text = font.render(f"Lap: {player1_car.lap_count}/5", True, RED)
        screen.blit(p1_lap_text, (10, 70))

        p1_time_text = font.render(f"Time: {player1_car.current_lap_time:.2f}", True, RED)
        screen.blit(p1_time_text, (10, 100))

        if player1_car.best_lap_time < float('inf'):
            p1_best_text = font.render(f"Best: {player1_car.best_lap_time:.2f}", True, RED)
            screen.blit(p1_best_text, (10, 130))

        # Player 2 HUD
        p2_name_text = font.render(player2_name, True, YELLOW)
        screen.blit(p2_name_text, (SCREEN_WIDTH - 250, 10))

        p2_speed_text = font.render(f"Speed: {int(player2_car.speed * 10)} km/h", True, YELLOW)
        screen.blit(p2_speed_text, (SCREEN_WIDTH - 250, 40))

        p2_lap_text = font.render(f"Lap: {player2_car.lap_count}/5", True, YELLOW)
        screen.blit(p2_lap_text, (SCREEN_WIDTH - 250, 70))

        p2_time_text = font.render(f"Time: {player2_car.current_lap_time:.2f}", True, YELLOW)
        screen.blit(p2_time_text, (SCREEN_WIDTH - 250, 100))

        if player2_car.best_lap_time < float('inf'):
            p2_best_text = font.render(f"Best: {player2_car.best_lap_time:.2f}", True, YELLOW)
            screen.blit(p2_best_text, (SCREEN_WIDTH - 250, 130))

        # Controls help
        help_text = pygame.font.Font(None, 24).render("Controls: P1=W key, P2=UP arrow, R=Reset", True, WHITE)
        screen.blit(help_text, (10, SCREEN_HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)

def main():
    pygame.init()
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Racing Game - Two Players")

    menu = create_menu(surface)
    menu.mainloop(surface)

if __name__ == "__main__":
    main()
