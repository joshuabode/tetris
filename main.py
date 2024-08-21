import pygame
import random
import numpy as np
from math import inf
color_map = {"boundary": "white" ,
               "tee": "purple", 
               "line": "cyan", 
               "cube": "yellow", 
               "ella": "orange",
               "ellb": "blue",
               "ess": "green",
               "zed": "red"}
score_dict = {0: 0, 1: 40, 2: 100, 3: 300, 4: 1200}
offset_dict = {"tee": (-10, 0), 
                "line": (0, -10), 
                "cube": (0, 0), 
                "ella": (-10,20),
                "ellb": (-10,20),
                "ess": (-10,0),
                "zed": (-10, 0)}
frame_rate = 30
speed = 1

def draw_square(x: int, y: int, shape: str, flash: bool):
    rect = pygame.Rect(x, y, 20, 20)
    if flash:
        square = pygame.draw.rect(screen, 'white', rect)
    else:
        square = pygame.draw.rect(screen, color_map[shape], rect)
    border = pygame.draw.rect(screen, 'black', rect, 1)
    return rect

def clear_lines(lines: list):
    if lines:
        for line in lines:
            y_to_go = (20-line)*20
            squares_to_go = [sq for sq in placed_squares if sq[0].y == y_to_go]
            for sq in squares_to_go:
                placed_squares.remove(sq)
            squares_to_drop = [sq for sq in placed_squares if sq[0].y < y_to_go]
            for sq in squares_to_drop:
                if sq[1] != "boundary":
                    sq[0].move_ip(0, 20)
                

    l_dict = {i: 0 for i in range(1, 30)}
    for sq in placed_squares:
        if sq[0].w == 20:
            l_dict[20-(sq[0].y//20)] += 1
    
    score = score_dict[len(lines)] * speed
    return (l_dict, score)

def draw_current():
    global current
    bonus = current.update()
    current.draw()
    return bonus

def draw_polys(polys):
    for poly in polys:
        if poly[1] != "boundary":
            draw_square(poly[0].x, poly[0].y, poly[1], False)
        else:
            pygame.draw.rect(screen, "black", poly[0])

def draw_aux(next_p, held_p):
    if next_p:
        next_p.draw()
    if held_p:
        held_p.draw()

def draw_text(string, color, x, y, size):
    font = pygame.font.Font("_internal/alagard.ttf", size)
    text = font.render(string, 1, color)
    rect = text.get_rect()
    rect.centerx, rect.centery = x, y
    screen.blit(text, rect)

class Poly:
    def __init__(self, x, y, speed):
        self.x, self.y = x, y
        self.state = 0
        self.x_min, self.x_max, self.count = self.limits[0][0], self.limits[0][1], 0
        if speed:
            self.count_max = frame_rate/speed 
        else:
            self.count_max = inf
        self.squares = [None for _ in range(self.n)]
        self.touched, self.placed = False, False
        self.flash = False
 
        
    def draw(self):
        x, y = self.x, self.y
        coords = self.coords[self.state]
        for i in range(self.n):
            self.squares[i] = draw_square(x+coords[i][0], y+coords[i][1], self.name, self.flash)

    def update(self):
        for square in self.squares:
            square.move_ip(0, 1)
        i_s = [square.collidelist([sq[0] for sq in placed_squares]) for square in self.squares]
        if all(i == -1 for i in i_s):
            self.touched = False
        else:
            self.touched = True
        if self.count == 0 and self.touched == False:
            self.y += 20
            self.count += 1
            return 1
        elif self.count == 0 and self.touched == True:
            self.placed, self.flash = True, True
        elif self.count < self.count_max:
            self.count += 1
        else:
            self.count = 0
        return 0

    def left(self):
        for square in self.squares:
            square.move_ip(-10, 0)
        i_s = [square.collidelist([sq[0] for sq in placed_squares]) for square in self.squares]
        if all(i == -1 for i in i_s):
            self.x -= 20

    def right(self):
        for square in self.squares:
            square.move_ip(10, 0)
        i_s = [square.collidelist([sq[0] for sq in placed_squares]) for square in self.squares]
        if all(i == -1 for i in i_s):
            self.x += 20

    def down(self):
        for square in self.squares:
            square.move_ip(0, 1)
        i_s = [square.collidelist([sq[0] for sq in placed_squares]) for square in self.squares]
        if all(i == -1 for i in i_s):
            self.touched = False
        else:
            self.touched = True
            self.placed = True
        if not self.touched:
            self.y += 20

    def clockwise(self):
        for i in range(self.n):
            x, y = tuple(np.subtract(self.coords[(self.state - 1)%len(self.coords)][i], self.coords[self.state][i]))
            self.squares[i].move_ip(x, y)
        i_s = [square.collidelist([sq[0] for sq in placed_squares]) for square in self.squares]
        if all(i == -1 for i in i_s):
            self.state = (self.state - 1) % len(self.coords)
            self.x_min, self.x_max = self.limits[self.state]

    def anticlockwise(self):
        for i in range(self.n):
            x, y = tuple(np.subtract(self.coords[(self.state + 1)%len(self.coords)][i], self.coords[self.state][i]))
            self.squares[i].move_ip(x, y)
        i_s = [square.collidelist([sq[0] for sq in placed_squares]) for square in self.squares]
        if all(i == -1 for i in i_s):
            self.state = (self.state + 1) % len(self.coords)
            self.x_min, self.x_max = self.limits[self.state]

class Tee(Poly):
    def __init__(self, x, y, speed):
        self.name = "tee"
        self.n = 4
        self.limits = [(20, 160), (0, 160), (20, 160), (20, 180)]
        self.coords = [[(-20, -20), (0, -20), (20, -20), (0, 0)],
                        [(0, -40), (0, -20), (20, -20), (0, 0)],
                        [(0, -20), (-20, -20), (20, -20), (0, -40)], 
                        [(0, -40), (0, -20), (-20, -20), (0, 0)]]
        super().__init__(x, y, speed)
        self.draw()   
    
class Line(Poly):
    def __init__(self, x, y, speed):
        self.name = "line"
        self.n = 4
        self.limits = [(40, 160), (0, 180), (40, 160), (20, 200)]
        self.coords = [[(-40, 0), (-20, 0), (0, 0), (20, 0)], 
                        [(0, -40), (0, -20), (0, 0), (0, 20)],
                        [(-40, -20), (-20, -20), (0, -20), (20, -20)],
                        [(-20, -40), (-20, -20), (-20, 0), (-20, 20)]]
        super().__init__(x, y, speed)
        self.draw()
   
class Cube(Poly):
    def __init__(self, x, y, speed):
        self.name = "cube"
        self.n = 4
        self.limits = [(20, 180)]
        self.coords = [[(0, 0), (-20, 0), (-20, -20), (0, -20)]]
        super().__init__(x, y, speed)
        self.draw()

class EllA(Poly):
    def __init__(self, x, y, speed):
        self.name = "ella"
        self.n = 4
        self.limits = [(20, 160), (20, 180), (20, 160), (0, 160)]
        self.coords = [[(-20, -20), (0, -20), (20, -20), (20, -40)],
                        [(0, 0), (0, -20), (0, -40), (-20, -40)],
                        [(-20, 0), (-20, -20), (0, -20), (20, -20)],
                        [(0, 0), (20, 0), (0, -20), (0, -40)]]
        super().__init__(x, y, speed)
        self.draw()

class EllB(Poly):
    def __init__(self, x, y, speed):
        self.name = "ellb"
        self.n = 4
        self.limits = [(20, 160), (20, 180), (20, 160), (0, 160)]
        self.coords = [[(-20, -40), (-20, -20), (0, -20), (20, -20)],
                        [(0, 0), (-20, 0), (0, -20), (0, -40)],
                        [(-20, -20), (0, -20), (20, -20), (20, 0)],
                        [(0, 0), (0, -20), (0, -40), (20, -40)]]
        super().__init__(x, y, speed)
        self.draw()

class Ess(Poly):
    def __init__(self, x, y, speed):
        self.name = "ess"
        self.n = 4
        self.limits = [(20, 160), (20, 180), (20, 160), (0, 160)]
        self.coords = [[(-20, 0), (0, 0), (0, -20), (20, -20)],
                        [(0, 0), (-20, 0), (0, 20), (-20, -20)],
                        [(-20, 20), (0, 20), (0,0), (20, 0)],
                        [(0, 0), (0, -20), (20, 0), (20, 20)]]
        super().__init__(x, y, speed)
        self.draw()

class Zed(Poly):
    def __init__(self, x, y, speed):
        self.name = "zed"
        self.n = 4
        self.limits = [(20, 160), (0, 160), (20, 160), (20, 180)]
        self.coords = [[(0, 0), (-20, -20), (0, -20), (20, 0)],
                        [(0, 0), (0, 20), (20, 0), (20, -20)],
                        [(0, 0), (-20, 0), (0, 20), (20, 20)],
                        [(0, 0), (-20, 0), (-20, 20), (0, -20)]]
        super().__init__(x, y, speed)
        self.draw()


pieces = [Tee, Line, Ess, Zed, Cube, EllA, EllB]



pygame.init()
screen = pygame.display.set_mode((450, 450))
pygame.display.set_caption("Tetris by Joshua Bode")
icon = pygame.image.load('_internal/icon.png')
pygame.display.set_icon(icon)

clock = pygame.time.Clock()
boundaries =    [[pygame.Rect(0, 400, 200, 100), "boundary"], 
                [pygame.Rect(-1, 0, 1, 400), "boundary"],
                [pygame.Rect(200, 0, 50, 500), "boundary"]
                ]
running, current, placed_squares = True, random.choice(pieces)(100, 20, speed), []
can_hold = True

next_piece = random.choice(pieces)
held_piece = None
paused = False
over, game_over_flag = False, False
placed_squares.extend(boundaries)
full_lines = []
lines = {i: 0 for i in range(1, 30)}
lines_cleared = 0


score = 0
while running:
    if game_over_flag:
        over = True
        draw_text("Game Over", (200, 10, 10), 225, 150, 80)
        draw_text("Final Score: "+str(score), (0, 0, 0), 225, 200, 30)
        pygame.display.flip()
    keys = pygame.key.get_pressed()
        
    if keys[pygame.K_s] and current.touched == False and current.y < 400:
        current.count = 1
        current.down()
        score += 2
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
                if paused:
                    screen.fill("grey80")
                    draw_text("PAUSED", (10, 10, 200), 225, 175, 100)
                    pygame.display.flip()
        if event.type == pygame.KEYDOWN and current and not paused:
            if event.key == pygame.K_q:
                current.anticlockwise() 
            if event.key == pygame.K_e:
                current.clockwise()   
            if event.key == pygame.K_a and current.x_min < current.x:
                current.left()
            if event.key == pygame.K_d and current.x < current.x_max:
                current.right()
            if event.key == pygame.K_h and can_hold:
                can_hold = False
                temp = held_piece
                held_piece = eval(current.__class__.__name__)
                if temp:
                    current = eval(temp.__name__ + "(100, 0, speed)")
                else:
                    current = next_piece(100, 0, speed)
                    next_piece = random.choice(pieces)
            

    screen.fill("gray60")

    if not paused and not over:
        score += draw_current()
        draw_polys(placed_squares)
        next_name = next_piece.__name__.lower()
        if held_piece:
            held_name = held_piece.__name__.lower()
            draw_aux(next_piece(400+offset_dict[next_name][0], 100+offset_dict[next_name][1], 0),
                 held_piece(400+offset_dict[held_name][0], 170+offset_dict[held_name][1], 0))
        else:
            draw_aux(next_piece(400+offset_dict[next_name][0], 100+offset_dict[next_name][1], 0),
                 None)
        draw_text("Next: ", (0, 0, 0), 320, 100, 25)
        draw_text("Held: ", (0, 0, 0), 320, 170, 25)
        if current.placed:
            can_hold = True
            for square in current.squares:
                placed_squares.append([square, current.name])
                lines[20-(square.y//20)] += 1
            current = next_piece(100, 0, speed)
            next_piece = random.choice(pieces)
            for i in range(1, 21):
                if lines[i] == 10:
                    full_lines.append(i)
            if lines[21] > 0:
                game_over_flag = True
        lines, bonus = clear_lines(list(reversed(full_lines)))
        lines_cleared += len(full_lines)
        speed = (lines_cleared // 10) + 1
        score += bonus
        full_lines = []
        draw_text("Score: "+str(score), (10, 15, 10), 350, 30, 25)
        draw_text("Lines: "+str(lines_cleared), (250, 250, 250), 100, 420, 25)
        pygame.display.flip()
        clock.tick(frame_rate)


pygame.quit()