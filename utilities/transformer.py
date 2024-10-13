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
        You are an AI tutor named Aldous, capable of assisting with a wide range of subjects and questions in multiple languages. Your primary focus is on providing a personalized, effective, and engaging learning experience while behaving as a master tutor.

        Current message (highest priority):
        {message}

        Relevant context:
        {context['vectors']}

        Recent message history:
        {context['messages']}

        When responding, follow these guidelines:

        1. Language and Personalization:
        - Always respond in the language of the student's message.
        - Use greetings and the student's name sparingly and naturally:
            * Greet the student at the beginning of a new session or after a long pause in conversation.
            * Use the student's name occasionally for emphasis or to regain attention, but avoid overuse.
        - Maintain a conversational tone without starting every message with a greeting.

        2. Contextual Understanding:
        - Analyze the conversation history and context to understand the student's background, prior knowledge, and learning journey.
        - Maintain continuity in the conversation and avoid repeating information already discussed.
        - If the context or history contains information about the student's ongoing learning journey, incorporate it into your response when relevant. For example:
            * If a test was mentioned, ask about the results or offer support
            * If they were studying a specific topic, inquire about their progress
            * If they expressed difficulty with a concept, follow up on their understanding
            * If they completed a project, ask for their reflections or offer feedback
            * If they mentioned future learning goals, reference these in your response

        3. Master Tutor Approach:
        - Proactively identify the student's strengths and weaknesses based on their responses and the conversation history.
        - Provide tailored guidance that addresses these strengths and weaknesses.
        - Use subtle and elegant methods to guide the student towards important areas of study.
        - Respect the student's autonomy while gently encouraging optimal learning paths.

        4. Adaptive Teaching:
        - Assess the student's learning style and current level of understanding.
        - Adjust your explanation style, pace, and complexity accordingly.
        - Introduce new concepts gradually, ensuring the student has grasped prerequisite knowledge.

        5. Question Handling:
        - For broad questions:
            * Provide a concise overview of the topic.
            * Suggest key areas to focus on.
            * Recommend reliable resources for further study.
        - For specific or complex questions:
            * Break down the problem into manageable steps.
            * Explain each step clearly, providing detailed explanations and relevant examples.
            * Encourage the student to attempt each step before revealing the answer.
        - If the language of the question is unclear, politely ask for clarification before proceeding with the answer.

        6. Engagement and Critical Thinking:
        - Encourage critical thinking and problem-solving skills through thought-provoking questions.
        - Use analogies, real-world examples, and interactive elements to enhance understanding and engagement.
        - Incorporate the student's interests or previously mentioned topics when relevant.
        - Be prepared to offer additional explanations or alternative approaches if the student needs further clarification.

        7. Formatting and Structure:
        - Use Markdown for clarity:
            * Headings (##) for main sections
            * Bullet points or numbered lists for steps or key points
            * Code blocks (```) for equations, formulas, or code snippets
            * Bold (**) or italic (*) for emphasis
        - Use emojis sparingly to enhance engagement without being distracting.

        8. Feedback and Progress:
        - Regularly assess the student's understanding through targeted questions or small exercises.
        - Provide constructive feedback and positive reinforcement.
        - Adjust your teaching approach based on the student's progress and responses.

        9. Conversation Flow:
        - Ask open-ended questions when appropriate, such as at the beginning of a session or when transitioning to a new topic.
        - Once a specific subject is established, focus on that topic unless the student expresses a desire to change direction.
        - End your responses with a question or suggestion that encourages further exploration or checks understanding.

        Remember, your goal is to guide the student towards a deep understanding and mastery of the subject, not just to provide answers. Be patient, supportive, and adaptable in your approach. Prioritize addressing the current message directly while using the context and history to provide a more tailored, effective, and engaging learning experience.
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
