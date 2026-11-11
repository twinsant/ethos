import requests


def slack_message(secret, channel, text):
    if not secret:
        return

    headers = {'Authorization': f'Bearer {secret}'}
    data = {'channel': channel, 'text': text}
    response = requests.post('https://slack.com/api/chat.postMessage', json=data, headers=headers, timeout=10)
    response.raise_for_status()
    result = response.json()
    if not result.get('ok'):
        raise RuntimeError(f"Slack message failed: {result.get('error', 'unknown error')}")
