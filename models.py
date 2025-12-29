class Spaceship:
    def __init__(self, spaceship_id, name, type_, status='available'):
        self.spaceship_id = spaceship_id
        self.name = name
        self.type_ = type_
        self.status = status

    def update_status(self, new_status):
        self.status = new_status


class Mission:
    def __init__(self, mission_id, name, goal, status="planned"):
        self.mission_id = mission_id
        self.name = name
        self.goal = goal
        self.status = status
        self.spaceships = []

    def add_spaceship(self, spaceship):
        self.spaceships.append(spaceship)


class CrewMember:
    def __init__(self, member_id, name, role):
        self.member_id = member_id
        self.name = name
        self.role = role

