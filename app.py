from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# Domain models (OOП) — использую классы, а не словари.
try:
    from models import Spaceship, Mission  # CrewMember exists but is not used in API endpoints
except Exception as e:
    Spaceship = None  # type: ignore
    Mission = None    # type: ignore

# In-memory storage (for learning/demo). Data will be reset on restart.
spaceships = []  # list[Spaceship]
missions = []    # list[Mission]

ALLOWED_MISSION_GOALS = {"exploration", "defense"}


@app.route('/api/v1', methods=['GET'])
def home():
    return "Сервер работает!", 200


# ---------------------------
# Helpers
# ---------------------------

def _next_spaceship_id() -> int:
    return (max((s.spaceship_id for s in spaceships), default=0) + 1)


def _next_mission_id() -> int:
    return (max((m.mission_id for m in missions), default=0) + 1)


def _find_spaceship(spaceship_id: int):
    return next((s for s in spaceships if s.spaceship_id == spaceship_id), None)


def _find_mission(mission_id: int):
    return next((m for m in missions if m.mission_id == mission_id), None)


def spaceship_to_dict(s) -> dict:
    # Prefer model method if present
    if hasattr(s, "to_dict") and callable(getattr(s, "to_dict")):
        return s.to_dict()
    # Fallback mapping
    type_value = getattr(s, "type", None)
    if type_value is None:
        type_value = getattr(s, "type_", None)
    return {
        "spaceship_id": getattr(s, "spaceship_id"),
        "name": getattr(s, "name"),
        "type": type_value,
        "status": getattr(s, "status"),
    }


def mission_to_dict(m) -> dict:
    if hasattr(m, "to_dict") and callable(getattr(m, "to_dict")):
        return m.to_dict()

    # mission.spaceships may contain objects or ids; normalize to ids
    ships = getattr(m, "spaceships", [])
    ship_ids = []
    for item in ships:
        if isinstance(item, int):
            ship_ids.append(item)
        else:
            ship_ids.append(getattr(item, "spaceship_id"))

    return {
        "mission_id": getattr(m, "mission_id"),
        "name": getattr(m, "name"),
        "goal": getattr(m, "goal"),
        "status": getattr(m, "status"),
        "spaceships": ship_ids,
    }


# ---------------------------
# Spaceships endpoints
# ---------------------------

@app.route('/api/v1/spaceships', methods=['GET'])
def get_spaceships():
    return jsonify([spaceship_to_dict(s) for s in spaceships]), 200


@app.route('/api/v1/spaceships', methods=['POST'])
def create_spaceship():
    if Spaceship is None:
        abort(500)

    data = request.get_json(silent=True)
    if not data or 'name' not in data or 'type' not in data:
        abort(400)

    next_id = _next_spaceship_id()

    name = data['name']
    ship_type = data['type']
    status = data.get('status', 'available')

    # Some implementations use `type_` in __init__. Try both styles.
    try:
        spaceship = Spaceship(spaceship_id=next_id, name=name, type_=ship_type, status=status)
    except TypeError:
        spaceship = Spaceship(next_id, name, ship_type, status)

    spaceships.append(spaceship)
    return jsonify(spaceship_to_dict(spaceship)), 201


@app.route('/api/v1/spaceships/<int:spaceship_id>', methods=['PUT'])
def update_spaceship_status(spaceship_id: int):
    data = request.get_json(silent=True)
    if not data or 'status' not in data:
        abort(400)

    spaceship = _find_spaceship(spaceship_id)
    if spaceship is None:
        abort(404)

    new_status = data['status']

    # Prefer model method if present
    if hasattr(spaceship, "update_status") and callable(getattr(spaceship, "update_status")):
        spaceship.update_status(new_status)
    else:
        spaceship.status = new_status

    return jsonify(spaceship_to_dict(spaceship)), 200


@app.route('/api/v1/spaceships/<int:spaceship_id>', methods=['DELETE'])
def delete_spaceship(spaceship_id: int):
    spaceship = _find_spaceship(spaceship_id)
    if spaceship is None:
        abort(404)

    spaceships.remove(spaceship)

    # Also remove this ship from all missions
    for m in missions:
        ships = getattr(m, "spaceships", [])
        # If stored as objects
        if ships and not isinstance(ships[0], int):
            m.spaceships = [s for s in ships if getattr(s, "spaceship_id") != spaceship_id]
        else:
            m.spaceships = [sid for sid in ships if sid != spaceship_id]

    return jsonify({'deleted': spaceship_id}), 200


# ---------------------------
# Missions endpoints
# ---------------------------

@app.route('/api/v1/missions', methods=['GET'])
def get_missions():
    return jsonify([mission_to_dict(m) for m in missions]), 200


@app.route('/api/v1/missions', methods=['POST'])
def create_mission():
    if Mission is None:
        abort(500)

    data = request.get_json(silent=True)
    if not data or 'name' not in data or 'goal' not in data:
        abort(400)

    goal = data['goal']
    if goal not in ALLOWED_MISSION_GOALS:
        abort(400)

    next_id = _next_mission_id()

    name = data['name']
    status = data.get('status', 'planned')

    try:
        mission = Mission(mission_id=next_id, name=name, goal=goal, status=status)
    except TypeError:
        mission = Mission(next_id, name, goal, status)

    # Ensure spaceships container exists
    if not hasattr(mission, "spaceships"):
        mission.spaceships = []

    missions.append(mission)
    return jsonify(mission_to_dict(mission)), 201


@app.route('/api/v1/missions/<int:mission_id>/spaceships', methods=['POST'])
def add_spaceship_to_mission(mission_id: int):
    data = request.get_json(silent=True)
    if not data or 'spaceship_id' not in data:
        abort(400)

    mission = _find_mission(mission_id)
    if mission is None:
        abort(404)

    spaceship_id = data['spaceship_id']
    spaceship = _find_spaceship(spaceship_id)
    if spaceship is None:
        abort(404)

    # Prefer model method if present
    if hasattr(mission, "add_spaceship") and callable(getattr(mission, "add_spaceship")):
        mission.add_spaceship(spaceship)
    else:
        if not hasattr(mission, "spaceships"):
            mission.spaceships = []
        # Avoid duplicates
        existing_ids = [getattr(s, "spaceship_id") if not isinstance(s, int) else s for s in mission.spaceships]
        if spaceship_id not in existing_ids:
            mission.spaceships.append(spaceship)

    return jsonify(mission_to_dict(mission)), 200


# ---------------------------
# Error handlers
# ---------------------------


@app.errorhandler(500)
def internal_error(_error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found_error(_error):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(400)
def bad_request_error(_error):
    return jsonify({'error': 'Bad request'}), 400


if __name__ == "__main__":
    app.run(debug=True)