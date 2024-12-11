from init.together import together_client

from data.models import Workflow, Analysis

from utilities.storage import get_data
from utilities.vector_storage import query_vectors

import requests

llama405bt = 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo'
llama90bt = 'meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo'
llama70bt = 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'
llama11bt = 'meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo'
llama8bt = 'meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo'


# Models
from pydantic import BaseModel
from typing import Optional


class Message(BaseModel):
    id: str
    phone_number_id: str
    sender: str
    phone_number: str
    message_type: str
    text: str
    image_id: Optional[str] = None
    image: Optional[str] = None
    image_analysis: Optional[str] = None


class Analysis(BaseModel):
    user: str
    educational_psychologist: Optional[str] = None
    communication_specialist: Optional[str] = None
    instructional_designer: Optional[str] = None
    cognitive_scientist: Optional[str] = None
    learning_analytics_specialist: Optional[str] = None
    behavioral_psychologist: Optional[str] = None
    memory_scientist: Optional[str] = None
    educational_data_privacy_officer: Optional[str] = None
    cognitive_load_analyst: Optional[str] = None
    synthesis: Optional[str] = None


class Workflow(BaseModel):
    message: Message
    previous_message: str = None
    agents: Optional[list] = None
    message_intent: Optional[str] = None
    analysis: Optional[Analysis] = None
    context_types: Optional[list] = None
    context: Optional[str] = None
    context_summary: Optional[str] = None
    web_search: Optional[list] = None
    knowledge_pool: Optional[str] = None
    potentiallized_response: Optional[str] = None
    raw_response: Optional[str] = None
    usage: int = 0


# Orchestrator
def orchestrate_response(workflow: Workflow) -> str:
    prompt = f'''
        You are an Orchestration Expert that analyzes user requests to determine the optimal agent sequence.

        AVAILABLE AGENTS:
        - context_retrieval: Retrieves conversation history
            * Use when the user's request depends on previous interactions or requires understanding the context of the conversation.
        - web_search: Gets current information
            * Use when the user needs up-to-date information, real-time data, or external references that are not part of the existing knowledge base.
        - knowledge_synthesizer: Analyzes information
            * Use when the information needs to be processed, summarized, or when insights and conclusions are required from the available data.
        - academic_potentializer: Enhances responses
            * Use when the response needs to be improved with expert analysis, recommendations, and insights.

        INPUT:
        {workflow.message.text}

        INTENT:
        {workflow.message_intent}

        IMAGE ANALYSIS:
        {workflow.message.image_analysis}

        RESPONSE FORMAT:
        You must respond in a pipe separated string with the agents in the order they should be executed.
        Example: context_retrieval|web_search|knowledge_synthesizer

        IMPORTANT:
        - Do not include agents that are not part of the available agents
        - Do not include text other than the pipe separated string of agents in your response
        - Do not include any additional information or comments
    '''

    raw_response = together_client.batch_response(prompt=prompt, image_base64=workflow.message.image, model=llama405bt, max_tokens=1000)
   
    if raw_response['status']:
        return raw_response['response']
    else:
        return False


# Image Analysis
def analyze_image(workflow: Workflow) -> str:
    prompt = f'''
        You are an Image Analyzer that interprets the image content and context.

        INPUT:
        {workflow.message.text}

        ANALYSIS:
        1. Identify key elements
        2. Determine context
        3. Extract relevant information
        4. Analyze for additional insights

        OUTPUT:
        # Image Analysis
        ## Key Elements
        - [Identified elements]
        - [Key context]

        ## Content Summary
        - [Relevant information]
        - [Additional insights]
    '''

    raw_response = together_client.batch_response(prompt=prompt, image_base64=workflow.message.image, model=llama90bt, max_tokens=1000)
   
    if raw_response['status']:
        return raw_response['response']
    else:
        return False


# Message Intent
def get_previous_message(message):
    url = f'users/{message.phone_number}/messages'
    messages = get_data(url)
    messages = [value for value in messages.values()] if messages else []
    messages = [f'{"Agent" if value["sender"] == "agent" else "User"}: {value["text"]}' for value in messages]
    return messages[-1] if len(messages) > 2 else 'No previous message'


def determine_message_intent(workflow: Workflow) -> str:
    prompt = f'''
        You are a Conversation Flow Analyzer that determines how the latest message relates to the previous exchange.

        USER MESSAGE:
        {workflow.message.text}

        IMAGE ANALYSIS:
        {workflow.message.image_analysis}

        PREVIOUS MESSAGE:
        {workflow.previous_message}

        Analyze the message type (follow-up, clarification, new topic, refinement, acknowledgment, decision), intent, and determine appropriate next action.
        
        RESPONSE FORMAT:
        The user message is a [type] and the intent is to [brief intent description]. You now must [specific action to take].
    '''

    raw_response = together_client.batch_response(prompt=prompt, image_base64=workflow.message.image, model=llama405bt, max_tokens=1000)
   
    if raw_response['status']:
        return raw_response['response']
    else:
        return False


