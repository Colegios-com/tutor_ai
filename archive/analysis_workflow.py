from init.together import together_client

from data.models import Analysis

from utilities.storage import get_data, save_data
from utilities.vector_storage import get_vectors

llama405bt = 'meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo'
llama90bt = 'meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo'


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


# Message Storage
def get_message_history(user):
    # Object Storage
    url = f'users/{user}/messages'
    messages = get_data(url)
    messages = [value for value in messages.values()] if messages else []
    messages = [f'{"Agent" if value["sender"] == "agent" else "User"}: {value["text"]}' for value in messages]
    return messages[:10]


# Memory Storage
def retrieve_context(user: str) -> dict:
    memories = get_vectors(user)
    return memories['documents'][:10]


# Analysis Storage
def get_analysis(user: str):
    # Object Storage
    url = f'users/{user}/analyses'
    analysis = get_data(url)


def save_analysis(analysis: Analysis):
    # Object Storage
    url = f'users/{analysis.user}/analyses'
    save_data(url, analysis.dict())


# Analysis Orchestrator
def select_analysis_experts(message_history, memories) -> list:
    prompt = f'''
        You are an Orchestrator tasked with selecting the most valuable set of analyst agents to employ for analyzing educational interactions. Your goal is to optimize computational resources by selecting only those experts that add significant value based on the provided message history and memories.

        AVAILABLE ANALYST AGENTS:
        - educational_psychologist: Analyzes cognitive load and emotional engagement.
        - communication_specialist: Evaluates clarity, effectiveness, and appropriateness of language.
        - instructional_designer: Assesses alignment of interactions with educational objectives and engagement strategies.
        - cognitive_scientist: Examines mental processes involved in learning and problem-solving.
        - learning_analytics_specialist: Identifies trends and patterns in learning behaviors and performance.
        - behavioral_psychologist: Understands behavioral patterns influencing learning outcomes.
        - memory_scientist: Evaluates effectiveness of memory formation and retention strategies.
        - cognitive_load_analyst: Assesses and optimizes cognitive demands placed on students.

        MESSAGE HISTORY:
        {message_history}

        MEMORIES:
        {memories}

        RESPONSE FORMAT:
        You must respond in a pipe separated string with the agents in the order they should be executed.
        Example: educational_psychologist|cognitive_scientist|learning_analytics_specialist|cognitive_load_analyst

        IMPORTANT:
        - Do not include agents that are not part of the available agent types
        - Do not include text other than the pipe separated string of agents in your response
        - Do not include any additional information or comments
    '''

    raw_response = together_client.batch_response(
        prompt=prompt,
        model=llama405bt,
        max_tokens=500
    )

    return raw_response['response']


# Textual Interactions Analysis
def analyze_educational_psychologist(message_history) -> str:
    prompt = f'''
        You are an Educational Psychologist analyzing the cognitive and emotional dynamics in the following student-AI tutor interactions.
        
        ANALYSIS OBJECTIVE: Understand the cognitive load and emotional engagement of the student.
        
        ANALYSIS COMPONENTS:
        - Strengths: Identify aspects that support cognitive processing and emotional engagement.
        - Weaknesses: Highlight elements that may cause cognitive overload or emotional disengagement.
        - Actionable Suggestions: Provide recommendations to balance cognitive load and enhance emotional engagement.
        - Potential Issues: Note any concerns related to student well-being or learning effectiveness.
        
        MESSAGE HISTORY:
        {message_history}
        
        RESPONSE FORMAT:
        ## Strengths
        - ...
        
        ## Weaknesses
        - ...
        
        ## Actionable Suggestions
        - ...
        
        ## Potential Issues
        - ...
    '''
    
    raw_response = together_client.batch_response(
        prompt=prompt,
        model=llama405bt,
        max_tokens=1500
    )
    return raw_response['response']


def analyze_communication_specialist(message_history) -> str:
    prompt = f'''
        You are a Communication Specialist evaluating the clarity, effectiveness, and appropriateness of language used in the following student-AI tutor interactions.
        
        ANALYSIS OBJECTIVE: Assess the effectiveness of communication styles, clarity, and tone.
        
        ANALYSIS COMPONENTS:
        - Strengths: Highlight clear and effective communication instances.
        - Weaknesses: Identify any ambiguities or areas where communication can be improved.
        - Actionable Suggestions: Recommend strategies to enhance communication clarity and effectiveness.
        - Potential Issues: Note any risks of miscommunication or cultural misunderstandings.
        
        MESSAGE HISTORY:
        {message_history}
        
        RESPONSE FORMAT:
        ## Strengths
        - ...
        
        ## Weaknesses
        - ...
        
        ## Actionable Suggestions
        - ...
        
        ## Potential Issues
        - ...
    '''
    
    raw_response = together_client.batch_response(
        prompt=prompt,
        model=llama405bt,
        max_tokens=1500
    )
    return raw_response['response']


