class Spaceship:
    def __init__(self, spaceship_id, name, type_, status='available'):
        self.spaceship_id = spaceship_id
        self.name = name
        self.type_ = type_
        self.status = status

    def update_status(self, new_status):
        self.status = new_status

    def to_dict(self):
        return {
            'spaceship_id': self.spaceship_id,
            'name': self.name,
            'type': self.type_,
            'status': self.status,
        }


class Mission:
    def __init__(self, mission_id, name, goal, status="planned"):
        self.mission_id = mission_id
        self.name = name
        self.goal = goal
        self.status = status
        self.spaceships = []

    def add_spaceship(self, spaceship):
        # Accept either a Spaceship object or an int id
        spaceship_id = getattr(spaceship, 'spaceship_id', spaceship)

        # Prevent duplicates
        existing_ids = [getattr(s, 'spaceship_id', s) for s in self.spaceships]
        if spaceship_id in existing_ids:
            return

        self.spaceships.append(spaceship)

    def to_dict(self):
        # Store spaceship objects internally, but serialize as a list of ids
        spaceship_ids = []
        for s in self.spaceships:
            if hasattr(s, 'spaceship_id'):
                spaceship_ids.append(s.spaceship_id)
            else:
                # fallback if ids are stored directly
                spaceship_ids.append(s)

        return {
            'mission_id': self.mission_id,
            'name': self.name,
            'goal': self.goal,
            'status': self.status,
            'spaceships': spaceship_ids,
        }


class CrewMember:
    def __init__(self, member_id, name, role):
        self.member_id = member_id
        self.name = name
        self.role = role

    def to_dict(self):
        return {
            'member_id': self.member_id,
            'name': self.name,
            'role': self.role,
        }
