import requests

def slack_message(secret, channel, text):
    headers = {'Authorization': f'Bearer {secret}'}
    data = {'channel': channel, 'text': text}
    headers
    requests.post('https://slack.com/api/chat.postMessage', json = data, headers=headers)