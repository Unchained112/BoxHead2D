# BoxHead2D

A simple BoxHead game in 2D with [Python Arcade](https://api.arcade.academy/en/latest/index.html).

### Design Document

Player:
- Health: 100
- Energy: 200
- Health recover: 5 (after kill one enemy)

Enemy White:
- Health: 100
- Collide damage: 20

Enemy Red:
- Health: 200
- Collide damage: 20
- Shoot damage: 30

Weapons:
| Name       | Damage  | Attack Speed | Cost | CD (*/60 s) | Attack Range (life span) |
|------------|---------|--------------|------|-------------|--------------------------|
| Pistol     | 40      | 25           | 0    | 20          | 20                       |
| Uzi        | 30      | 30           | 2    | 10 or less? | 30                       |
| Shotgun    | 40 * 3  | 30           | 8    | 30          | 12                       |
| PlacedWall | 0       | \            | 6    | 10          | \                        |
| Barrel     | 10 * 24 | \            | 9    | 10          | \                        |

### Developer Notes

There is no game over as the gameplay design is not done yet.


### Notes:

When running on mac os, please disable popup showing accented characters when holding a key.
Run the command `defaults write -g ApplePressAndHoldEnabled -bool false`.
Link to the [reference](https://apple.stackexchange.com/questions/332769/macos-disable-popup-showing-accented-characters-when-holding-down-a-key)
