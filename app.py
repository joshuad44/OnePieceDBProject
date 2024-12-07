from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:topher14@localhost:3306/one_piece_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Define models
class Crew(db.Model):
    __tablename__ = 'Crew'
    crew_id = db.Column(db.Integer, primary_key=True)
    crew_name = db.Column(db.String(100), nullable=False)
    captain = db.Column(db.String(100), nullable=True)
    ship = db.Column(db.String(100), nullable=True)

class DevilFruit(db.Model):
    __tablename__ = 'Devil_Fruit'
    devil_fruit_id = db.Column(db.Integer, primary_key=True)
    devil_fruit_name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=True)
    power = db.Column(db.String(100), nullable=True)

class OPCharacter(db.Model):
    __tablename__ = 'OPCharacter'
    character_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    crew_id = db.Column(db.Integer, db.ForeignKey('Crew.crew_id'), nullable=True)
    devil_fruit_id = db.Column(db.Integer, db.ForeignKey('Devil_Fruit.devil_fruit_id'), nullable=True)
    first_episode_id = db.Column(db.Integer, nullable=True)

class Episode(db.Model):
    __tablename__ = 'Episode'
    episode_id = db.Column(db.Integer, primary_key=True)
    episode_name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    arc_name = db.Column(db.String(100), db.ForeignKey('Arc.arc_name'))

class Arc(db.Model):
    __tablename__ = 'Arc'
    arc_name = db.Column(db.String(100), primary_key=True)
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer, nullable=False)

# Routes for Characters
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/devil_fruits')
def devil_fruits():
    return render_template('devil_fruit.html')


@app.route('/api/characters', methods=['GET', 'POST'])
def manage_characters():
    if request.method == 'GET':
        characters = db.session.query(OPCharacter, Crew, DevilFruit) \
            .outerjoin(Crew, OPCharacter.crew_id == Crew.crew_id) \
            .outerjoin(DevilFruit, OPCharacter.devil_fruit_id == DevilFruit.devil_fruit_id).all()
        return jsonify([{
            'character_id': c.OPCharacter.character_id,
            'name': c.OPCharacter.name,
            'crew_name': c.Crew.crew_name if c.Crew else None,
            'devil_fruit_name': c.DevilFruit.devil_fruit_name if c.DevilFruit else None,
            'first_episode_id': c.OPCharacter.first_episode_id
        } for c in characters])
    elif request.method == 'POST':
        data = request.json
        new_character = OPCharacter(
            name=data['name'],
            crew_id=data.get('crew_id'),
            devil_fruit_id=data.get('devil_fruit_id'),
            first_episode_id=data.get('first_episode_id')
        )
        db.session.add(new_character)
        db.session.commit()
        return jsonify({'message': 'Character added successfully!'}), 201

@app.route('/api/characters/<int:character_id>', methods=['GET', 'PUT', 'DELETE'])
def update_delete_character(character_id):
    character = OPCharacter.query.get_or_404(character_id)

    if request.method == 'GET':
        crew = Crew.query.get(character.crew_id)
        devil_fruit = DevilFruit.query.get(character.devil_fruit_id)
        return jsonify({
            'character_id': character.character_id,
            'name': character.name,
            'crew_name': crew.crew_name if crew else None,
            'devil_fruit_name': devil_fruit.devil_fruit_name if devil_fruit else None,
            'first_episode_id': character.first_episode_id
        })

    if request.method == 'PUT':
        data = request.json
        character.name = data['name']
        character.crew_id = data.get('crew_id')
        character.devil_fruit_id = data.get('devil_fruit_id')
        character.first_episode_id = data.get('first_episode_id')
        db.session.commit()
        return jsonify({'message': 'Character updated successfully!'})

    if request.method == 'DELETE':
        db.session.delete(character)
        db.session.commit()
        return jsonify({'message': 'Character deleted successfully!'})

@app.route('/api/characters/save', methods=['POST'])
def save_character():
    """
    This route handles both creating a new character and editing an existing one.
    If 'character_id' is provided in the request, it updates the existing character.
    Otherwise, it creates a new character.
    """
    data = request.json

    # If character_id is provided, edit the existing character
    if 'character_id' in data and data['character_id']:
        character = OPCharacter.query.get_or_404(data['character_id'])
        character.name = data['name']
        character.crew_id = data.get('crew_id')
        character.devil_fruit_id = data.get('devil_fruit_id')
        character.first_episode_id = data.get('first_episode_id')
        db.session.commit()
        return jsonify({'message': 'Character updated successfully!'})

    # Otherwise, create a new character
    else:
        new_character = OPCharacter(
            name=data['name'],
            crew_id=data.get('crew_id'),
            devil_fruit_id=data.get('devil_fruit_id'),
            first_episode_id=data.get('first_episode_id')
        )
        db.session.add(new_character)
        db.session.commit()
        return jsonify({'message': 'Character added successfully!'})

