from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)

client = MongoClient('mongodb+srv://test:sparta@cluster0.cyvuwe8.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta


@app.route('/')
def main():
    word_result = db.words.find({}, {'_id': False})
    words = []
    for word in word_result:
        definitions = word['definitions'][0]['shortdef']
        definitions = definitions if type(definitions) is str else definitions[0]
        words.append({
            'word' : word['word'],
            'definitions' : definitions,
        })
    msg = request.args.get('msg')
    return render_template("index.html", words=words, msg=msg)


@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = '7290fe7f-bdd0-4e01-99a3-8315e114605c'
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()
    if not definitions:
        return render_template('error.html',word=keyword)
    
    if type(definitions[0]) is str:
        return render_template("error.html", word=keyword, definitions=definitions)
    status = request.args.get('status_give', 'new')
    return render_template("detail.html", word=keyword, definitions=definitions, status=status)

@app.route('/error')
def error():
    return render_template("error.html")

@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')
    doc = {
        'word' : word,
        'definitions' : definitions,
        'date': datetime.now().strftime('%Y/%m/%d'),
    }
    db.words.insert_one(doc)

    return jsonify({'result': 'success', 'msg': f'the word {word}, was saved!'})


@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word': word})
    db.examples.delete_many({'word':word})
    return jsonify({'result': 'success', 'msg': f'the word {word} was deleted'})

@app.route('/api/get_exs', methods=['GET'])
def get_exs():
    word = request.args.get('word')
    example_data = db.examples.find({'word':word})
    examples = []
    for example in example_data:
        examples.append({
            'example': example.get('example'),
            'id': str(example.get('_id')),
        })
    return jsonify({'result': 'success', 'examples':examples})

@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    word = request.form.get('word')
    example = request.form.get('example')
    doc = {
        'word':word,
        'example':example,
    }
    db.examples.insert_one(doc)
    return jsonify({'result': 'success', 'msg':f'Your Example, {example}, for the word, {word}, Was Saved!'})


@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    id = request.form.get('id')
    word = request.form.get('word')
    db.examples.delete_one({'_id': ObjectId(id)})
    return jsonify({'result': 'success', 'msg':f'Your example for, {word}, was deleted!',})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)