def analyze_instructional_designer(message_history) -> str:
    prompt = f'''
        You are an Instructional Designer evaluating the structure and effectiveness of the learning material and interactions in the following student-AI tutor exchanges.
        
        ANALYSIS OBJECTIVE: Assess the alignment of interactions with educational objectives and the effectiveness of engagement strategies.
        
        ANALYSIS COMPONENTS:
        - Strengths: Identify well-structured elements that align with educational goals.
        - Weaknesses: Highlight areas where instructional design can be improved for better alignment and engagement.
        - Actionable Suggestions: Provide recommendations to optimize the instructional design for enhanced learning outcomes.
        - Potential Issues: Note any challenges related to adaptability or resource constraints in instructional design.
        
        MESSAGE HISTORY:
        {message_history}
        
        RESPONSE FORMAT:
        ## Strengths
        - ...
        
        ## Weaknesses
        - ...
        
        ## Actionable Suggestions
        - ...
        
        ## Potential Issues
        - ...
    '''
    
    raw_response = together_client.batch_response(
        prompt=prompt,
        model=llama405bt,
        max_tokens=1500
    )
    return raw_response['response']


def analyze_cognitive_scientist(message_history) -> str:
    prompt = f'''
        You are a Cognitive Scientist analyzing the mental processes involved in the following student-AI tutor interactions.
        
        ANALYSIS OBJECTIVE: Understand how students process information and apply problem-solving skills during interactions.
        
        ANALYSIS COMPONENTS:
        - Strengths: Identify instances where cognitive processes are effectively supported.
        - Weaknesses: Highlight areas where cognitive overload or misunderstandings may occur.
        - Actionable Suggestions: Recommend strategies to enhance cognitive processing and problem-solving.
        - Potential Issues: Note any risks related to cognitive strain or misinformation.
        
        MESSAGE HISTORY:
        {message_history}
        
        RESPONSE FORMAT:
        ## Strengths
        - ...
        
        ## Weaknesses
        - ...
        
        ## Actionable Suggestions
        - ...
        
        ## Potential Issues
        - ...
    '''
    
    raw_response = together_client.batch_response(
        prompt=prompt,
        model=llama405bt,
        max_tokens=1500
    )
    return raw_response['response']


# Memory Experts
def analyze_learning_analytics_specialist(memories) -> str:
    prompt = f'''
        You are a Learning Analytics Specialist analyzing the following memory logs derived from student-AI tutor interactions.
        
        ANALYSIS OBJECTIVE: Identify trends and patterns in student learning behaviors and performance.
        
        ANALYSIS COMPONENTS:
        - Strengths: Highlight positive learning behaviors and progress indicators.
        - Weaknesses: Identify areas where student performance may be lagging.
        - Actionable Suggestions: Provide data-driven recommendations to improve learning outcomes.
        - Potential Issues: Note any anomalies or data integrity concerns that may affect analysis.
        
        MEMORIES:
        {memories}
        
        RESPONSE FORMAT:
        ## Strengths
        - ...
        
        ## Weaknesses
        - ...
        
        ## Actionable Suggestions
        - ...
        
        ## Potential Issues
        - ...
    '''
    
    raw_response = together_client.batch_response(
        prompt=prompt,
        model=llama405bt,
        max_tokens=1500
    )
    return raw_response['response']


def analyze_behavioral_psychologist(memories) -> str:
    prompt = f'''
        You are a Behavioral Psychologist analyzing the following memory logs to understand student behaviors in learning interactions.
        
        ANALYSIS OBJECTIVE: Identify behavioral patterns that influence learning outcomes.
        
        ANALYSIS COMPONENTS:
        - Strengths: Recognize positive behaviors that support effective learning.
        - Weaknesses: Highlight negative or counterproductive behaviors.
        - Actionable Suggestions: Recommend strategies to reinforce positive behaviors and mitigate negative ones.
        - Potential Issues: Note ethical concerns or unintended consequences of behavior interventions.
        
        MEMORIES:
        {memories}
        
        RESPONSE FORMAT:
        ## Strengths
        - ...
        
        ## Weaknesses
        - ...
        
        ## Actionable Suggestions
        - ...
        
        ## Potential Issues
        - ...
    '''
    
    raw_response = together_client.batch_response(
        prompt=prompt,
        model=llama405bt,
        max_tokens=1500
    )
    return raw_response['response']


