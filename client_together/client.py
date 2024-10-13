import json
import requests

class TogetherAiClient:
    def __init__(self, key):
        self.key = key

    def batch_response(self, prompt, image_base64, model, max_tokens):
        try:
            headers = {
                'Authorization': f'Bearer {self.key}',
                'accept': 'application/json',
                'content-type': 'application/json',
            }
            payload = {
                'model': model,
                'max_tokens': max_tokens,
                'request_type': 'language-model-inference',
                'temperature': 0.5,
                'top_p': 0.5,
                'top_k': 15,
                'repetition_penalty': 1,
                'stop': [
                    '<|eot_id|>'
                ],
                'negative_prompt': '',
                'sessionKey': 'd9c5e540-749a-4c81-b701-6a5397b198d0',
                'type': 'chat',
                'messages': [
                    {
                        'content': [
                            {
                                'type': 'text',
                                'text': prompt
                            }
                        ],
                        'role': 'user'
                    }
                ],
            }

            if image_base64:
                payload['messages'][0]['content'].append({
                    'type': 'image_url',
                    'image_url': {
                        'url': f"data:image/jpeg;base64,{image_base64}"
                    }
                })

            response = requests.post(
                'https://api.together.xyz/v1/chat/completions', 
                headers=headers, 
                data=json.dumps(payload)
            )
            if response.status_code == 200:
                response = response.json()
                # print('Tokens used:')
                # print(response['usage'])
                return response['choices'][0]['message']['content']
            else:
                print(response.text)
                raise Exception
        except Exception as e:
            return {'status': False, 'message': f'Oops, there was an error batching a response: {e}'}


    def stream_response(self, prompt, model, max_tokens):
        try:
            headers = {
                'Authorization': f'Bearer {self.key}',
                'accept': 'application/json',
                'content-type': 'application/json',
            }
            payload = {
                'model': model,
                'max_tokens': max_tokens,
                'request_type': 'language-model-inference',
                'temperature': 0.5,
                'top_p': 0.5,
                'top_k': 15,
                'repetition_penalty': 1,
                'stop': [
                    '<|eot_id|>'
                ],
                'negative_prompt': '',
                'sessionKey': 'd9c5e540-749a-4c81-b701-6a5397b198d0',
                'type': 'chat',
                'messages': [
                    {
                        'content': [
                            {
                                'type': 'text',
                                'text': prompt
                            }
                        ],
                        'role': 'user'
                    }
                ],
                'stream': True,
            }
            with requests.post('https://api.together.xyz/v1/chat/completions', headers=headers, json=payload, stream=True) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        line = line.decode('utf-8')
                        if line and '[DONE]' not in line:
                            try:
                                json_response = json.loads(line.split('data: ')[1])
                                if len(json_response['choices']) != 0:
                                    yield json_response['choices'][0]['text']
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield json.dumps({'status': False, 'message': f'Oops, there was an error: {str(e)}'})