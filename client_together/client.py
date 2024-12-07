import json
import requests

class TogetherAiClient:
    def __init__(self, key):
        self.key = key

    def batch_response(self, prompt, model, max_tokens, image_base64=None):
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
            'type': 'chat',
            
        }

        if model == 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo':
            payload['messages'] = [
                {
                    'content': prompt,
                    'role': 'user'
                }
            ]
        else:
            payload['messages'] = [
                {
                    'content': [
                        {
                            'type': 'text',
                            'text': prompt
                        }
                    ],
                    'role': 'user'
                }
            ]

        if image_base64 and model == 'meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo':
            payload['messages'][0]['content'].append({
                'type': 'image_url',
                'image_url': {
                    'url': f"data:image/jpeg;base64,{image_base64}"
                }
            })
        try:
            response = requests.post(
                'https://api.together.ai/inference', 
                headers=headers, 
                data=json.dumps(payload)
            )
            if response.status_code == 200:
                response = response.json()
                if model == 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo':
                    return {
                        'status' : True,
                        'response': response['output']['choices'][0]['text'],
                        'usage': response['usage'],
                    }
                else:
                    return {
                        'status' : True,
                        'response': response['choices'][0]['message']['content'],
                        'usage': response['usage'],
                    }
            else:
                raise Exception
        except Exception as e:
            return {'status': False, 'message': f'Oops, there was an error batching a response: {e}'}
