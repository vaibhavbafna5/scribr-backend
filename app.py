#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_cors import CORS
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


import random

# object to store medical terms
class MedicalTerm:
    
    def __init__(self, defn, term, related_terms=[]):
        self.definition = defn
        self.term = term
        self.related_terms = related_terms
        self.score = random.randint(0, 10)

class Node:
    '''
    Each node stores a value, a MedicalTerm object (as defined above), 
    children, and a `completed` boolean to denote that a term is complete.
    '''
    def __init__(self, val='', m_term=None):
        self.val = val
        self.medical_term = m_term
        self.children = {}
        self.completions = []
        self.completed = False
        
class AutocompleteTrie:
    
    def __init__(self):
        '''
        Initializes an empty node as the root with an 
        empty dictionary as children.
        '''
        self.root = Node()
        
    
    def insert_word(self, m_term):
        '''
        Inserts medical term into the trie. Creates
        new children nodes correspondingly.
        '''
        val = m_term.term
        curr_node = self.root
        
        # NEW NEW NEW NEW
        related_terms_exist = False
        if m_term.related_terms:
            related_terms_exist = True
        # NEW NEW NEW NEW
        
        for i in range(0, len(val)):
            char = val[i]
            
            # create new nodes if children don't exist
            if char not in curr_node.children:
                stubbed_suggestion = val[0: i + 1]
                new_node = Node(stubbed_suggestion)
                
                # NEW NEW NEW NEW
                new_node.completions.append(val)
                if related_terms_exist:
                    new_node.completions.extend(m_term.related_terms)
                # NEW NEW NEW NEW 
                
                curr_node.children[char] = new_node
                curr_node = new_node
            else:
                curr_node = curr_node.children[char]
                
                # NEW NEW NEW NEW
                curr_node.completions.append(val)
                if related_terms_exist:
                    curr_node.completions.extend(m_term.related_terms)
                # NEW NEW NEW NEW
        
        curr_node.medical_term = m_term
        curr_node.completed = True
    
    
    def find_word(self, val):
        '''
        Attempts to find a word in the trie. Returns False
        if the word is not found, otherwise returns the term, 
        definition, and related words in a Tuple:
            (term, definition, related_words)
        '''
        curr_node = self.root
        
        for k in val:
            if k not in curr_node.children:
                return False
            else:
                curr_node = curr_node.children[k]
                
        if curr_node.completed:
            return (curr_node.val, curr_node.medical_term.definition, curr_node.medical_term.related_terms)
        else:
            return False

    
    def find_suggestions(self, val):
        '''
        Returns a list of words that match a given prefix as well as words
        that could possibly be related to a given prefix.
        '''
        curr_node = self.root
        
        for k in val:
            if k not in curr_node.children:
                return list()
            
            curr_node = curr_node.children[k]
            
        return curr_node.completions
    
    
    def find_suggestions_helper(self, node, suggestions):
        '''
        Recursive helper function for the above.
        '''
        if node.completed:
            suggestions.append(node.val)
            # add related terms to suggestions if they exist
            if node.medical_term.related_terms:
                suggestions.extend(node.medical_term.related_terms)
        
        for c in node.children:
            self.find_suggestions_helper(node.children[c], suggestions)


if __name__ == "__main__": 
    app.run(debug=True)
