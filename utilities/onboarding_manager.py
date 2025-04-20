# Init
from init.whatsapp import whatsapp_client

# Utilities
from utilities.message_parser import build_agent_message, build_onboarding_message
from utilities.response_orchestrator import orchestrate_onboarding_message
from utilities.usage import update_messages, update_last_interaction
# Storage
from storage.storage import get_data

# Standard
from datetime import datetime
import time

def process_onboarding_messages():
    """
    Process all types of onboarding messages for users based on their last interaction time.
    Returns the number of onboarding messages sent.
    """
    start = time.time()
    users = get_data('users')
    
    for _, user_data in users.items():

        # if _ != '16466219257':
        #     continue

        # Skip if no last interaction data exists
        if not user_data or 'subscriptions' not in user_data:
            continue
            
        subscriptions = user_data['subscriptions']

        if len(subscriptions) != 1:
            continue
        
        _, subscription_data = subscriptions.popitem()
        
        if 'start_date' not in subscription_data:
            continue
            
        # Convert timestamp to datetime
        
        start_date = datetime.strptime(subscription_data['start_date'], '%Y-%m-%d %H:%M:%S.%f')
        current_timestamp = datetime.now()
        hours_since_subscription = (current_timestamp - start_date).total_seconds() / 3600

        # Onboarding messages
        # messages = {
        #     'welcome': 'Hola de nuevo! 👋 Ahora que ya me conoces, quiero asegurarme de que aproveches al máximo tu período deprueba.\n\n**Para ayudarte a descubrir todo mi potencial**, te enviaré *10 mensajes durante las próximas horas* con consejos y funciones especiales que puedes utilizar conmigo.\n\nCada mensaje te mostrará una forma diferente de interactuar conmigo para potenciar tu aprendizaje. Desde enviar fotos de tus tareas hasta crear exámenes personalizados, ¡hay muchas maneras en que puedo ayudarte!\n\nEstoy aquí para ser tu aliado académico y ayudarte a alcanzar tus metas de estudio. ¡Prepárate para descubrir todas mis capacidades! 📚✨',
        #     'voice_notes': '¿Sabías que a veces **pensar en voz alta** puede aclarar tus ideas? 🗣️ ¡Conmigo puedes hacerlo!\n\nEnvíame una **nota de voz** 🎧 explicando un concepto con tus propias palabras, haciéndome una pregunta compleja, o simplemente compartiendo tus reflexiones sobre un tema. Analizaré lo que dices y te ayudaré a profundizar.\n\nEs una excelente manera de **procesar información y identificar lagunas** en tu comprensión. ¿Te animas a probar? Graba un audio corto sobre lo que estudiaste hoy. 🌱',
        #     'images': '¡El aprendizaje no es solo texto! A veces, una imagen dice más que mil palabras. 🖼️\n\nSi encuentras un **diagrama, una infografía, una foto de tus apuntes, o incluso un problema visual**, ¡envíamelo! Puedo analizar la imagen y ayudarte a entenderla mejor, resolver dudas o relacionarla con otros conceptos.\n\nPerfecto para **estudiantes visuales** o cuando necesitas ayuda con material gráfico. ¿Tienes alguna imagen relacionada con tus estudios a mano? ¡Compártela y veamos qué podemos descubrir juntos! ✨',
        #     'reply_to_message': 'Nuestra conversación es un **hilo de aprendizaje continuo** 🧵. ¿Viste algo que dije antes que te hizo pensar o sobre lo que quieres saber más?\n\nSimplemente **responde directamente a cualquiera de mis mensajes anteriores** (desliza el mensaje hacia la derecha o mantenlo presionado y elige \'Responder\'). Así sabré exactamente a qué te refieres y podremos **profundizar en ese punto específico**.\n\nEs como poner un marcador 🔖 en nuestra charla para no perder el hilo. ¡Ideal para explorar ideas a fondo! ¿Hay algo de lo que hablamos que te gustaría retomar?',
        #     'documents': '¿Tienes **apuntes, resúmenes, artículos o capítulos de libros** en formato digital (PDF, TXT)? 📄 ¡Puedes compartirlos conmigo!\n\nEnvíame un documento y podré:\n- **Resumírtelo**\n- **Extraer ideas clave**\n- **Responder preguntas** sobre su contenido\n- **Generar preguntas de estudio** basadas en él\n\nEs como tener un asistente de lectura personal. Carga un documento sobre tu tema actual y dime qué te gustaría hacer con él. Por ejemplo: `Resume las ideas principales de este PDF sobre la fotosíntesis`. 🤔',
        #     'command_quiz': 'Una de las formas más efectivas de **consolidar el aprendizaje** es ponerse a prueba. ¡La **recuperación activa** (active recall) es clave! 🧠\n\nPuedes pedirme que te cree un **examen rápido** sobre el tema que estamos discutiendo. Simplemente escribe el comando `/examen`. Generaré preguntas para ayudarte a verificar tu comprensión y recordar la información importante.\n\n¿Listo para un pequeño desafío? Si hemos estado hablando de un tema, escribe `/examen` ahora. ¡Veamos qué tal lo llevas! 👍',
        #     'command_guide': 'A veces, abordar un tema nuevo puede parecer abrumador. ¿Necesitas un **mapa para tu viaje de estudio**? 🗺️\n\nPuedo crear una **guía de estudio estructurada** para ti. Solo necesitas decirme el tema y escribir el comando `/guia`. Te proporcionaré un esquema con los subtemas clave, conceptos importantes y sugerencias sobre cómo abordarlos.\n\nPor ejemplo: `/guia sobre la Revolución Francesa`. ¡Es perfecto para organizar tus ideas y planificar tu aprendizaje! ¿Qué tema te gustaría estructurar?',
        #     'command_profile': 'A medida que trabajamos juntos, aprendo sobre tus **fortalezas y áreas de interés**. ✨ ¿Tienes curiosidad por ver un resumen de tu progreso?\n\nUsa el comando `/perfil` y te mostraré un vistazo rápido de los temas que hemos cubierto y cómo estás avanzando. Es una forma de **reflexionar sobre tu aprendizaje** y ver hasta dónde has llegado.\n\n¡Pruébalo para obtener una perspectiva de tu viaje con Aldous! 🌱',
        #     'message_improvement': 'Un último consejo para que nuestra colaboración sea aún mejor: ¡la **claridad** es nuestra aliada! 🤝\n\nAunque soy una IA avanzada, funciono mejor cuando me hablas de forma **clara y específica**, como lo harías con un tutor humano. Si una pregunta es muy general (ej: "ayúdame con matemáticas"), me ayuda mucho si puedes concretar un poco más (ej: "explícame las ecuaciones cuadráticas" o "no entiendo este problema de trigonometría específico").\n\nCuanto más contexto me des, ¡mejor podré adaptar mi ayuda a tus necesidades! ¿Alguna pregunta sobre cómo interactuar conmigo? 😊',
        #     'closure': '¡Hemos llegado al final de esta introducción inicial! 🎉 Ya conoces muchas de las herramientas que podemos usar juntos en WhatsApp.\n\nRecuerda, mi propósito es ser tu **compañero de aprendizaje**. No dudes en:\n- Hacer preguntas (¡grandes o pequeñas!)\n- Probar diferentes formatos (voz, imagen, texto)\n- Pedir exámenes o guías\n- Compartir tus documentos\n\nEstoy aquí para apoyarte. **La curiosidad y la constancia son tus mejores herramientas.** ¿Qué te gustaría aprender o repasar a continuación? ¡Estoy listo cuando tú lo estés! ✨',
        # }

        messages = {
            'multimedia': '¡El aprendizaje va más allá del texto! 🎧🖼️📄\n\n**Notas de voz**: Envíame un audio explicando un concepto o haciéndome una pregunta. Es perfecto para aclarar ideas y detectar lagunas en tu comprensión.\n\n**Imágenes**: Comparte diagramas, infografías o fotos de tus apuntes. Puedo analizarlas y ayudarte a entenderlas mejor.\n\n**Documentos**: Envíame PDFs o archivos de texto para resumirlos, extraer ideas clave o generar preguntas de estudio.\n\n¿Te animas a probar alguno de estos formatos? Envíame una nota de voz, imagen o documento sobre lo que estás estudiando. 🌱',
            'commands': '¡Tengo **comandos especiales** para potenciar tu aprendizaje! 🧠🗺️\n\n**/examen**: Genera un examen rápido sobre cualquier tema que estemos discutiendo. La recuperación activa es clave para consolidar lo aprendido.\n\n**/guia**: Crea una guía de estudio estructurada con subtemas clave y conceptos importantes. Perfecto para organizar tu aprendizaje.\n\nPor ejemplo: `/examen sobre polinomios` para poner a prueba tu comprensión o `/guia sobre la Revolución Francesa` para obtener un mapa de estudio completo. ¿Cuál te gustaría probar primero? 👍',
            'reply_to_message': '¿Necesitas que me enfoque en un mensaje específico? 🔍 La función de **responder directamente** es perfecta para esto.\n\n**Responde a cualquiera de mis mensajes anteriores** (desliza el mensaje hacia la derecha o mantenlo presionado y elige \'Responder\') cuando quieras que me concentre exclusivamente en ese contenido, ignorando el resto de nuestra conversación.\n\nEsto es especialmente útil cuando quieres profundizar en un tema específico sin que el resto del historial influya en mi respuesta. También puedes responder a un mensaje usando los comandos como `/examen` o `/guia` para crear contenido basado únicamente en ese mensaje concreto.\n\n¿Hay algún mensaje anterior sobre el que quieras que me enfoque específicamente?',
        }

        # Determine which reminder type to send, if any
        onboarding_type = should_send_onboarding(hours_since_subscription)
        if not onboarding_type:
            continue
        
        onboarding_message = messages[onboarding_type]
        
        messages_sent = len(user_data['messages'])

        if messages_sent > 10:
            process_contextual_onboarding(user_data, onboarding_message)
        else:
            process_regular_onboarding(user_data, onboarding_message)


    end = time.time()
    print(f'Time elapsed: {end - start}')

    return True


