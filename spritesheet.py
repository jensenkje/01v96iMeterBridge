import pygame

def load_sprite_sheet_array(filename,rows,cols,offsetx,offsety):
    images = []
    SS = pygame.image.load(filename).convert_alpha()
    for col in range(0,cols):
        for row in range(0,rows):
            x = row*offsetx
            y = col*offsety
            image = pygame.Surface((offsetx,offsety),pygame.SRCALPHA).convert_alpha()
            image.blit(SS,(0,0),(x,y,offsetx,offsety))
            images.append(image)
    return images