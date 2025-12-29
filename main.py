from models import Spaceship
from models import Mission

ship1 = Spaceship(1, 'Apollo', 'cargo')
ship2 = Spaceship(2, 'Apollo', 'cargo')

mission1 = Mission(1, 'Moon mission', 'Explore the Moon')
mission1.add_spaceship(ship1)
mission1.add_spaceship(ship2)

print(mission1.spaceships)
