from Zumbi import Zumbi
from Cachorro import Cachorro
from Boss import Boss

def get_enemy_config(tile_size):
    return {
        1: {
            'class': Zumbi,
            'positions': [
                (35 * tile_size, 16 * tile_size),
                (55 * tile_size, 16 * tile_size),
                (59 * tile_size, 16 * tile_size)
            ]
        },
        2: {
            'class': Cachorro,
            'positions': [
                (15 * tile_size, 22 * tile_size)
            ]
        },
        3: {
            'class': Boss,
            'positions': [
                (40 * tile_size, 20 * tile_size)
            ]
        }
    }