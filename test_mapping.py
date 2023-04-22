from time import time

import pygame

import mapping.mapping as mapping

pygame.init()

screen = pygame.display.set_mode((0, 0))
map = mapping.Map(120, 68)
map_img = map.get_layers()['bg']

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(map_img, (0, 0))

    pygame.display.flip()


pygame.quit()
