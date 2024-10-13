from init.together import together_client

from data.models import Parameters, Template

import json
import asyncio

llama405bt = 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo'
llama90bt = 'meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo'
llama70bt = 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'
llama8bt = 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo'


def generate_descriptors(template: Template) -> str:
    prompt = f'''
        Given a template for an academic document, generate 10 descriptive phrases in Spanish that accurately represent the template's unique purpose and content. These phrases should be suitable for semantic retrieval in a vector database. Provide the phrases as a single pipe (|) separated string.

        Template structure:
        {{
            "id": "string",
            "template_type": "string",
            "title": "string",
            "description": "string",
            "metadata": "string"
        }}

        Consider the following guidelines:
        1. Each phrase should be concise but informative, typically 25-50 words long.
        2. Focus on the key actions, purposes, or outcomes specific to this template.
        3. Use action verbs at the beginning of each phrase.
        4. Incorporate relevant educational terminology and concepts unique to this template type.
        5. Ensure the phrases are highly specific to this template's purpose and type.
        6. Avoid generic descriptions or terms that could apply to other template types.
        7. Include variations in phrasing to capture different aspects of the template's use.
        8. Emphasize the primary function and distinguishing features of this template.
        9. Avoid mentioning secondary elements that might be central to other template types.
        10. All phrases must be in Spanish.

        Here's the template to describe:

        Template Type: {template.template_type}

        Title: {template.title}

        Description: {template.description}

        Metadata: {template.metadata}

        Please provide 10 retrieval phrases in Spanish for this template as a single pipe (|) separated string, like this:

        Phrase 1 | Phrase 2 | Phrase 3 | Phrase 4 | Phrase 5 | Phrase 6 | Phrase 7 | Phrase 8 | Phrase 9 | Phrase 10

        Ensure each phrase is unique and directly related to the core purpose of this specific template. The output should contain only the Spanish phrases separated by pipes, with no additional text.
    '''

    raw_response = together_client.batch_response(prompt=prompt, model=llama90bt, max_tokens=2500)
    return raw_response


async def stream_rewrite(websocket, parameters: Parameters) -> str:
    prompt = (
        'As an expert in content adaptation, rewrite the following text in Spanish according to the provided instructions:'
        f'\n\nOriginal Content:\n\n{parameters.seed}\n'
        f'\n\nRewriting Instructions:\n{parameters.instructions}'
        '\n\nTask: Refine and rewrite the content while adhering to these requirements:'
        '\n1. Language: Spanish'
        '\n2. Format: Valid Markdown syntax'
        '\n3. Structure: Maintain the original document structure'
        '\n4. Content: Ensure the rewrite aligns closely with the original content\'s key points and objectives'
        '\n5. Adaptations: Implement changes as specified in the rewriting instructions'
        '\n6. Output: Provide only the rewritten content, without explanatory text or additional formatting'
        '\n\nBefore submitting, review your response to confirm strict adherence to these requirements.'
        '\n\nBegin your rewritten content here:'
    )
    response_stream = together_client.stream_response(prompt=prompt, model=llama90bt, max_tokens=2500)
    
    for chunk in response_stream:
        await websocket.send_text(chunk)
        await asyncio.sleep(0.01)


def batch_optimize(seed: str, instructions: str) -> str:
    prompt = (
        f'Analyze this seed document:\n{seed}'
        f'\nand these original instructions:\n{instructions}'
        '\nThen, provide concise instructions in Spanish (max 200 words) to create a new document that:'
        '\n1. Directly relates to and builds upon the seed document'
        '\n2. Aligns with the seed\'s content and learning objectives'
        '\n3. Uses an appropriate format (e.g., worksheet, quiz, presentation, analysis)'
        '\n4. Encourages innovative presentation or assessment of the seed\'s information'
        '\nYour response should be a single paragraph in plain text, without formatting. Focus on clear, specific guidance tailored to the seed document.'
    )
    raw_response = together_client.batch_response(prompt=prompt, model=llama90bt, max_tokens=2500)
    return raw_response


