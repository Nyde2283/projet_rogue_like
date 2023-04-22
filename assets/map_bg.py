from typing import Dict, Tuple
from PIL import Image

class TextureBlock:

    textures: Dict[Tuple[int, int], Image.Image] = {}

    def __init__(self, id: int, subId: int = -1, file_name: str = 'error.png') -> None:

        self.key = (id, subId)
        self.id = id
        self.subId = subId
        self.texture = Image.open(f'./assets/map_bg/{file_name}')
        TextureBlock.textures[self.key] = self.texture

VIDE = TextureBlock(-1, 0, 'vide.png')
GROUND = TextureBlock(0, 0, 'sol.png')
GROUND_DOOR = TextureBlock(0, 2, 'door.png')
GROUND_HALL = TextureBlock(0, 1, 'hall.png')
RAW_WALL = TextureBlock(10)
WALL_BASE = TextureBlock(10, 0, 'mur_base.png')
WALL_N = TextureBlock(10, 1, 'mur_haut.png')
WALL_S = TextureBlock(10, 2, 'mur_bas.png')
WALL_O = TextureBlock(10, 3, 'mur_gauche.png')
WALL_E = TextureBlock(10, 4, 'mur_droit.png')
WALL_NO = TextureBlock(10, 5, 'mur_haut_gauche.png')
WALL_NE = TextureBlock(10, 6, 'mur_haut_droit.png')
WALL_SO = TextureBlock(10, 7, 'mur_bas_gauche.png')
WALL_SE = TextureBlock(10, 8, 'mur_bas_droit.png')
WALL_NO_INT = TextureBlock(10, 9, 'mur_haut_gauche_int.png')
WALL_NE_INT = TextureBlock(10, 10, 'mur_haut_droit_int.png')
WALL_SO_INT = TextureBlock(10, 11, 'mur_bas_gauche_int.png')
WALL_SE_INT = TextureBlock(10, 12, 'mur_bas_droit_int.png')

textures = TextureBlock.textures
