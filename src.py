import pygame
import neat
import time
import os
import random
from pygame.locals import *
pygame.font.init()

WIN_WIDTH = 440
WIN_HEIGHT = 600
GEN = 0  

BIRD_IMGS = [pygame.transform.scale(pygame.image.load("bird1.png"), (47,32)),\
  pygame.transform.scale(pygame.image.load("bird2.png"), (47,32)),
  pygame.transform.scale(pygame.image.load("bird3.png"), (47,32))]
PIPE_IMG = pygame.transform.scale(pygame.image.load("pipe.png"), (73,500))
BG_IMG = pygame.transform.scale(pygame.image.load("bg.png"), (450,600))
BASE_IMG = pygame.transform.scale(pygame.image.load("base.png"), (420,112))

STAT_FONT = pygame.font.SysFont("comicsans", 35)

class Bg:
  WIDTH = BG_IMG.get_width()
  IMG = BG_IMG

  def __init__(self, velocity):
    self.VEL = velocity
    self.y = 0
    self.x1 = 0
    self.x2 = self.WIDTH

  def move(self):
    self.x1 -= round(self.VEL * 0.12)
    self.x2 -= round(self.VEL * 0.12)
    if self.x1 + self.WIDTH < 0:
      self.x1 = self.x2 + self.WIDTH

    if self.x2 + self.WIDTH < 0:
      self.x2 = self.x1 + self.WIDTH

  def draw(self, win):
    win.blit(self.IMG, (self.x1, self.y))
    win.blit(self.IMG, (self.x2, self.y))

class Bird:
  IMGS = BIRD_IMGS
  MAX_ROTATION = 25
  ROT_VEL = 20
  ANIMATION_TIME = 5

  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.tilt = 0
    self.tick_count = 0
    self.vel = 0
    self.height = self.y
    self.img_count = 0
    self.img = self.IMGS[0]

  def jump(self):
    self.vel = -9.0
    self.tick_count = 0
    self.height = self.y
  
  def move(self):
    self.tick_count += 1

    d = self.vel * self.tick_count + 1.5 * self.tick_count**2

    if d >= 16:
      d = 16
    if d < 0:
      d -= 2
    
    self.y = self.y + d

    if d < 0 or self.y <self.height + 50:
      if self.tilt < self.MAX_ROTATION:
        self.tilt = self.MAX_ROTATION
    else:
      if self.tilt > -90:
        self.tilt -= self.ROT_VEL
      
  def draw(self, win):
    self.img_count += 1

    if self.img_count < self.ANIMATION_TIME:
      self.img = self.IMGS[0]
    elif self.img_count < self.ANIMATION_TIME*2:
      self.img = self.IMGS[1]
    elif self.img_count < self.ANIMATION_TIME*3:
      self.img = self.IMGS[2]
    elif self.img_count < self.ANIMATION_TIME*4:
      self.img = self.IMGS[1]
    elif self.img_count < self.ANIMATION_TIME*4 + 1:
      self.img = self.IMGS[0]
      self.img_count = 0

    if self.tilt <= -80:
      self.img = self.IMGS[1]
      self.img_count = self.ANIMATION_TIME*2
    
    rotated_image = pygame.transform.rotate(self.img, self.tilt)
    new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
    win.blit(rotated_image, new_rect.topleft)
  
  def get_mask(self):
    return pygame.mask.from_surface(self.img)

class Pipe:
  GAP = 170#120

  def __init__(self, x, velocity, pipeno):
    self.pipeno = pipeno
    self.tick_count = 0
    self.VEL = velocity
    self.x = x
    self.height = 0

    self.top = 0
    self.bottom = 0

    self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
    self.PIPE_BOTTOM = PIPE_IMG

    self.passed = False

    self.set_height()

  def set_height(self):
    if self.pipeno%2 == 0:
      self.height = random.randrange(40, 90)#40,370
    else:
      self.height = random.randrange(180, 230)#40,370
    self.top = self.height - self.PIPE_TOP.get_height()
    self.bottom = self.height + self.GAP

  def move(self):
    self.tick_count += 1
    pipevel = 0.02
    self.x -= round(self.VEL * 0.12)
    if self.pipeno%2 == 0:
      self.bottom += round(self.tick_count*pipevel) 
      self.top += round(self.tick_count*pipevel) 
    else:
      self.bottom -= round(self.tick_count*pipevel) 
      self.top -= round(self.tick_count*pipevel)

  def draw(self, win):
    win.blit(self.PIPE_TOP, (self.x, self.top))
    win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


  def collide(self, bird):
    bird_mask = bird.get_mask()
    top_mask = pygame.mask.from_surface(self.PIPE_TOP)
    bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
    
    top_offset = (self.x - bird.x, self.top - round(bird.y))
    bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

    b_point = bird_mask.overlap(bottom_mask, bottom_offset)
    t_point = bird_mask.overlap(top_mask,top_offset)

    if b_point or t_point:
      return True

    return False