def analyze_memory_scientist(memories) -> str:
    prompt = f'''
        You are a Memory Scientist evaluating the effectiveness of memory formation and retention strategies in the following memory logs derived from student-AI tutor interactions.
        
        ANALYSIS OBJECTIVE: Assess how well the AI tutor facilitates memory encoding and retrieval.
        
        ANALYSIS COMPONENTS:
        - Strengths: Identify effective memory retention techniques used.
        - Weaknesses: Highlight gaps in memory support and potential forgetting issues.
        - Actionable Suggestions: Provide recommendations to enhance memory retention strategies.
        - Potential Issues: Note any cognitive overload or dependency on memory aids.
        
        MEMORIES:
        {memories}
        
        RESPONSE FORMAT:
        ## Strengths
        - ...
        
        ## Weaknesses
        - ...
        
        ## Actionable Suggestions
        - ...
        
        ## Potential Issues
        - ...
    '''
    
    raw_response = together_client.batch_response(
        prompt=prompt,
        model=llama405bt,
        max_tokens=1500
    )
    return raw_response['response']


def analyze_cognitive_load_analyst(memories) -> str:
    prompt = f'''
        You are a Cognitive Load Analyst evaluating the following memory logs to assess the cognitive demands placed on students during interactions with the AI tutor.
        
        ANALYSIS OBJECTIVE: Determine if the cognitive load is optimized for effective learning.
        
        ANALYSIS COMPONENTS:
        - Strengths: Identify areas where cognitive load is appropriately managed.
        - Weaknesses: Highlight instances of cognitive overload or underuse.
        - Actionable Suggestions: Provide strategies to balance intrinsic, extraneous, and germane cognitive loads.
        - Potential Issues: Note any risks related to cognitive fatigue or disengagement.
        
        MEMORIES:
        {memories}
        
        RESPONSE FORMAT:
        ## Strengths
        - ...
        
        ## Weaknesses
        - ...
        
        ## Actionable Suggestions
        - ...
        
        ## Potential Issues
        - ...
    '''
    
    raw_response = together_client.batch_response(
        prompt=prompt,
        model=llama405bt,
        max_tokens=1500
    )
    return raw_response['response']


def analysis_synthesis(analyses) -> str:
    combined_analyses = ''
    for expert, analysis in analyses.items():
        combined_analyses += f"### {expert}\n{analysis}\n\n"

    prompt = f'''
        You are the Master Analyst responsible for synthesizing the following analyses from various educational experts into a cohesive, one-page report. This report will be shared with students, teachers, and parents to personalize the student's academic environment.

        Focus on creating a clear, concise, and comprehensive summary that highlights key strengths, areas for improvement, actionable recommendations, and any potential issues. Ensure the language is accessible to non-experts and emphasizes actionable insights.

        ANALYSIS DATA:
        {combined_analyses}

        REPORT FORMAT:
        - **Overview**
        - **Key Strengths**
        - **Areas for Improvement**
        - **Actionable Recommendations**
        - **Potential Concerns**

        RESPONSE FORMAT:
        # Overview
        Brief summary of the student's current academic status and interactions.

        # Key Strengths
        - ...

        # Areas for Improvement
        - ...

        # Actionable Recommendations
        - ...

        # Potential Concerns
        - ...
    '''

    raw_response = together_client.batch_response(
        prompt=prompt,
        model=llama405bt,
        max_tokens=1500
    )
    return raw_response['response']


def initialize_analysis_workflow(user: str):    
    message_history = get_message_history(user)
    memories = retrieve_context(user)

    raw_selected_agents = select_analysis_experts(message_history, memories)
    selected_agents = raw_selected_agents.split('|')

    message_agents = {
        'educational_psychologist': analyze_educational_psychologist,
        # 'communication_specialist': analyze_communication_specialist,
        # 'instructional_designer': analyze_instructional_designer,
        'cognitive_scientist': analyze_cognitive_scientist
    }

    memory_agents = {
        'learning_analytics_specialist': analyze_learning_analytics_specialist,
        # 'behavioral_psychologist': analyze_behavioral_psychologist,
        # 'memory_scientist': analyze_memory_scientist,
        'cognitive_load_analyst': analyze_cognitive_load_analyst
    }

    analysis_results = {}

    for agent in selected_agents:
        if agent in message_agents:
            analysis_results[agent] = message_agents[agent](message_history)
        elif agent in memory_agents:
            analysis_results[agent] = memory_agents[agent](memories)

    analysis_results['synthesis'] = analysis_synthesis(analysis_results)
    analysis = Analysis(user=user, **analysis_results)
    save_analysis(analysis)

    return True