# Academic Analysis
def get_analysis(workflow: Workflow):
    # Object Storage
    url = f'users/{workflow.message.phone_number}/analyses'
    analyses = get_data(url)
    analyses = [value for value in analyses.values()] if analyses else []
    return analyses[-1] if len(analyses) > 0 else {}


# Context Retrieval
def select_context_types(workflow: Workflow) -> str:
    prompt = f'''
        You are a Pedagogic Memory Expert that determines which memory types are essential for personalized educational responses.

        AVAILABLE MEMORY TYPES:
        - personal_profile: Student behavior, preferences, reactions
        - academic_context: Current studies, methods, progress  
        - knowledge_state: Subject comprehension, application
        - learning_events: Breakthroughs, significant moments

        INPUT:
        {workflow.message.text}

        IMAGE ANALYSIS:
        {workflow.message.image_analysis}

        RESPONSE FORMAT:
        You must respond in a pipe separated string with the memory types in the order they should be executed.
        Example: personal_profile|academic_context|knowledge_state|learning_events

        IMPORTANT:
        - Do not include memory types that are not part of the available memory types
        - Do not include text other than the pipe separated string of memory types in your response
        - Do not include any additional information or comments
    '''

    raw_response = together_client.batch_response(prompt=prompt, image_base64=workflow.message.image, model=llama405bt, max_tokens=1000)
   
    if raw_response['status']:
        return raw_response['response']
    else:
        return False


def retrieve_context(workflow: Workflow) -> dict:
    vectors = {}
    for context_type in workflow.context_types:
        context_data = query_vectors(data=workflow.message.text, user=workflow.message.phone_number, context_type=context_type)
        if context_data:
            vectors[context_type] = context_data
    
    return vectors


def summarize_context(workflow: Workflow) -> str:
    prompt = f'''
        You are a Context Analyzer that filters and summarizes relevant information.

        AVAILABLE CONTEXT:
        {'\n'.join(f'{key.upper()}: {value}' for key, value in workflow.context.items())}

        WEB SEARCH:
        {workflow.web_search}

        USER INPUT:
        {workflow.message.text}

        USER INTENT AND INSTRUCTION:
        {workflow.message_intent}

        IMAGE ANALYSIS:
        {workflow.message.image_analysis}

        ANALYZE:
        1. Filter for:
        - Direct relevance to input
        - Essential background
        - Specific references
        - Key history elements

        2. Summarize by including:
        - Actual relevant content
        - Specific quotes when needed
        - Complete context required for understanding
        - Full historical references

        OUTPUT:
        # Summary
        ## Key Content
        - [Actual relevant information, not just references]
        - [Specific quotes and details]

        ## Critical Context
        - [Complete background information]
        - [Full historical elements]

        ## Application
        - [Specific guidance with examples]
        - [How to use this information]
    '''

    raw_response = together_client.batch_response(prompt=prompt, image_base64=workflow.message.image, model=llama405bt, max_tokens=1000)
   
    if raw_response['status']:
        return raw_response['response']
    else:
        return False


# Web Search
def search_web(workflow: Workflow) -> str:
    # Extract search query and API key
    query = workflow.message.text
    EXA_API_KEY = 'e89cc7c3-9713-4164-a0a1-a837db5bc49b'

    # Configure Exa API request
    url = 'https://api.exa.ai/search'
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'x-api-key': EXA_API_KEY
    }
    payload = {
        'query': query,
        'type': 'keyword',
        'numResults': 10,
        'contents': {
        'highlights': {
            'highlightsPerUrl': 3,
            'numSentences': 3
        },
        'summary': True,
        'livecrawl': 'always'
        }
    }

    # Make API request
    request = requests.post(url, json=payload, headers=headers)
    response = request.json()
    return response

    
# Knowledge Synthesizer
def synthesize_knowledge(workflow: Workflow) -> str:
    prompt = f'''
        You are a Knowledge Architect that creates structured, scaffolded knowledge pools.

        USER INTENT AND INSTRUCTION:
        {workflow.message_intent}

        IMAGE ANALYSIS:
        {workflow.message.image_analysis}

        CONTEXT SUMMARY:
        {workflow.context_summary}

        SYNTHESIS PROCESS:
        1. Identify core concepts
        2. Create knowledge hierarchy
        3. Establish concept relationships
        4. Design learning progression
     
        OUTPUT FORMAT:
        # Knowledge Structure
        ## Core Concepts
        - [Fundamental elements]
        - [Key relationships]

        ## Learning Scaffold
        1. [Foundation level]
        2. [Intermediate concepts]
        3. [Advanced elements]

        ## Integration Points
        - [Concept connections]
        - [Application pathways]
    '''

    raw_response = together_client.batch_response(prompt=prompt, image_base64=workflow.message.image, model=llama405bt, max_tokens=1000)
   
    if raw_response['status']:
        return raw_response['response']
    else:
        return False