@app.route('/api/characters/search', methods=['GET'])
def search_characters():
    query = request.args.get('query', '').lower()

    # Join OPCharacter with Crew and DevilFruit for search
    results = db.session.query(OPCharacter, Crew, DevilFruit) \
        .outerjoin(Crew, OPCharacter.crew_id == Crew.crew_id) \
        .outerjoin(DevilFruit, OPCharacter.devil_fruit_id == DevilFruit.devil_fruit_id) \
        .filter(
            db.or_(
                OPCharacter.name.ilike(f"%{query}%"),
                Crew.crew_name.ilike(f"%{query}%"),
                DevilFruit.devil_fruit_name.ilike(f"%{query}%")
            )
        ).all()

    # Format results into a JSON-friendly format
    return jsonify([{
        'character_id': c.OPCharacter.character_id,
        'name': c.OPCharacter.name,
        'crew_name': c.Crew.crew_name if c.Crew else None,
        'devil_fruit_name': c.DevilFruit.devil_fruit_name if c.DevilFruit else None,
        'first_episode_id': c.OPCharacter.first_episode_id
    } for c in results])

# Route to get all devil fruits
@app.route('/api/devil_fruits', methods=['GET'])
def get_devil_fruits():
    devil_fruits = DevilFruit.query.all()
    return jsonify([{
        'devil_fruit_id': fruit.devil_fruit_id,
        'devil_fruit_name': fruit.devil_fruit_name,
        'type': fruit.type,
        'power': fruit.power
    } for fruit in devil_fruits])

# Route to add a new devil fruit
@app.route('/api/devil_fruits', methods=['POST'])
def add_devil_fruit():
    data = request.json
    devil_fruit_name = data.get('devil_fruit_name')
    devil_fruit_type = data.get('type')
    devil_fruit_power = data.get('power')

    # Check if the devil fruit already exists
    if DevilFruit.query.filter_by(devil_fruit_name=devil_fruit_name).first():
        return jsonify({'message': 'Devil Fruit already exists!'}), 400

    new_devil_fruit = DevilFruit(
        devil_fruit_name=devil_fruit_name,
        type=devil_fruit_type,
        power=devil_fruit_power
    )
    db.session.add(new_devil_fruit)
    db.session.commit()
    return jsonify({'message': 'Devil Fruit added successfully!'}), 201

