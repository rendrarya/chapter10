import requests

api_key = '7290fe7f-bdd0-4e01-99a3-8315e114605c'
word = 'fuck'
root_url = 'https://www.dictionaryapi.com/api/v3/references/collegiate/json'
final_url = f'{root_url}/{word}?key={api_key}'
r = requests.get(final_url)
result = r.json()
print(result)