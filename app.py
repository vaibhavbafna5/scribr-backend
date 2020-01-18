#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_cors import CORS
from trie import AutocompleteTrie, Node, MedicalTerm
import json
import pickle

# boot server & load data
print("Server is live :)")

filehandler = open('medical_dictionary.pkl', 'rb')
medical_dictionary = pickle.load(filehandler)

filehandler = open('autocomplete_trie.pkl', 'rb')
autocomplete_trie = pickle.load(filehandler)

app = Flask(__name__)
CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def say_hi():
    return 'alive'

@app.route('/suggestions', methods=['GET'])
def find_artists():
    # extract prefix from json
    prefix = request.args['prefix']
    
    # query the trie
    suggestions = autocomplete_trie.find_suggestions(prefix)
    print("SUGGESTIONS: ", suggestions)
    
    return jsonify(suggestions)


@app.route('/insert', methods=['POST'])
def insert_term():
    data = request.data.decode('UTF-8')
    data = json.loads(data)
    params = data['params']

    # update trie
    m_term = MedicalTerm(params['defn'], params['term'], params['related_terms'])
    autocomplete_trie.insert_word(m_term)

    return {'status': 'success'}


@app.route('/update', methods=['POST'])
def update_term():
    data = request.data.decode('UTF-8')
    data = json.loads(data)
    term = data['term']

    # update term's score in trie 
    m_term = autocomplete_trie.find_word(term)
    if m_term == False:
        return {'status': 'failure'}
    m_term.medical_term.score += 0.5

    return {'status': 'success'}

if __name__ == "__main__": 
    app.run(debug=True)
