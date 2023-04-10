from time import time

import mapping.mapping as mapping

lvl = mapping.Map(100, 100)
layers = lvl.get_layers()
layers['bg'].show()
layers['bg'].save(f'./img/{time()}.png')