async def stream_generate(websocket, parameters: Parameters, template: dict) -> str:
    prompt = (
        f'Generate a {template["title"]} in Spanish that {template["description"]}. Adhere strictly to this Markdown template:'
        f'\n<HEADING>'
        f'\n# Título: <CREATIVE_GENERATED_TITLE>'
        f'\n'
        f'\n- Tipo: {template["title"]}'
        f'\n- Grado: {parameters.grade}'
        f'\n- Materia: {parameters.subject}'
        f'\n- Tema: {parameters.topic}'
        f'\n</HEADING>'
        f'\n'
        f'\n{template["metadata"]}'
        '\nKey instructions:'
        f'\n1. Use these parameters: Grade={parameters.grade}, Level={parameters.class_level}, Subject={parameters.subject}, Topic={parameters.topic}, Complexity={parameters.complexity}, Length={parameters.length} minutes'
        f'\n2. Additional instructions: {parameters.instructions}'
        '\n3. Start directly with content. No introductory text.'
        '\n4. Fill all sections with appropriate Spanish content.'
        '\n5. Do not alter template structure or add sections.'
        '\n6. Ensure output is valid Markdown.'
        '\nReview your response to confirm strict adherence to the template and instructions.'
    )
    response_stream = together_client.stream_response(prompt=prompt, model=llama90bt, max_tokens=2500)
    
    for chunk in response_stream:
        await websocket.send_text(chunk)
        await asyncio.sleep(0.01)


def batch_respond(message: str, context: dict, image_base64: str) -> str:
    prompt = f'''
    You are an AI tutor capable of assisting with a wide range of subjects and questions in multiple languages. Your role is to provide guidance, explanations, and answers tailored to the student's needs. When responding, follow these guidelines:

    1. Always respond in the same language as the question asked.

    2. Assess the question's complexity and specificity.

    3. For general or broad questions:
    - Provide an overview of the topic
    - Suggest key areas to focus on
    - Recommend reliable resources for further study
    - Outline a general approach to understanding the subject

    4. For specific or complex questions:
    - Break down the problem into manageable steps
    - Explain each step clearly
    - Provide intermediate answers or results
    - Encourage the student to attempt each step before revealing the answer

    5. Always use Markdown formatting for clarity and structure:
    - Use headings (##) for main sections
    - Use bullet points or numbered lists for steps or key points
    - Use code blocks (```) for equations, formulas, or code snippets
    - Use bold (**) or italic (*) for emphasis

    6. Adapt your language and explanation style to the student's apparent level of understanding.

    7. Encourage critical thinking and problem-solving skills.

    8. Be prepared to offer additional explanations or alternative approaches if the student needs further clarification.

    9. End your response with a question or suggestion to check the student's understanding or encourage further exploration of the topic.

    10. If the language of the question is unclear, politely ask for clarification before proceeding with the answer.

    11. Use emojis or visual aids when appropriate to enhance engagement and understanding and to make the learning experience more enjoyable.

    Remember, your goal is to guide the student towards understanding and mastery of the subject, not just to provide answers. Always communicate in the language used by the student to ensure effective learning and clear communication.
    
    Here is the message you need to respond to: {message}

    Here is the relevant context of the conversation: {context['vectors']}

    Here is the most recent messages: {context['messages']}
    
    '''
    raw_response = together_client.batch_response(prompt=prompt, image_base64=image_base64, model=llama90bt, max_tokens=2500)
    return raw_response

