from character import Player


class Item:
    """Item to be bought in the shop."""

    def __init__(self):
        self.image_path = ""
        self.description = ""
        # Item quality: bronze: 1, sliver: 2, gold: 3
        self.quality = 1
        self.cost = 0

    def equip(self, player: Player) -> bool:
        """To be override. Return purchase succeeded or failed."""
        return True


