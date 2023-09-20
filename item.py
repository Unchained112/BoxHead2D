import weapon
from character import Player

class Item:
    """
    Item to be bought in the shop.
    Item quality: bronze: 1, sliver: 2, gold: 3
    PS: quality=0 means the item has no quality,
    e.g. adding a weapon
    """

    def __init__(self, image_path: str, description: str, equip):
        self.image_path = image_path
        self.description = description
        self.equip = equip
        self.quality = 0
        self.value = 0
        self.cost = 0


# Player items


def increase_health(quality: int, player: Player) -> bool:
    if quality == 1:
        player.health += 50
    if quality == 2:
        player.health += 100
    if quality == 3:
        player.health += 200
    return True


def increase_speed(quality: int, player: Player) -> bool:
    if quality == 1:
        player.speed += 100
    if quality == 2:
        player.speed += 200
    if quality == 3:
        player.speed += 400
    return True


def increase_explosion_damage(quality: int, player: Player) -> bool:
    if quality == 1:
        player.explosion_damage += 10
    if quality == 2:
        player.explosion_damage += 20
    if quality == 3:
        player.explosion_damage += 40
    return True


def minus_health(quality: int, player: Player) -> bool:
    if quality == 1:
        health = 50
    if quality == 2:
        health = 100
    if quality == 3:
        health = 200
    if player.health > health:
        player.health -= health
        return True
    else:
        return False


def minus_speed(quality: int, player: Player) -> bool:
    if quality == 1:
        speed = 100
    if quality == 2:
        speed = 200
    if quality == 3:
        speed = 400
    # Player speed minimum: 600
    if player.speed - speed > 600:
        player.speed -= speed
        return True
    else:
        return False


def minus_explosion_damage(quality: int, player: Player) -> bool:
    if quality == 1:
        explosion_damage = 10
    if quality == 2:
        explosion_damage = 20
    if quality == 3:
        explosion_damage = 40
    if player.explosion_damage > explosion_damage:
        player.explosion_damage -= explosion_damage
        return True
    else:
        return False


class Shop:
    """Shop instance class."""

    def __init__(self, player: Player):
        self.uzi = player.weapons[0]
        self.defualt_item_list = []

        self.uzi = weapon.Uzi()
        self.shotgun = weapon.Shotgun()
        self.rocket = weapon.Rocket()
        self.placed_wall = weapon.PlacedWall()
        self.barrel = weapon.Barrel()
        self.mine = weapon.Mine()
        self.uzi_item_list = []
        self.shotgun_item_list = []
        self.rocket_item_list = []
        self.wall_item_list = []
        self.barrel_item_list = []
        self.mine_item_list = []
        self.cur_item_list = []

    def add_uzi(self, player: Player) -> bool:
        player.add_weapon(self.uzi)
        return True

    def clear(self) -> None:
        pass