def colegios_json_bot(parameters: Parameters, content: str) -> str:
    outputs = {
        'multiple_choice': {
            'title': '<CREATIVE_TEST_TITLE>',
            'difficulty': '<DIFFICULTY_LEVEL>',
            'subject': '<SUBJECT_CATEGORY>',
            'instructions': '<CLEAR_AND_CONCISE_TEST_INSTRUCTIONS>',
            'content': [
                {
                    'question': '<CLEAR_AND_CONCISE_QUESTION_TEXT>',
                    'choices': ['<PLAUSIBLE_ANSWER_CHOICE>', '<PLAUSIBLE_ANSWER_CHOICE>', '<PLAUSIBLE_ANSWER_CHOICE>', '<PLAUSIBLE_ANSWER_CHOICE>'],
                    'answer': {
                        'index': '<CORRECT_ANSWER_INDEX>',
                        'reasoning': '<DETAILED_JUSTIFICATION_FOR_ANSWER>',
                        'work': '<STEP_BY_STEP_SOLUTION_WITH_FORMATTING>'
                    },
                    'points': '<QUESTION_POINTS>',
                    'tags': ['<RELEVANT_QUESTION_TAG>', '<RELEVANT_QUESTION_TAG>']
                }
            ]
        },
        'true_false': {
            'title': '<CREATIVE_TEST_TITLE>',
            'difficulty': '<DIFFICULTY_LEVEL>',
            'subject': '<SUBJECT_CATEGORY>',
            'content': [
                {
                    'question': '<CLEAR_AND_CONCISE_QUESTION_TEXT>',
                    'answer': {
                        'value': '<CORRECT_ANSWER_VALUE>',
                        'reasoning': '<DETAILED_JUSTIFICATION_FOR_ANSWER>',
                    },
                    'points': '<QUESTION_POINTS>',
                    'tags': ['<RELEVANT_QUESTION_TAG>', '<RELEVANT_QUESTION_TAG>']
                }
            ]
        },
        'short_answer': {
            'title': '<CREATIVE_TEST_TITLE>',
            'difficulty': '<DIFFICULTY_LEVEL>',
            'subject': '<SUBJECT_CATEGORY>',
            'content': [
                {
                    'question': '<CLEAR_AND_CONCISE_QUESTION_TEXT>',
                    'answer': {
                        'value': '<EXPECTED_ANSWER_TEXT_1-2_SENTENCES>',
                        'keywords': ['<KEYWORD_1>', '<KEYWORD_2>', '<KEYWORD_3>'],
                        'reasoning': '<DETAILED_JUSTIFICATION_FOR_ANSWER>'
                    },
                    'alternate_answers': [
                        {
                            'value': '<ACCEPTABLE_ALTERNATE_ANSWER_1-2_SENTENCES>',
                            'keywords': ['<KEYWORD_1>', '<KEYWORD_2>', '<KEYWORD_3>'],
                            'reasoning': '<JUSTIFICATION_FOR_ALTERNATE_ANSWER>'
                        }
                    ],
                    'points': '<QUESTION_POINTS>',
                    'tags': ['<RELEVANT_QUESTION_TAG>', '<RELEVANT_QUESTION_TAG>']
                }
            ]
        }
    }

    prompt = (
        f'You are an asistant that only speaks valid RFC 8259 JSON. Do not write anything else.'
        + f'\nYou are tasked with creating question a {parameters.template} test in Spanish.'
        + f'\nThe test should be based on the following content: {content}'
        + f'\nQuestions should be progressively more difficult and should build on the previous question.'
        + f'\nThe test must meet the following criteria:'
        + f'\nGrade: {parameters.grade}'
        + f'\nClass Level: {parameters.class_level}'
        + f'\nSubject: {parameters.subject}'
        + f'\nTopic: {parameters.topic}'
        + f'\nComplexity: {parameters.complexity}'
        + f'\nLength: {parameters.length} questions'
        + f'\nInstructions: {parameters.instructions}'
        + f'\n<OUTPUT>{outputs[parameters.template]}</OUTPUT>'
    )
    raw_response = together.send_message(prompt=prompt, model=llama90bt, max_tokens=2500)
    return raw_response
