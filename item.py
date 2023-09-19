from character import Player


class Item:
    """Item to be bought in the shop."""

    def __init__(self, image_path: str, description: str, cost: int, equip):
        self.image_path = image_path
        self.description = description

        # Item quality: bronze: 1, sliver: 2, gold: 3
        self.quality = 1
        self.cost = cost
        self.equip = equip

# Player items

def increase_health(quality: int, player: Player) -> bool:
    if quality == 1:
        player.health += 50
    if quality == 2:
        player.health += 100
    if quality == 3:
        player.health += 200
    return True


class Shop:
    """Shop instance class."""

    def __init__(self):
        self.player_item_list = []
        self.pistol_item_list = []
        self.uzi_item_list = []
        self.shotgun_item_list = []
        self.rocket_item_list = []
        self.wall_item_list = []
        self.barrel_item_list = []
        self.mine_item_list = []
        self.cur_item_list = []
