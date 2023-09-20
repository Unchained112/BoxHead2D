import weapon
import random
from character import Player


class Item:
    """
    Item to be bought in the shop.
    Item quality: bronze: 1, sliver: 2, gold: 3
    PS: quality = -1 means the item has no quality,
    e.g. adding a weapon.
    """

    def __init__(self,
                 image_path: str,
                 description: str,
                 base_value: int,
                 base_cost: int,
                 quality: int,
                 equip):
        self.image_path = image_path
        self.description = description
        self.value = base_value
        self.cost = base_cost
        self.equip = equip
        self.quality = quality


def increase_health(item: Item, player: Player) -> bool:
    player.health += item.value
    return True


def increase_speed(item: Item, player: Player) -> bool:
    player.speed += item.value
    return True


def increase_luck(item: Item, player: Player) -> bool:
    # Luck maximum: 60
    player.luck = min(item.value + player.luck, 60)
    return True


def increase_explosion_damage(item: Item, player: Player) -> bool:
    player.explosion_damage += item.value
    return True


def increase_kill_recover(item: Item, player: Player) -> bool:
    player.kill_recover += item.value
    return True


def minus_health(item: Item, player: Player) -> bool:
    if player.health > item.value:
        player.health -= item.value
        return True
    else:
        return False


def minus_luck(item: Item, player: Player) -> bool:
    # Minimum luck -60
    if player.luck > item.value - 61:
        player.luck -= item.value
        return True
    else:
        return False


def minus_speed(item: Item, player: Player) -> bool:
    # Player speed minimum: 600
    if player.speed - item.value > 600:
        player.speed -= item.value
        return True
    else:
        return False


def minus_explosion_damage(item: Item, player: Player) -> bool:
    if player.explosion_damage > item.value:
        player.explosion_damage -= item.value
        return True
    else:
        return False


def minus_kill_recover(item: Item, player: Player) -> bool:
    if player.kill_recover > item.value:
        player.kill_recover -= item.value
        return True
    else:
        return False


class Shop:
    """Shop instance class."""

    def __init__(self, player: Player):
        self.pistol = player.weapons[0]
        self.default_item_list = [
            Item("", "Add health: ", 50, 10, 1, increase_health),
            Item("", "Sell health: ", 50, -18, 1, minus_health),
            Item("", "Add speed: ", 100, 15, 1, increase_speed),
            Item("", "Sell speed: ", 100, -25, 1, minus_speed),
            Item("", "Increase luck: ", 2, 18, 1, increase_luck),
            Item("", "Sell luck: ", 2, -32, 1, minus_luck),
            Item("", "Add health recover after kill: ",
                 5, 12, 1, increase_kill_recover),
            Item("", "Sell health recover after kill: ",
                 5, -24, 1, minus_kill_recover),
            Item("", "Get Uzi", 0, 30, -1, self.add_uzi),
        ]

        self.uzi = weapon.Uzi()
        self.shotgun = weapon.Shotgun()
        self.rocket = weapon.Rocket()
        self.placed_wall = weapon.PlacedWall()
        self.barrel = weapon.Barrel()
        self.mine = weapon.Mine()

        self.explosion_item_list = [
            Item("", "Add explosion damage: ",
                 10, 30, 1, increase_explosion_damage),
            Item("", "Sell explosion damage: ",
                 10, -40, 1, minus_explosion_damage),
        ]
        self.uzi_item_list = []
        self.shotgun_item_list = []
        self.rocket_item_list = []
        self.wall_item_list = []
        self.barrel_item_list = []
        self.mine_item_list = []
        self.cur_item_list = []

    def generate_item(self, item: Item, wave: int, player: Player) -> Item:
        if item.quality == -1:
            return item

        actual_cost = item.cost + wave + int(item.cost * wave * 0.1)
        rand_quality = random.randrange(0, 99)

        actual_quality = 0
        if rand_quality < wave + player.luck:
            actual_quality = 3
        elif rand_quality >= wave + player.luck and rand_quality < 2 * (wave + player.luck):
            actual_quality = 2
        else:
            actual_quality = 1

        real_value = 0
        if actual_quality == 1:
            real_value = item.value
        elif actual_quality == 2:
            real_value = item.value * 2
        else:
            real_value = item.value * 4

        return Item(item.image_path,
                    item.description + str(real_value),
                    real_value,
                    actual_cost,
                    actual_quality,
                    item.equip
                    )

    def get_items(self, wave: int, player: Player) -> list:
        items = []

        return items

    def add_uzi(self, player: Player) -> bool:
        player.add_weapon(self.uzi)
        return True

    def clear(self) -> None:
        pass


# For testing
x = Player()