# Route to handle specific devil fruit by ID
@app.route('/api/devil_fruits/<int:devil_fruit_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_devil_fruit(devil_fruit_id):
    devil_fruit = DevilFruit.query.get_or_404(devil_fruit_id)
    
    if request.method == 'GET':
        # Fetch and return the devil fruit details
        return jsonify({
            'devil_fruit_id': devil_fruit.devil_fruit_id,
            'devil_fruit_name': devil_fruit.devil_fruit_name,
            'type': devil_fruit.type,
            'power': devil_fruit.power
        })

    if request.method == 'PUT':
        # Update the devil fruit
        data = request.json
        devil_fruit.devil_fruit_name = data.get('devil_fruit_name', devil_fruit.devil_fruit_name)
        devil_fruit.type = data.get('type', devil_fruit.type)
        devil_fruit.power = data.get('power', devil_fruit.power)
        db.session.commit()
        return jsonify({'message': 'Devil Fruit updated successfully!'})

    if request.method == 'DELETE':
        # Delete the devil fruit
        db.session.delete(devil_fruit)
        db.session.commit()
        return jsonify({'message': 'Devil Fruit deleted successfully!'})

# Route to search devil fruits
@app.route('/api/devil_fruits/search', methods=['GET'])
def search_devil_fruits():
    query = request.args.get('query', '').lower()

    results = DevilFruit.query.filter(
        db.or_(
            DevilFruit.devil_fruit_name.ilike(f"%{query}%"),
            DevilFruit.type.ilike(f"%{query}%"),
            DevilFruit.power.ilike(f"%{query}%")
        )
    ).all()

    return jsonify([{
        'devil_fruit_id': fruit.devil_fruit_id,
        'devil_fruit_name': fruit.devil_fruit_name,
        'type': fruit.type,
        'power': fruit.power
    } for fruit in results])

# Route to render Crew management page
@app.route('/crews')
def crews():
    return render_template('crews.html')

# Route to get all crews
@app.route('/api/crews', methods=['GET'])
def get_crews():
    crews = Crew.query.all()
    return jsonify([{
        'crew_id': crew.crew_id,
        'crew_name': crew.crew_name,
        'captain': crew.captain,
        'ship': crew.ship
    } for crew in crews])

# Route to add a new crew
@app.route('/api/crews', methods=['POST'])
def add_crew():
    data = request.json
    crew_name = data.get('crew_name')
    captain = data.get('captain')
    ship = data.get('ship')

    # Check if the crew already exists
    if Crew.query.filter_by(crew_name=crew_name).first():
        return jsonify({'message': 'Crew already exists!'}), 400

    new_crew = Crew(
        crew_name=crew_name,
        captain=captain,
        ship=ship
    )
    db.session.add(new_crew)
    db.session.commit()
    return jsonify({'message': 'Crew added successfully!'}), 201

# Route to handle specific crew by ID
@app.route('/api/crews/<int:crew_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_crew(crew_id):
    crew = Crew.query.get_or_404(crew_id)
    
    if request.method == 'GET':
        # Fetch and return the crew details
        return jsonify({
            'crew_id': crew.crew_id,
            'crew_name': crew.crew_name,
            'captain': crew.captain,
            'ship': crew.ship
        })

    if request.method == 'PUT':
        # Update the crew
        data = request.json
        crew.crew_name = data.get('crew_name', crew.crew_name)
        crew.captain = data.get('captain', crew.captain)
        crew.ship = data.get('ship', crew.ship)
        db.session.commit()
        return jsonify({'message': 'Crew updated successfully!'})

    if request.method == 'DELETE':
        # Delete the crew
        db.session.delete(crew)
        db.session.commit()
        return jsonify({'message': 'Crew deleted successfully!'})

# Route to search crews
@app.route('/api/crews/search', methods=['GET'])
def search_crews():
    query = request.args.get('query', '').lower()

    results = Crew.query.filter(
        db.or_(
            Crew.crew_name.ilike(f"%{query}%"),
            Crew.captain.ilike(f"%{query}%"),
            Crew.ship.ilike(f"%{query}%")
        )
    ).all()

    return jsonify([{
        'crew_id': crew.crew_id,
        'crew_name': crew.crew_name,
        'captain': crew.captain,
        'ship': crew.ship
    } for crew in results])


@app.route('/timeline')
def show_timeline():
    # Query to get the unique arc names and their start and end years based on the Episode table
    arcs = db.session.query(
        Episode.arc_name,
        db.func.min(Episode.year).label('start_year'),
        db.func.max(Episode.year).label('end_year')
    ).group_by(Episode.arc_name).all()

    # Convert arcs to a list of dictionaries for easy JSON serialization
    arcs_list = [{'arc_name': arc.arc_name, 'start_year': arc.start_year, 'end_year': arc.end_year} for arc in arcs]

    # Sort the arcs list by start year in ascending order
    arcs_list.sort(key=lambda arc: arc['start_year'])

    # Get all episodes data and convert to a list of dictionaries
    episodes = Episode.query.all()
    episodes_list = [{'episode_id': e.episode_id, 'episode_name': e.episode_name, 'year': e.year, 'arc_name': e.arc_name} for e in episodes]

    # Render the timeline page with the arcs and episodes data
    return render_template('timeline.html', arcs=arcs_list, episodes=episodes_list)

@app.route('/api/first_appearances')
def first_appearances():
    characters = db.session.query(OPCharacter, Episode).join(Episode, OPCharacter.first_episode_id == Episode.episode_id).all()
    appearances = [{
        'character_name': c.name,
        'first_episode_name': e.episode_name,
        'first_episode_year': e.year
    } for c, e in characters]
    return jsonify(appearances)

# New Route to Fetch First-Time Characters for a Specific Arc
@app.route('/api/first_time_characters/<arc_name>', methods=['GET'])
def get_first_time_characters(arc_name):
    # Query to find characters whose first appearance is in the specified arc
    characters = db.session.query(OPCharacter.name).join(Episode, OPCharacter.first_episode_id == Episode.episode_id).filter(Episode.arc_name == arc_name).all()
    
    # Extract the character names from the query result
    character_names = [character.name for character in characters]
    
    return jsonify(character_names)

@app.route('/one_piece_analysis')
def one_piece_analysis():
    # Crew analysis
    crew_counts = db.session.query(
        Crew.crew_name,
        db.func.count(OPCharacter.character_id).label('character_count')
    ).join(OPCharacter, OPCharacter.crew_id == Crew.crew_id)\
     .group_by(Crew.crew_name).all()

    # Devil fruit analysis
    fruit_counts = db.session.query(
        DevilFruit.type,
        db.func.count(OPCharacter.character_id).label('character_count')
    ).join(OPCharacter, OPCharacter.devil_fruit_id == DevilFruit.devil_fruit_id)\
     .group_by(DevilFruit.type)\
     .order_by(db.func.count(OPCharacter.character_id).desc()).all()

    return render_template('one_piece_analysis.html', crew_counts=crew_counts, fruit_counts=fruit_counts)

@app.route('/api/popular_devil_fruits', methods=['GET'])
def popular_devil_fruits():
    fruit_counts = db.session.query(
        DevilFruit.type,
        db.func.count(OPCharacter.character_id).label('character_count')
    ).join(OPCharacter, OPCharacter.devil_fruit_id == DevilFruit.devil_fruit_id)\
     .group_by(DevilFruit.type)\
     .order_by(db.func.count(OPCharacter.character_id).desc()).all()

    return jsonify([{
        'type': f.type,
        'character_count': f.character_count
    } for f in fruit_counts])

if __name__ == '__main__':
    app.run(debug=True)
