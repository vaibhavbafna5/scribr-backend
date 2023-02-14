## Building Medical Autocomplete

**Sourcing Data**

Before I could even orchestrate any kind of API or think of architecture, I needed to source the data that would form the basis of this autocomplete system. After mulling over a few options (scraping google search results, some open source data sets, medical textbooks), I stumbled upon [this](https://www.passporttolanguages.com/Interpreter_Resources/Gloss_Med_Terms.pdf) glossary of medical terms.

This source had a few advantages over other sources I evaluated:

- easy to scrape data
- the presence of related terms
- comprehensive definitions
- focus on primary care conditions

For instance, here's an example medical term I found in the glossary.

```
💡 Acute pulmonary edema -- Set of dramatic, life-threatening symptoms, including extreme shortness of breath, rapid breathing, anxiety, cough, bluish lips and nails, and sweating. Usually caused by congestive heart failure. See Congestive heart failure.
```

The term & definitions are delimited by a '- - ', which is consistent across the definitions in the glossary.

Additionally, congestive heart failure is also outlined as a related condition which signals the ability to suggest conditions that don't necessarily start with 'a'.

**Parsing the Data, Building Data Structures, & Optimizing**

In order to parse the data and test different data structures, I used a Jupyter Notebook, given the quick interactive feedback loop.

The following [notebook](https://github.com/vaibhavbafna5/scribr-data-exploration/blob/master/Scribr-Notebook.ipynb) is organized as follows:

- Data extraction
- Building & testing a trie
- Analysis & optimizations
- Final notes

## Putting It All Together

**Frontend**

I built the frontend using React. One of the key advantages it offered was its state management, which allowed me to "listen" on the textarea for changes and make an API request on every single user keystroke. That was the key insight needed for the blazing fast autocomplete on the user side.

Here are some of the features I added.

- Keyboard shortcut ('ctrl-d') will pick the top suggestion and automatically fill that in the text area
- Mousing over the suggestions and then clicking on one will automatically fill that in the text area
- Selecting a suggestion (whether by keyboard shortcut or clicking) will increase its score in the backend

You can view the frontend code I wrote [here](https://github.com/vaibhavbafna5/scribr-frontend).

**Backend**

The backend is a pretty standard Flask app hosted using Heroku. There are two main endpoints:

For suggestions for a term, I send a `GET` request with a `prefix` parameter that queries the trie and returns suggestions.

```python
@app.route('/suggestions', methods=['GET'])
```

If a user decides to select a term & autocomplete it, I send a `POST` request with the term that attempts to find the term in the trie and increments its score by 0.5. If the term isn't found in the trie, a failure message is returned on the backend.

```python
@app.route('/update/<term>', methods=['POST'])
```
