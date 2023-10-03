# BoxHead2D

A simple BoxHead Survivor game in 2D with [Python Arcade](https://api.arcade.academy/en/latest/index.html). 

This is a "rogue-lite", "top-down shooter" game. The core gameplay is a combination of an old 3D BoxHead zombie game and a recent popular survivor-style game.

Requirements for running in the terminal:

- Python 3.6+
- Arcade library `pip install arcade` or `pip3 install arcade`

Run the game with the command:
```python
python app.py # Windows environment
python3 app.py # Linux or Mac
```

### Design Document

#### Player

| Characters | Health | Energy | Money | Speed | Kill recover | Explosion Damage | Luck |
|------------|--------|--------|-------|-------|--------------|------------------|------|
| Player     |   1000 |      0 |     0 |  1600 |            5 |               20 |    6 |

#### Weapons

| Weapons    | Damage           | Energy cost | CD | Attack range (bullet life span) | Bullet speed | Bullet number | Health |
|------------|------------------|-------------|----|---------------------------------|--------------|---------------|--------|
| Pistol     |               30 |           0 | 30 |                              20 |           25 | \             | \      |
| Uzi        |               30 |           3 | 20 |                              25 |           30 | \             | \      |
| Shotgun    | 40*3             |          12 | 50 |                              10 |           25 |             3 | \      |
| Rocket     | explosion damage |          20 | 40 |                              15 |           32 |             1 | \      |
| PlacedWall | \                |           5 |  4 |                                 | \            | \             |    200 |
| Barrel     | explosion damage |          20 |  4 |                                 | \            | \             |      0 |
| Mine       | explosion damage |          20 |  4 |                                 | \            | \             |      0 |

#### Enemies

| Enemies   | Health | Hit Damage | Bullet damage | Speed | CD  | Attack range | Bullet speed |
|-----------|--------|------------|---------------|-------|-----|--------------|--------------|
| White     |    100 |         20 | \             |   800 | \   | \            | \            |
| Red       |    300 |         20 |            30 |   800 | 120 |          200 |            6 |
| Crack     |    200 |         40 | \             |  1000 | \   | \            | \            |
| Big Mouth |    150 |         20 | 50*2          |   800 |  70 |          300 |            7 |
| Crash     |    100 |         40 | \             |  1000 | \   |          200 | \            |
| Tank      |    400 |         60 | \             |   600 | \   |          200 | \            |

#### Items

#### Round




### Notes:

When running on mac os, please disable popup showing accented characters when holding a key.
Run the command `defaults write -g ApplePressAndHoldEnabled -bool false`.
Link to the [reference](https://apple.stackexchange.com/questions/332769/macos-disable-popup-showing-accented-characters-when-holding-down-a-key)
