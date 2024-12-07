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
    crew_name = db.Column(db.String(100), primary_key=True)

class CrewWithDetails(db.Model):
    __tablename__ = 'Crew'
    __table_args__ = {'extend_existing': True}
    crew_name = db.Column(db.String(100), primary_key=True)
    captain = db.Column(db.String(100), nullable=True)
    ship = db.Column(db.String(100), nullable=True)

class DevilFruit(db.Model):
    __tablename__ = 'Devil_Fruit'
    devil_fruit_name = db.Column(db.String(100), primary_key=True)
    type = db.Column(db.String(100))  


class OPCharacter(db.Model):
    __tablename__ = 'OPCharacter'
    character_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    crew_name = db.Column(db.String(100), db.ForeignKey('Crew.crew_name'), nullable=True)
    devil_fruit_name = db.Column(db.String(100), db.ForeignKey('Devil_Fruit.devil_fruit_name'), nullable=True)
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

@app.route('/crew')
def crew():
    return render_template('crew.html')



@app.route('/api/characters', methods=['GET', 'POST'])
def manage_characters():
    if request.method == 'GET':
        characters = OPCharacter.query.all()
        return jsonify([{
            'character_id': c.character_id,
            'name': c.name,
            'crew_name': c.crew_name,
            'devil_fruit_name': c.devil_fruit_name,
            'first_episode_id': c.first_episode_id
        } for c in characters])
    elif request.method == 'POST':
        data = request.json
        new_character = OPCharacter(
            name=data['name'],
            crew_name=data.get('crew_name'),
            devil_fruit_name=data.get('devil_fruit_name'),
            first_episode_id=data.get('first_episode_id')
        )
        db.session.add(new_character)
        db.session.commit()
        return jsonify({'message': 'Character added successfully!'}), 201

@app.route('/api/characters/<int:character_id>', methods=['GET', 'PUT', 'DELETE'])
def update_delete_character(character_id):
    character = OPCharacter.query.get_or_404(character_id)

    if request.method == 'GET': 
        return jsonify({
            'character_id': character.character_id,
            'name': character.name,
            'crew_name': character.crew_name,
            'devil_fruit_name': character.devil_fruit_name,
            'first_episode_id': character.first_episode_id
        })
    
    if request.method == 'PUT':
        data = request.json
        character.name = data['name']
        character.crew_name = data.get('crew_name')
        character.devil_fruit_name = data.get('devil_fruit_name')
        character.first_episode_id = data.get('first_episode_id')
        db.session.commit()
        return jsonify({'message': 'Character updated successfully!'})
    
    if request.method == 'DELETE':
        db.session.delete(character)
        db.session.commit()
        return jsonify({'message': 'Character deleted successfully!'})


# Routes for Crews (Character Page)
@app.route('/api/crews', methods=['GET'])
def get_crews():
    crews = Crew.query.all()
    return jsonify([{'name': crew.crew_name} for crew in crews])

@app.route('/api/crews_with_details', methods=['GET'])
def get_crews_with_details():
    crews = CrewWithDetails.query.all()
    return jsonify([{
        'name': crew.crew_name,
        'captain': crew.captain,
        'ship': crew.ship
    } for crew in crews])

@app.route('/api/crews_with_details', methods=['POST'])
def add_crew_with_details():
    data = request.json
    crew_name = data['name']
    captain = data.get('captain')
    ship = data.get('ship')

    if not CrewWithDetails.query.filter_by(crew_name=crew_name).first():
        new_crew = CrewWithDetails(
            crew_name=crew_name,
            captain=captain,
            ship=ship
        )
        db.session.add(new_crew)
        db.session.commit()
    return jsonify({'message': 'Crew added successfully!'}), 201

@app.route('/api/crews_with_details/<string:crew_name>', methods=['GET', 'PUT', 'DELETE'])
def update_delete_crew_with_details(crew_name):
    crew = CrewWithDetails.query.get_or_404(crew_name)

    if request.method == 'GET': 
        return jsonify({
            'name': crew.crew_name,
            'captain': crew.captain,
            'ship': crew.ship
        })
    
    if request.method == 'PUT':
        data = request.json
        crew.crew_name = data['name']
        crew.captain = data.get('captain')
        crew.ship = data.get('ship')
        db.session.commit()
        return jsonify({'message': 'Crew updated successfully!'})
    
    if request.method == 'DELETE':
        db.session.delete(crew)
        db.session.commit()
        return jsonify({'message': 'Crew deleted successfully!'})


# Routes for Devil Fruits
@app.route('/api/devil_fruits', methods=['GET'])
def get_devil_fruits():
    devil_fruits = DevilFruit.query.all()
    return jsonify([{'name': fruit.devil_fruit_name} for fruit in devil_fruits])

@app.route('/api/devil_fruits', methods=['POST'])
def add_devil_fruit():
    data = request.json
    devil_fruit_name = data['name']
    if not DevilFruit.query.filter_by(devil_fruit_name=devil_fruit_name).first():
        new_devil_fruit = DevilFruit(devil_fruit_name=devil_fruit_name)
        db.session.add(new_devil_fruit)
        db.session.commit()
    return jsonify({'message': 'Devil fruit added successfully!'}), 201


# New Routes for Timeline and First-Time Character Appearances

# Timeline Route

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




# First-time Character Appearances
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
    # Get crew character counts
    crew_counts = db.session.query(
        Crew.crew_name,
        db.func.count(OPCharacter.character_id).label('character_count')
    ).join(OPCharacter, OPCharacter.crew_name == Crew.crew_name)\
     .group_by(Crew.crew_name).all()

    # Get popular devil fruit types
    fruit_counts = db.session.query(
        DevilFruit.type,  # Use 'type' here
        db.func.count(OPCharacter.devil_fruit_name).label('character_count')
    ).join(OPCharacter, OPCharacter.devil_fruit_name == DevilFruit.devil_fruit_name)\
     .group_by(DevilFruit.type)\
     .order_by(db.func.count(OPCharacter.devil_fruit_name).desc()).all()

    return render_template('one_piece_analysis.html', crew_counts=crew_counts, fruit_counts=fruit_counts)



@app.route('/api/popular_devil_fruits', methods=['GET'])
def popular_devil_fruits():
    # Query to count the number of characters per devil fruit type
    fruit_counts = db.session.query(
        DevilFruit.type,  # Use 'type' here, not 'devil_fruit_type'
        db.func.count(OPCharacter.devil_fruit_name).label('character_count')
    ).join(OPCharacter, OPCharacter.devil_fruit_name == DevilFruit.devil_fruit_name)\
     .group_by(DevilFruit.type)\
     .order_by(db.func.count(OPCharacter.devil_fruit_name).desc()).all()

    # Return the result as JSON
    return jsonify([{
        'devil_fruit_type': d.type,  # 'type' here as well
        'character_count': d.character_count
    } for d in fruit_counts])


if __name__ == '__main__':
    app.run(debug=True)
