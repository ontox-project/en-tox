from flask import Flask, request, jsonify, render_template 
import spacy
from typing import List
import main
from decorators import *

app = Flask(__name__)

custom_valid_values = {
    'causes': ['COMPOUND', 'PHENOTYPE'],  # Custom valid values for 'cause'
    'effects': ['PHENOTYPE']  # Custom valid values for 'effect'
}

@app.route('/relationships', methods=['POST'])
@validate_relationship_input(valid_values=custom_valid_values)
def get_relationships(text, cause, effect):
    #text = request.form['input_text'] if we don't use an interface
    relationships = main.entox_parse(text, cause=cause, effect=effect)
    return jsonify({"relationships": relationships})

@app.route('/')  # New route to serve your HTML file
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
