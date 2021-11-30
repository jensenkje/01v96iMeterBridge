import random
import sys
import pygame

pygame.init()
clock = pygame.time.Clock()


screen_width = 2560
screen_height = 720

#screen = pygame.display.set_mode((screen_width,screen_height),pygame.FULLSCREEN)
screen = pygame.display.set_mode((screen_width,screen_height))



while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()


    pygame.display.flip()
    clock.tick(10)