import weapon
import random
from utils import Utils
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


def minus_energy(item: Item, player: Player) -> bool:
    if player.energy >= item.value:
        player.energy -= item.value
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
    if player.speed - item.value >= 600:
        player.speed -= item.value
        return True
    else:
        return False


class Shop:
    """Shop instance class."""

    def __init__(self, player: Player):
        self.pistol = player.weapons[0]
        self.uzi = weapon.Uzi()
        self.shotgun = weapon.Shotgun()
        self.rocket = weapon.Rocket()
        self.wall = weapon.PlacedWall()
        self.barrel = weapon.Barrel()
        self.mine = weapon.Mine()
        self.add_uzi_item = Item("", "Get Uzi", 0, 30, -1, self.add_uzi)
        self.add_shotgun_item = Item(
            "", "Get Shotgun", 0, 42, -1, self.add_shotgun)
        self.add_rocket_item = Item(
            "", "Get Rocket", 0, 56, -1, self.add_rocket)
        self.add_wall_item = Item(
            "", "Get Wall", 0, 28, -1, self.add_wall)
        self.add_barrel_item = Item(
            "", "Get Barrel", 0, 52, -1, self.add_barrel)
        self.add_mine_item = Item(
            "", "Get Mine", 0, 49, -1, self.add_mine)

        self.default_item_list = [
            Item("", "Sell health: ", 100, -18, 1, minus_health),
            Item("", "Sell energy: ", 50, -12, 1, minus_energy),
            Item("", "Add speed: ", 100, 15, 1, increase_speed),
            Item("", "Sell speed: ", 100, -25, 1, minus_speed),
            Item("", "Increase luck: ", 2, 18, 1, increase_luck),
            Item("", "Sell luck: ", 2, -32, 1, minus_luck),
            Item("", "Add health recover after kill: ",
                 5, 12, 1, increase_kill_recover),
            Item("", "Increase Pistol damage: ",
                 10, 9, 1, self.increase_pistol_damage),
            Item("", "Increase Pistol damage: ",
                 10, 9, 1, self.increase_pistol_damage),
            Item("", "Reduce Pistol CD: ",
                 2, 14, 1, self.increase_pistol_speed),
            Item("", "Increase Pistol attack range: ",
                 5, 16, 1, self.increase_pistol_range),
            self.add_uzi_item,
        ]

        self.is_explosion_added = False
        self.explosion_item_list = [
            Item("", "Add explosion damage: ",
                 5, 30, 1, increase_explosion_damage),
            Item("", "Add explosion damage: ",
                 5, 30, 1, increase_explosion_damage),
        ]
        self.uzi_item_list = [
            Item("", "Increase Uzi damage: ", 10,
                 21, 1, self.increase_uzi_damage),
            Item("", "Increase Uzi damage: ", 10,
                 21, 1, self.increase_uzi_damage),
            Item("", "Reduce Uzi CD: ", 2, 19, 1, self.increase_uzi_speed),
            Item("", "Increase Uzi attack range: ",
                 5, 20, 1, self.increase_uzi_range),
            Item("", "Reduce Uzi energy cost: ",
                 1, 18, 1, self.reduce_uzi_cost),
            Item("", "Sell Uzi", 0, -30, -1, self.sell_uzi),
        ]
        self.shotgun_item_list = [
            Item("", "Increase Shotgun damage: ", 10,
                 36, 1, self.increase_shotgun_damage),
            Item("", "Increase Shotgun damage: ", 10,
                 36, 1, self.increase_shotgun_damage),
            Item("", "Reduce Shotgun CD: ", 2, 21,
                 1, self.increase_shotgun_speed),
            Item("", "Increase Shotgun attack range: ",
                 5, 28, 1, self.increase_shotgun_range),
            Item("", "Reduce Shotgun energy cost: ",
                 1, 24, 1, self.reduce_shotgun_cost),
            Item("", "Sell Shotgun", 0, -42, -1, self.sell_shotgun),
            Item("", "Increase Shotgun bullets: ", 1,
                 26, 1, self.increase_shotgun_bullets)
        ]
        self.rocket_item_list = [
            Item("", "Reduce Rocket CD: ", 2, 32,
                 1, self.increase_rocket_speed),
            Item("", "Increase Rocket attack range: ",
                 5, 35, 1, self.increase_rocket_range),
            Item("", "Reduce Rocket energy cost: ",
                 1, 28, 1, self.reduce_rocket_cost),
            Item("", "Sell Rocket", 0, -56, -1, self.sell_rocket),
            # Item("", "Increase Rocket bullets:", 1,
            #      52, 1, self.increase_rocket_bullets)
        ]
        self.wall_item_list = [
            Item("", "Reduce Wall energy cost: ", 1, 16,
                 1, self.reduce_wall_cost),
            Item("", "Sell Wall", 0, -28,
                 -1, self.sell_wall),
            Item("", "Increase Wall durability: ", 20, 24,
                 1, self.add_wall_durability),
        ]
        self.barrel_item_list = [
            Item("", "Reduce Barrel energy cost: ", 1, 35,
                 1, self.reduce_barrel_cost),
            Item("", "Sell Barrel", 0, -52, -1, self.sell_barrel),
        ]
        self.mine_item_list = [
            Item("", "Reduce Mine energy cost: ", 1, 28,
                 1, self.reduce_mine_cost),
            Item("", "Sell Mine: ", 0, -49, -1, self.sell_mine),
        ]

        self.cur_item_list = []
        self.cur_item_list.extend(self.default_item_list)

    def generate_item(self, item: Item, wave: int, player: Player, lang) -> Item:
        # Calculate the actual cost
        actual_cost = item.cost * wave * 2
        description = lang.ItemText[item.description]

        # Deal with no-quality items
        if item.quality == -1:
            return Item(item.image_path, description, item.value,
                        actual_cost, item.quality, item.equip)

        # Randomly generate quality with luck
        rand_quality = random.randrange(0, 99)
        actual_quality = 0
        if rand_quality < 5 + wave + player.luck:  # 5% base
            actual_quality = 3
        elif rand_quality >= 5 + wave + player.luck and rand_quality < 5 + 2 * (wave + player.luck):
            actual_quality = 2
        else:
            actual_quality = 1
        actual_cost *= actual_quality

        real_value = 0
        if actual_quality == 1:
            real_value = item.value
        elif actual_quality == 2:
            real_value = item.value * 2
        else:
            real_value = item.value * 4

        return Item(item.image_path,
                    description + str(real_value),
                    real_value,
                    actual_cost,
                    actual_quality,
                    item.equip
                    )

    def get_items(self, wave: int, player: Player, lang) -> list:
        tmp_list = random.sample(self.cur_item_list, 4)
        items = []
        for i in tmp_list:
            items.append(self.generate_item(i, wave, player, lang))
        return items

    def update_item_list(self, wave: int, player: Player) -> None:
        if (wave >= 3 and player.weapons.count(self.shotgun) == 0
                and self.cur_item_list.count(self.add_shotgun_item) == 0):
            self.cur_item_list.append(self.add_shotgun_item)
        if (wave >= 4 and player.weapons.count(self.wall) == 0
                and self.cur_item_list.count(self.add_wall_item) == 0):
            self.cur_item_list.append(self.add_wall_item)
        if (wave >= 5 and player.weapons.count(self.barrel) == 0
                and self.cur_item_list.count(self.add_barrel_item) == 0):
            self.cur_item_list.append(self.add_barrel_item)
        if (wave >= 6 and player.weapons.count(self.mine) == 0
                and self.cur_item_list.count(self.add_mine_item) == 0):
            self.cur_item_list.append(self.add_mine_item)
        if (wave >= 7 and player.weapons.count(self.rocket) == 0
                and self.cur_item_list.count(self.add_rocket_item) == 0):
            self.cur_item_list.append(self.add_rocket_item)

    # Pistol items

    def increase_pistol_damage(self, item: Item, player: Player) -> bool:
        self.pistol.damage += item.value
        return True

    def increase_pistol_speed(self, item: Item, player: Player) -> bool:
        self.pistol.cd_max = max(self.pistol.cd_max - item.value, Utils.CD_MIN)
        return True

    def increase_pistol_range(self, item: Item, player: Player) -> bool:
        self.pistol.life_span += item.value
        return True

    # Uzi items

    def add_uzi(self, item: Item, player: Player) -> bool:
        player.add_weapon(self.uzi)
        self.cur_item_list.remove(self.add_uzi_item)
        self.cur_item_list.extend(self.uzi_item_list)
        return True

    def increase_uzi_damage(self, item: Item, player: Player) -> bool:
        self.uzi.damage += item.value
        return True

    def increase_uzi_speed(self, item: Item, player: Player) -> bool:
        self.uzi.cd_max = max(self.uzi.cd_max - item.value, Utils.CD_MIN)
        return True

    def increase_uzi_range(self, item: Item, player: Player) -> bool:
        self.uzi.life_span += item.value
        return True

    def reduce_uzi_cost(self, item: Item, player: Player) -> bool:
        self.uzi.cost = max(self.uzi.cost - item.value, 0)
        return True

    def sell_uzi(self, item: Item, player: Player) -> bool:
        player.weapons.remove(self.uzi)
        self.uzi = weapon.Uzi()
        for i in self.uzi_item_list:
            self.cur_item_list.remove(i)
        self.cur_item_list.append(self.add_uzi_item)
        return True

    # Shotgun items

    def add_shotgun(self, item: Item, player: Player) -> bool:
        player.add_weapon(self.shotgun)
        self.cur_item_list.remove(self.add_shotgun_item)
        self.cur_item_list.extend(self.shotgun_item_list)
        return True

    def increase_shotgun_damage(self, item: Item, player: Player) -> bool:
        self.shotgun.damage += item.value
        return True

    def increase_shotgun_speed(self, item: Item, player: Player) -> bool:
        self.shotgun.cd_max = max(
            self.shotgun.cd_max - item.value, Utils.CD_MIN)
        return True

    def increase_shotgun_range(self, item: Item, player: Player) -> bool:
        self.shotgun.life_span += item.value
        return True

    def reduce_shotgun_cost(self, item: Item, player: Player) -> bool:
        self.shotgun.cost = max(self.shotgun.cost - item.value, 0)
        return True

    def sell_shotgun(self, item: Item, player: Player) -> bool:
        player.weapons.remove(self.shotgun)
        self.shotgun = weapon.Shotgun()
        for i in self.shotgun_item_list:
            self.cur_item_list.remove(i)
        self.cur_item_list.append(self.add_shotgun_item)
        return True

    def increase_shotgun_bullets(self, item: Item, player: Player) -> bool:
        self.shotgun.bullet_num += item.value
        return True

    # Rocket items

    def add_rocket(self, item: Item, player: Player) -> bool:
        if self.is_explosion_added == False:
            self.is_explosion_added = True
            self.cur_item_list.extend(self.explosion_item_list)
        player.add_weapon(self.rocket)
        self.cur_item_list.remove(self.add_rocket_item)
        self.cur_item_list.extend(self.rocket_item_list)
        return True

    def increase_rocket_speed(self, item: Item, player: Player) -> bool:
        self.rocket.cd_max = max(self.rocket.cd_max - item.value, Utils.CD_MIN)
        return True

    def increase_rocket_range(self, item: Item, player: Player) -> bool:
        self.rocket.life_span += item.value
        return True

    def reduce_rocket_cost(self, item: Item, player: Player) -> bool:
        self.rocket.cost = max(self.rocket.cost - item.value, 0)
        return True

    def sell_rocket(self, item: Item, player: Player) -> bool:
        player.weapons.remove(self.rocket)
        self.rocket = weapon.Rocket()
        for i in self.rocket_item_list:
            self.cur_item_list.remove(i)
        self.cur_item_list.append(self.add_rocket_item)

        if (player.weapons.count(self.barrel) == 0 and
                player.weapons.count(self.mine) == 0):
            for i in self.explosion_item_list:
                self.cur_item_list.remove(i)
            self.is_explosion_added = False

        return True

    # TODO: add fix or limit for the rocket
    # def increase_rocket_bullets(self, item: Item, player: Player) -> bool:
    #     self.rocket.bullet_num += item.value
    #     return True

    # PlacedWall items

    def add_wall(self, item: Item, player: Player) -> bool:
        player.add_weapon(self.wall)
        self.cur_item_list.remove(self.add_wall_item)
        self.cur_item_list.extend(self.wall_item_list)
        return True

    def reduce_wall_cost(self, item: Item, player: Player) -> bool:
        self.wall.cost = max(self.wall.cost - item.value, 0)
        return True

    def sell_wall(self, item: Item, player: Player) -> bool:
        player.weapons.remove(self.wall)
        self.wall = weapon.PlacedWall()
        for i in self.wall_item_list:
            self.cur_item_list.remove(i)
        self.cur_item_list.append(self.add_wall_item)
        return True

    def add_wall_durability(self, item: Item, player: Player) -> bool:
        self.wall.health_max += item.value
        return True

    # Barrel items

    def add_barrel(self, item: Item, player: Player) -> bool:
        if self.is_explosion_added == False:
            self.is_explosion_added = True
            self.cur_item_list.extend(self.explosion_item_list)
        player.add_weapon(self.barrel)
        self.cur_item_list.remove(self.add_barrel_item)
        self.cur_item_list.extend(self.barrel_item_list)
        return True

    def reduce_barrel_cost(self, item: Item, player: Player) -> bool:
        self.barrel.cost = max(self.barrel.cost - item.value, 0)
        return True

    def sell_barrel(self, item: Item, player: Player) -> bool:
        player.weapons.remove(self.barrel)
        self.barrel = weapon.Barrel()
        for i in self.barrel_item_list:
            self.cur_item_list.remove(i)
        self.cur_item_list.append(self.add_barrel_item)

        if (player.weapons.count(self.rocket) == 0 and
                player.weapons.count(self.mine) == 0):
            for i in self.explosion_item_list:
                self.cur_item_list.remove(i)
            self.is_explosion_added = False

        return True

    # Mine items

    def add_mine(self, item: Item, player: Player) -> bool:
        if self.is_explosion_added == False:
            self.is_explosion_added = True
            self.cur_item_list.extend(self.explosion_item_list)
        player.add_weapon(self.mine)
        self.cur_item_list.remove(self.add_mine_item)
        self.cur_item_list.extend(self.mine_item_list)
        return True

    def reduce_mine_cost(self, item: Item, player: Player) -> bool:
        self.mine.cost = max(self.mine.cost - item.value, 0)
        return True

    def sell_mine(self, item: Item, player: Player) -> bool:
        player.weapons.remove(self.mine)
        self.mine = weapon.Mine()
        for i in self.mine_item_list:
            self.cur_item_list.remove(i)
        self.cur_item_list.append(self.add_mine_item)

        if (player.weapons.count(self.barrel) == 0 and
                player.weapons.count(self.rocket) == 0):
            for i in self.explosion_item_list:
                self.cur_item_list.remove(i)
            self.is_explosion_added = False

        return True
