import pygame, math, time
from utils import scale_image, blit_rotate_center, blit_text_center

pygame.font.init()

# Getting all textures to be used
GRASS = scale_image(pygame.image.load(r"imgs/grass.jpg"), 1.5)

TRACK = scale_image(pygame.image.load(r"imgs/track.png"), 0.67)
TRACK_BORDER = scale_image(pygame.image.load(r"imgs/track-border.png"), 0.67)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = scale_image(pygame.image.load(r"imgs/finish.png"), 0.8)
FINISH_POSITION = (95, 190)
FINISH_MASK = pygame.mask.from_surface(FINISH)

RED_CAR = scale_image(pygame.image.load(r"imgs/red-car.png"), 0.38)
GREEN_CAR = scale_image(pygame.image.load(r"imgs/green-car.png"), 0.38)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()

# Window Size
WIN = pygame.display.set_mode((600,600))
pygame.display.set_caption("Racing Game")

MAIN_FONT = pygame.font.SysFont("bahnschrift", 35)

FPS = 60
PATH = [(116, 92), (90, 62), (44, 98), (50, 353), (230, 537), (290, 521), (305, 400), (358, 356), (442, 398), (469, 532), (535, 526), (546, 316), (522, 276), (342, 271), (295, 237), (321, 195), (506, 189), (549, 132), (525, 67), (252, 58), (205, 104), (208, 257), (175, 297), (132, 279), (134, 194)]

#
class GameInfo:
    LEVELS = 3

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()


    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)


# Main Car Class
class AbstractCar:
    
    def __init__(self, max_vel, rotate_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotate_vel = rotate_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotate_vel
        elif right:
            self.angle -= self.rotate_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_back(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel
        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0

# Child Class for Player Car
class PlayerCar(AbstractCar):

    IMG = RED_CAR
    START_POS = (135, 140)

    # For momentum while slowing
    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration/0.9, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel*0.3
        self.move()

# Child Class for Computer Car
class CompCar(AbstractCar):
    
    IMG = GREEN_CAR
    START_POS = (115, 140)

    def __init__(self, max_vel, rotate_vel, path=[]):
        super().__init__(max_vel, rotate_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel


    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi/2
        else:
            desired_radian_angle = math.atan(x_diff/y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotate_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotate_vel, abs(difference_in_angle))

    def update_point_path(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())

        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.update_point_path()
        super().move()

    
    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2
        self.current_point = 0

    '''def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255,0,0), point, 5)
        
    def draw(self, win):
        super().draw(win)
        self.draw_points(win)'''

def draw(win, imgs, player_car, comp_car, game_info):
    for img, pos in imgs:
        win.blit(img, pos)

    level_text = MAIN_FONT.render(f"Level {game_info.level}", 1, (255, 255, 255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))

    time_text = MAIN_FONT.render(f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))

    vel_text = MAIN_FONT.render(f"Vel {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))

    player_car.draw(win)
    comp_car.draw(win)

    pygame.display.update()

def handle_collision(player_car, comp_car, game_info):
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    comp_finish_poi_collide = comp_car.collide(FINISH_MASK, *FINISH_POSITION)
    if comp_finish_poi_collide != None:
        blit_text_center(WIN, MAIN_FONT, "Computer Wins! Try Again")
        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        comp_car.reset()

    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()
            comp_car.next_level(game_info.level)

def move_player(player_car):
    
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()

    if keys[pygame.K_s]:
        moved = True
        player_car.move_back()

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    
    if keys[pygame.K_d]:
        player_car.rotate(right=True)

    
    if not moved:
        player_car.reduce_speed()


run = True
clock = pygame.time.Clock()
imgs = [(GRASS, (0,0)), (TRACK, (0,0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0,0))]

# Define Cars
player_car = PlayerCar(1.3,2.2)
comp_car = CompCar(0.9,2.2, PATH)
game_info = GameInfo()

# MAIN EVENT LOOP
while run:
    clock.tick(FPS)

    draw(WIN, imgs, player_car, comp_car, game_info)

    while not game_info.started:
        blit_text_center(WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        '''if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            comp_car.path.append(pos)'''
        
    move_player(player_car)
    comp_car.move()
    
    handle_collision(player_car, comp_car, game_info)

    if game_info.game_finished():
        blit_text_center(WIN, MAIN_FONT, "You Won The Game!")
        pygame.time.wait(5000)
        pygame.display.update()
        game_info.reset()
        player_car.reset()
        comp_car.reset()

#print(comp_car.path)

pygame.quit()