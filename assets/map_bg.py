from typing import Dict, Tuple
from PIL import Image

class TextureBlock:

    textures: Dict[Tuple[int, int], Image.Image] = {}

    def __init__(self, id: int, subId: int, file_name: str) -> None:

        self.key = (id, subId)
        self.id = id
        self.subId = subId
        self.texture = Image.open(f'./assets/map_bg/{file_name}')
        TextureBlock.textures[self.key] = self.texture

VIDE = TextureBlock(-1, 0, 'vide.png')
GROUND = TextureBlock(0, 0, 'sol.png')
DOOR = TextureBlock(1, 0, 'door.png')
HALL = TextureBlock(2, 0, 'hall.png')
WALL_BASE = TextureBlock(10, 0, 'mur_base.png')
WALL_N = TextureBlock(10, 1, 'mur_haut.png')
WALL_S = TextureBlock(10, 2, 'mur_bas.png')
WALL_O = TextureBlock(10, 3, 'mur_gauche.png')
WALL_E = TextureBlock(10, 4, 'mur_droit.png')
WALL_NO = TextureBlock(10, 5, 'mur_haut_gauche.png')
WALL_NE = TextureBlock(10, 6, 'mur_haut_droit.png')
WALL_SO = TextureBlock(10, 7, 'mur_bas_gauche.png')
WALL_SE = TextureBlock(10, 8, 'mur_bas_droit.png')

textures = TextureBlock.textures
