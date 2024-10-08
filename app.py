from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3

'''
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type
'''

app = Flask(__name__)
CORS(app)

# Your database connection logic
def get_db_connection():
    conn = sqlite3.connect('xcom_abilities.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route to handle search query
@app.route('/search_abilities')
def search_abilities():
    query = request.args.get('query', '')
    if query:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Perform search in the abilities table
        cur.execute("SELECT name FROM abilities WHERE name LIKE ?", ('%' + query + '%',))
        abilities = cur.fetchall()
        
        # Return the result as a list of ability names
        results = [ability['name'] for ability in abilities]
        return jsonify(results)
    return jsonify([])

@app.route('/get_full_ability', methods=['GET'])
def get_full_ability():
    ability_name = request.args.get('ability_name')
    if not ability_name:
        return jsonify({'error': 'Ability name is required'}), 400

    conn = get_db_connection()
    ability = conn.execute('SELECT * FROM abilities WHERE name = ?', (ability_name,)).fetchone()
    conn.close()

    if ability is None:
        return jsonify({'error': 'Ability not found'}), 404

    # Return ability data
    return jsonify({
        'name': ability['name'],
        'class': ability['class'],
        'rank': ability['rank'],
        'game1': ability['game1'],
        'game2': ability['game2']
    })
    
@app.route('/random_ability')
def random_ability():
    conn = get_db_connection()
    # Select all fields for a random ability
    ability = conn.execute('SELECT name, class, rank, game1, game2 FROM abilities ORDER BY RANDOM() LIMIT 1').fetchone()
    conn.close()
    if ability:
        # Return all the relevant data: name, class, rank, and games
        return jsonify({
            'ability': ability['name'],
            'class': ability['class'],
            'rank': ability['rank'],
            'game1': ability['game1'],
            'game2': ability['game2']
        })
    return jsonify({'error': 'No abilities found'}), 404

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        abilities = search_abilities(query)
        return jsonify(abilities)
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