class Base:
  WIDTH = BASE_IMG.get_width()
  IMG = BASE_IMG

  def __init__(self, y, velocity):
    self.VEL = velocity
    self.y = y
    self.x1 = 0
    self.x2 = self.WIDTH

  def move(self):
    self.x1 -= round(self.VEL * 0.12)
    self.x2 -= round(self.VEL * 0.12)
    if self.x1 + self.WIDTH < 0:
      self.x1 = self.x2 + self.WIDTH

    if self.x2 + self.WIDTH < 0:
      self.x2 = self.x1 + self.WIDTH

  def draw(self, win):
    win.blit(self.IMG, (self.x1, self.y))
    win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, birds, pipes, base, score, gen, bg):
  bg.draw(win)
  # win.blit(BG_IMG, (0,0))

  for pipe in pipes:
    pipe.draw(win)
  
  text = STAT_FONT.render("Score: "+str(score), 1, (255,255,255))
  win.blit(text, (WIN_WIDTH-10-text.get_width(), 10))

  text = STAT_FONT.render("Gen : "+str(gen), 1, (255,255,255))
  win.blit(text, (10, 10)) 

  text = STAT_FONT.render("Alive: "+str(len(birds)), 1, (255,255,255))
  win.blit(text, (10, 40))

  base.draw(win)
  for bird in birds:
    bird.draw(win)
  pygame.display.update()

def main(genomes, config): #actual fitness function
  score = 0
  global GEN
  GEN += 1
  nets = []
  ge = []
  birds = []#Bird(130, 240)

  for _,g in genomes:
    net = neat.nn.FeedForwardNetwork.create(g, config)
    nets.append(net)
    birds.append(Bird(130,240))
    g.fitness = 0
    ge.append(g)
  
  bg = Bg(1)
  base = Base(530, 30)
  pipes = [Pipe(480,30,0)]
  win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), RESIZABLE)
  pygame.init()
  run = True

  clock = pygame.time.Clock()

  while run:
    clock.tick(30)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        if len(ge)>0:
          print(ge[0])
        run = False
        pygame.quit()
        quit()
    
    pipe_ind = 0
    if len(birds) > 0:
      if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
        pipe_ind = 1
    
    else:
      run = False
      break
    
    for x,bird in enumerate(birds):
      bird.move()
      ge[x].fitness += 0.1

      output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
      if output[0] > 0.5:
        bird.jump()


    rem = []
    add_pipe = False
    for pipe in pipes:
      VEL_C = min(30 + score*0.75, 150)
      base.VEL = VEL_C
      bg.VEL = VEL_C/7
      for x,bird in enumerate(birds):
        if pipe.collide(bird):
          ge[x].fitness -= 1
          birds.pop(x)
          nets.pop(x)
          ge.pop(x)

        if not pipe.passed and pipe.x < bird.x:
          pipe.passed = True
          add_pipe = True

      if pipe.x + pipe.PIPE_TOP.get_width() < 0:
          rem.append(pipe)
      
      pipe.move()

    if add_pipe:
      score += 1
      for g in ge:
        g.fitness += 5
      pipes.append(Pipe(480,VEL_C,score))
      # if len(ge)>0:
      #   print(ge[0], ge[len(ge)-1])

    for r in rem:
      pipes.remove(r)

    for x,bird in enumerate(birds):
      if bird.y + bird.img.get_height() >= 530 or bird.y<0:
        ge[x].fitness -= 2
        birds.pop(x)
        nets.pop(x)
        ge.pop(x)

    bg.move()
    base.move()
    # print(base.VEL)
    draw_window(win, birds, pipes, base, score, GEN, bg)

  

def run(config_file):
  config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_file)

  p = neat.Population(config)

  p.add_reporter(neat.StdOutReporter(True))
  stats = neat.StatisticsReporter()
  p.add_reporter(stats)

  p.run(main, 20)
  winner = stats.best_genome()
  print(winner)


if __name__ == '__main__':
  local_dir = os.path.dirname(__file__)
  config_path = os.path.join(local_dir, 'config-feedforward.txt')
  run(config_path)