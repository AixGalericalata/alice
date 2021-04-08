import os

from flask import Flask, request
import logging

import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}

goods = ['слона', 'кролика']


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


@app.route('/')
@app.route('/index')
def index():
    return "Привет, Яндекс!"


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = f'Привет! Купи {goods[0]}!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    user_req = req['request']['original_utterance'].lower()
    for word in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'
    ]:
        if word in user_req:
            good = goods.pop(0)
            res['response']['text'] = f'{good.capitalize()} можно найти на Яндекс.Маркете!'
            if goods:
                res['response']['text'] += f'\nА ещё купи {goods[0]}'
            else:
                res['response']['end_session'] = True
            return

    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {goods[0]}!"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