# Academic Potentializer
def potentiallize_response(workflow: Workflow) -> str:
    prompt = f'''
        You are an Academic Potentializer responsible for enhancing responses using expert-crafted academic analysis.

        **INPUTS:**
        KNOWLEDGE POOL:
        {workflow.knowledge_pool}

        USER INTENT:
        {workflow.message_intent}

        ACADEMIC ANALYSIS:
        {workflow.analysis.synthesis if workflow.analysis else 'No academic analysis available'}

        OUTPUT:
        Leverage the academic analysis, which includes strengths, weaknesses, recommendations, and key insights, to craft a precise set of instructions for an answer composer. These instructions should ensure that the final response aligns with the expert-derived analysis and effectively addresses the user's current needs or desires.
    '''

    raw_response = together_client.batch_response(prompt=prompt, image_base64=workflow.message.image, model=llama405bt, max_tokens=1000)
   
    if raw_response['status']:
        return raw_response['response']
    else:
        return False

# Response Composer
def compose_response(workflow: Workflow) -> str:
    prompt = f'''
        You are an expert tutor responding to a student's query. 
        Always match the language of the input and use formatting for clarity.

        INPUT:
        {workflow.message.text}

        USER INTENT:
        {workflow.message_intent}

        IMAGE ANALYSIS:
        {workflow.message.image_analysis}

        KNOWLEDGE:
        {workflow.knowledge_pool}

        LANGUAGE:
        Match input language exactly

        RESPONSE STYLE:
        Direct Questions:
        - Precise, clear answers
        - Include formulas/rules
        - Brief examples if needed

        Conceptual Questions:
        - Start with core principle
        - Build step by step
        - Connect to familiar ideas
        - Add thought-provoking examples

        Problem-Solving:
        - Guide don't solve
        - Break into steps
        - Highlight key insights
        - Encourage critical thinking

        TONE:
        - Clear & authoritative
        - Encouraging
        - Curiosity-sparking
        - Use analogies for complex topics

        FORMATTING:

        Basic
        *bold* for key terms
        _italic_ for emphasis
        ~strike~ for corrections

        Lists
        * bullet points
        1. numbered steps

        Quotes
        > key principles

        Code/Math
        `inline formulas`
        ```math blocks```

        Math Symbols
        - Fractions: ½ ⅓ ¼ 
        - Powers: x² x³
        - Root: √x
        - Multiply: 2·3
        - Divide: ÷
        - Compare: ≤ ≥ ≠
        - Greek: π α β
        - Other: ∞ ± ∑ ∫

        Matrices
        [a b c]
        [d e f]
        [g h i]
    '''

    raw_response = together_client.batch_response(prompt=prompt, image_base64=workflow.message.image, model=llama405bt, max_tokens=1000)
   
    if raw_response['status']:
        return raw_response['response']
    else:
        return False


# Workflow Initialization

def initialize_tutor_workflow(message) -> str:
    # Initialize Workflow
    workflow = Workflow(message=message)

    # Analyze Image
    if workflow.message.image:
        workflow.message.image_analysis = analyze_image(workflow=workflow)

    # Academic Analysis
    raw_analysis = get_analysis(workflow=workflow)
    if raw_analysis:
        workflow.analysis = Analysis(**raw_analysis)

    # Interpate User Message
    workflow.previous_message = get_previous_message(message=message)
    workflow.message_intent = determine_message_intent(workflow=workflow)

    # Orchestrate Agents
    raw_agents = orchestrate_response(workflow=workflow)
    workflow.agents = raw_agents.split('|')

    for agent in workflow.agents:
        if agent == 'context_retrieval':
            # Get Context Types
            raw_context_types = select_context_types(workflow=workflow)
            workflow.context_types = raw_context_types.split('|')

            workflow.context = retrieve_context(workflow=workflow)
            workflow.context_summary = summarize_context(workflow=workflow)

        # elif agent == 'web_search':
        #     workflow.web_search = search_web(workflow=workflow)
        
        elif agent == 'knowledge_synthesizer':
            workflow.knowledge_pool = synthesize_knowledge(workflow=workflow)
        
        elif agent == 'academic_potentializer':
            workflow.potentiallized_response = potentiallize_response(workflow=workflow)


    workflow.raw_response = compose_response(workflow=workflow)

    return workflow.raw_response