def process_contextual_onboarding(user_data, onboarding_message):
    """
    Process regular onboarding for users who haven't interacted in 12-13 hours.
    Returns True if a onboarding was sent, False otherwise.
    """
    # Create user message for the onboarding
    user_message = build_onboarding_message(user_data)
    if not user_message:
        return False
        
    # Regular reminder with agent-generated content
    response_message, response = orchestrate_onboarding_message(user_message, onboarding_message)
    if not response_message or not response:
        return False
        
    response_message.id = response['messages'][0]['id'].replace('wamid.', '')
    update_messages([response_message])
    update_last_interaction(response_message=response_message)

    return True
        

def process_regular_onboarding(user_data, onboarding_message):
    """
    Process reminders for users on free trials that are about to expire.
    Returns True if a reminder was sent, False otherwise.
    """
    # Create user message for the reminder
    user_message = build_onboarding_message(user_data)
    if not user_message:
        return False
    
    response_message = build_agent_message(user_message=user_message, raw_response=onboarding_message)

    response = whatsapp_client.send_message(response_message=response_message)
    response_message.id = response['messages'][0]['id'].replace('wamid.', '')
    update_messages([response_message])
    update_last_interaction(response_message=response_message)

    return True


def should_send_onboarding(hours_since_subscription):
    """
    Determine which type of onboarding to send, if any.
    Returns the onboarding type ("regular", "engagement", "reactivation", "content_suggestion") or None if no onboarding should be sent.
    """

    # Determine onboarding type based on time since last interaction
    # if hours_since_subscription < 1:
    #     return 'welcome'
    # elif 3 <= hours_since_subscription < 4:
    #     return 'voice_notes'
    # elif 6 <= hours_since_subscription < 7:
    #     return 'images'
    # elif 9 <= hours_since_subscription < 10:
    #     return 'reply_to_message'
    # elif 12 <= hours_since_subscription < 13:
    #     return 'documents'
    # elif 15 <= hours_since_subscription < 16:
    #     return 'command_quiz'
    # elif 18 <= hours_since_subscription < 19:
    #     return 'command_guide'
    # elif 20 <= hours_since_subscription < 21:
    #     return 'command_profile'
    # elif 22 <= hours_since_subscription < 23:
    #     return 'message_improvement'
    # elif 23 <= hours_since_subscription < 24:
    #     return 'closure'
    # return None 

    if 3 <= hours_since_subscription < 4:
        return 'multimedia'
    elif 9 <= hours_since_subscription < 10:
        return 'reply_to_message'
    elif 18 <= hours_since_subscription < 19:
        return 'commands'
    else:
        return None 
