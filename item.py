from character import Player

class item:
    """Item to be bouth in the shop."""

    def __init__(self):
        self.description = ""
        # Iteam quality: bronze: 1, sliver: 2, gold: 3
        self.quality = 1
        self.cost = 0

    def equip(self, player: Player) -> bool:
        """To be overriden. Return purchase succeeded or failed."""
        return True
