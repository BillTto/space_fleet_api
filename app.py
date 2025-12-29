from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# In-memory storage (for learning/demo). Data will be reset on restart.
spaceships: list[dict] = []
missions: list[dict] = []


@app.route('/api/v1', methods=['GET'])
def home():
    return "Сервер работает!", 200


# ---------------------------
# Spaceships endpoints
# ---------------------------

@app.route('/api/v1/spaceships', methods=['GET'])
def get_spaceships():
    return jsonify(spaceships), 200


@app.route('/api/v1/spaceships', methods=['POST'])
def create_spaceship():
    data = request.get_json(silent=True)
    if not data or 'name' not in data or 'type' not in data:
        abort(400)

    # very simple id generation for demo
    next_id = (max((s['spaceship_id'] for s in spaceships), default=0) + 1)

    spaceship = {
        'spaceship_id': next_id,
        'name': data['name'],
        'type': data['type'],
        'status': data.get('status', 'available'),
    }
    spaceships.append(spaceship)
    return jsonify(spaceship), 201


@app.route('/api/v1/spaceships/<int:spaceship_id>', methods=['PUT'])
def update_spaceship_status(spaceship_id: int):
    data = request.get_json(silent=True)
    if not data or 'status' not in data:
        abort(400)

    spaceship = next((s for s in spaceships if s['spaceship_id'] == spaceship_id), None)
    if spaceship is None:
        abort(404)

    spaceship['status'] = data['status']
    return jsonify(spaceship), 200


@app.route('/api/v1/spaceships/<int:spaceship_id>', methods=['DELETE'])
def delete_spaceship(spaceship_id: int):
    spaceship = next((s for s in spaceships if s['spaceship_id'] == spaceship_id), None)
    if spaceship is None:
        abort(404)

    spaceships.remove(spaceship)
    return jsonify({'deleted': spaceship_id}), 200


# ---------------------------
# Missions endpoints
# ---------------------------

@app.route('/api/v1/missions', methods=['GET'])
def get_missions():
    return jsonify(missions), 200


@app.route('/api/v1/missions', methods=['POST'])
def create_mission():
    data = request.get_json(silent=True)
    if not data or 'name' not in data or 'goal' not in data:
        abort(400)

    next_id = (max((m['mission_id'] for m in missions), default=0) + 1)

    mission = {
        'mission_id': next_id,
        'name': data['name'],
        'goal': data['goal'],
        'status': data.get('status', 'planned'),
        'spaceships': [],  # store spaceship_id values
    }
    missions.append(mission)
    return jsonify(mission), 201


@app.route('/api/v1/missions/<int:mission_id>/spaceships', methods=['POST'])
def add_spaceship_to_mission(mission_id: int):
    data = request.get_json(silent=True)
    if not data or 'spaceship_id' not in data:
        abort(400)

    mission = next((m for m in missions if m['mission_id'] == mission_id), None)
    if mission is None:
        abort(404)

    spaceship_id = data['spaceship_id']
    spaceship = next((s for s in spaceships if s['spaceship_id'] == spaceship_id), None)
    if spaceship is None:
        abort(404)

    if spaceship_id not in mission['spaceships']:
        mission['spaceships'].append(spaceship_id)

    return jsonify(mission), 200


# ---------------------------
# Error handlers
# ---------------------------

@app.errorhandler(404)
def not_found_error(_error):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(400)
def bad_request_error(_error):
    return jsonify({'error': 'Bad request'}), 400


if __name__ == "__main__":
    app.run(debug=True)