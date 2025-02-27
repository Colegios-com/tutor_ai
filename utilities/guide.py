from init.openai import openai_client

text_model = 'accounts/fireworks/models/llama-v3p3-70b-instruct'


def create_robotics_problem(theme: str, grade_level: str, learning_criteria: str, components: list[str], team_size: int) -> str:
    system_prompt = f'''
        Actúa como un experto en pedagogía STEAM con 15 años de experiencia en diseño de retos robóticos. Genera un desafío educativo en español que cumpla rigurosamente con la siguiente estructura, utilizando las variables proporcionadas {grade_level}, {team_size}, {components}, y {learning_criteria}:

        REQUISITOS GENERALES:
        - El desafío debe ser centrado en {theme}
        - El desafío debe ser motivador y accesible para el nivel indicado
        - La progresión de las misiones debe ser gradual y lógica
        - Los conceptos técnicos deben presentarse como guías, no soluciones
        - Las métricas de evaluación deben ser claras y medibles
        - La narrativa debe mantenerse consistente a lo largo de todo el desafío

        REQUSITOS ESPECÍFICOS:
        1. Lenguaje y Formato
        - Usar terminología técnica precisa pero accesible para {grade_level}
        - Implementar formato markdown exclusivamente
        - Mantener coherencia en la documentación

        2. Elementos Pedagógicos
        - Alinear cada elemento con {learning_criteria}
        - Usar verbos de Bloom apropiados al nivel
        - Asegurar progresión lógica entre misiones

        3. Elementos de Gamificación
        - Incluir nombres temáticos para cada misión
        - Implementar sistema de logros desbloqueables
        - Mantener narrativa consistente

        4. Métricas y Evaluación
        - Incluir variables numéricas específicas en todos los checklists
        - Proporcionar criterios de evaluación medibles
        - Establecer puntos de control claros

        <QUEST_DETAILS>
        [Instruction: Provide a detailed challenge description that includes the title, narrative context, mission objectives, and expected outcomes.]
        # [Gameified title with accompanying emoji]
            - Setting
            - Point in Time
            - Context of the mission

        ## Narrativa
            - Mission description with engaging storytelling
            - Context and motivation for students
            - Main objectives and expected outcomes of the mission

        <TECHNICAL_REQUIREMENTS>
        [Instruction: List the required hardware components, optional extensions, relevant technical specifications, vocabulary and technical concepts for the quest given the specific requirements outlined previously.]
        ## Componentes de Hardware
            - Required components: {components}
            - Optional extensions: [List of additional components]
            - Technical specifications: [Specific requirements]

        ## Requisitos de Software
            - Software requirements: [List of necessary functions]
            - Programming concepts: [Key technical concepts]
            - Troubleshooting strategies: [Common debugging methods]

        ## Vocabulario y Conceptos Clave
            - Programming terminology: [List of key terms]
            - Technical concepts: [Core programming concepts]


        <MISSION_DETAILS>
        [Instruction: Generate 5 missions with increasing complexity that breaks down the complete challenge into manageable parts. Each mission should focus on a specific technical concept and include a clear objective, detailed activities, and a conceptual guide.]
        ## [Gameified title with accompanying emoji]

            ### Objetivos y Actividades
            [Instruction: For each mission, provide specific objectives, estimated completion time, and 2-3 activities with clear instructions.]
                <EXAMPLE_MISSION>
                ### **Misión 1: "Reparación del Robot"** 🤖
                #### **Objetivos y Actividades**
                - **Objetivo técnico:** Programar el robot para que se mueva hacia adelante y hacia atrás utilizando los 2 motores.
                - **Tiempo estimado:** 30 minutos
                - **Actividades:**
                1. Conectar los motores al robot y programar el movimiento hacia adelante.
                2. Programar el movimiento hacia atrás.
                3. Realizar pruebas para asegurarse de que el robot se mueva correctamente.


            ### Primeros Pasos
            [Instruction: Provide a step-by-step guide for students to get started with the mission. Include preliminary psuedo-code or block arrangement, critical thinking questions, and key technical concepts to consider.]
                <EXAMPLE_STEPS>
                #### **Primeros Pasos**
                    - **Quick start:** Conectar los motores y comenzar a programar.
                    - **Pseudo-código:** `mover_adelante()`, `mover_atras()`
                    - **Preguntas críticas:** ¿Cómo se pueden controlar los motores para lograr el movimiento deseado?
                    - **Conceptos clave:** Control de motores, Programación secuencial

            ### Criterios de Éxito
            [Instruction: Define the success criteria for each mission, including technical metrics, performance indicators, and suggested checkpoints for debugging.]
                <EXAMPLE_CRITERIA>
                #### **Criterios de Éxito**
                - **Criterios de éxito:** El robot se mueve hacia adelante y hacia atrás sin problemas.
                - **Métricas técnicas:** Tiempo de respuesta del robot, distancia recorrida.
                - **Puntos de control:** Verificar conexiones, revisar código, probar en diferentes superficies.

        <EVALUATION_CRITERIA>
        [Instruction: Define a clear three tiered (Bronze, Silver, Gold) evaluation system that includes technical, creative, and collaborative aspects. Make sure these criteria are very specific examples of what would be expected from students in each level.]
            <EXAMPLE_TIER>
            ## Nivel Bronce
            - **Programación:** El robot se mueve hacia adelante y hacia atrás con poco tiempo de respuesta. El sensor de color logra detectar colores primarios. El código es funcional pero no optimizado.
            - **Creatividad:** El diseño del robot es básico pero funcional. Se utilizan colores primarios en la decoración. El robot sigue un patrón de movimiento simple.
            - **Colaboración:** Los miembros del equipo se turnan para programar y probar el robot. Se comparten ideas y se resuelven problemas juntos. Puede haber algunas discusiones pero se resuelven rápidamente.
'''

    response = openai_client.chat.completions.create(
        model=text_model,
        messages=[
            {'role': 'system', 'content': [{'type': 'text', 'text': system_prompt}]},
            {'role': 'user', 'content': [{'type': 'text', 'text': f"Crea un problema de robótica para {grade_level}"}]}
        ]
    )
    return response.choices[0].message.content


def create_solution(problem_statement: str) -> dict:
    system_prompt = f'''
        # Basado en el enunciado del problema:
        {problem_statement}

        Por favor, genere una Guía de Solución detallada para Mentores para cada MISIÓN X (donde X es 1-5), proporcione:
        
        REQUISITOS GENERALES:
        Para cada implementación de código, incluir:
        - Instrucciones claras de construcción bloque por bloque
        - Combinaciones alternativas de bloques para el mismo resultado
        - Arreglos incorrectos comunes de bloques a evitar
        - Consejos para la organización eficiente de bloques
        - Estrategias de depuración específicas para mBlock/Scratch

        La guía debe enfatizar:
        - Conceptos de programación visual basada en bloques
        - Uso adecuado del sistema de eventos de mBlock
        - Uso eficiente de bucles y estructuras de control
        - Uso apropiado de variables y listas
        - Mejores prácticas de integración de sensores
        - Estructura de código limpia y organizada

        Requisitos de Formato:
        - Incluir referencias visuales para los arreglos de bloques
        - Proporcionar separaciones claras entre temas
        - Usar formato consistente para ejemplos de código
        - Incluir un resumen de referencia rápida para cada misión
        - Asegurar un diseño apto para impresión


        # GUÍA DE SOLUCIÓN PARA MENTORES
        [Para cada misión, incluir una sección detallada con los siguientes elementos]
        ## MISIÓN X: [Nombre de la Misión]
        - Duración Estimada: [Tiempo estimado en minutos]
        - Objetivo Técnico: [Descripción del objetivo principal]
        - Habilidad de Bloom: [Nivel cognitivo requerido]
        - Conceptos Clave: [Principales conceptos de programación]

        ## VISIÓN GENERAL DE LA MISIÓN
        - Objetivos Clave de Aprendizaje
        - Prerrequisitos Necesarios
        - Desglose Estimado de Tiempo
        - Desafíos Comunes de los Estudiantes

        ## GUÍA DETALLADA DE IMPLEMENTACIÓN
        ### Configuración Inicial
            - Configuración del Hardware
            - Configuración del Entorno mBlock
            - Pasos Iniciales de Prueba

        ### Implementación Paso a Paso del Código
            - Cada paso debe incluir:
                * Los bloques específicos de mBlock/Scratch a utilizar
                * Captura de pantalla o descripción textual del arreglo de bloques
                * Comportamiento esperado después de cada paso
                * Punto de control de prueba

        ### Pruebas y Validación
            - Pasos de Pruebas Unitarias
            - Pasos de Pruebas de Integración
            - Métricas de Rendimiento
            - Validación de Criterios de Éxito

        ### SOLUCIÓN COMPLETA DEL CÓDIGO
        - Programa completo en mBlock/Scratch con:
            * Estructura principal del programa
            * Todas las funciones/procedimientos requeridos
            * Definiciones de variables
            * Comentarios explicando cada sección
            * Captura de pantalla del arreglo completo de bloques

        ### ESTRATEGIAS DE MENTORÍA
        - Preguntas Guía para Orientar a los Estudiantes
        - Conceptos Erróneos Comunes y Aclaraciones
        - Sugerencias de Andamiaje
        - Consejos para el Seguimiento del Progreso

        ### GUÍA DE SOLUCIÓN DE PROBLEMAS
        - Errores Comunes en la Lógica de Bloques
        - Problemas de Conexión de Hardware
        - Problemas de Calibración de Sensores
        - Problemas de Rendimiento
        - Errores de Ejecución

        ### POSIBILIDADES DE EXTENSIÓN
        - Combinaciones Avanzadas de Bloques
        - Integración de Sensores Adicionales
        - Patrones de Movimiento Complejos
        - Soluciones Alternativas
        - Integración Entre Misiones

        ### LISTA DE VERIFICACIÓN DE EVALUACIÓN
        - Criterios de Implementación Técnica
        - Métricas de Calidad del Código
        - Requisitos de Documentación
        - Evaluación del Trabajo en Equipo

        ### CONSEJOS DE ENSEÑANZA
        - Mejores Prácticas de Programación por Bloques
        - Preguntas Frecuentes de los Estudiantes y Respuestas
        - Sugerencias para la Gestión del Tiempo
        - Consideraciones de Seguridad
        - Estrategias de Gestión de Grupos
'''


    response = openai_client.chat.completions.create(
        model=text_model,
        messages=[
            {'role': 'system', 'content': [{'type': 'text', 'text': system_prompt}]},
            {'role': 'user', 'content': [{'type': 'text', 'text': problem_statement}]}
        ]
    )

    return response.choices[0].message.content


def create_narrative(problem_statement: str, theme: str, components: list) -> str:
    system_prompt = f'''
        Actúa como un "Dungeon Master" educativo especializado en STEM. Crea una narrativa en español con tema {theme} que:

        # 🏰 **Marco Narrativo: [Título del Reino/Tema]**  
        ## 🌍 **Contexto Dinámico**  
        "[Descripción atmosférica de 2 párrafos usando elementos de {theme}]  
        *En un mundo donde [situación problemática relacionada con componentes],  
        los aprendices deben dominar [habilidad técnica] para [objetivo narrativo].  
        Pero cuidado con [elemento antagonista] que [mecánica de desafío]*"

        ## 🧙 **Personajes Arquetípicos**  
        1. **[Aliado Temático]:**  
        - Rol: [Mentor/Sabio/Compañero]  
        - Diálogo clave: *"[Frase que conecta {components[0]} con la trama]"*  
        - Habilidad única: [Asistencia técnica disfrazada de magia/tecnología]  

        2. **[Antagonista Contextual]:**  
        - Motivación: [Obstaculizar progreso usando fallas técnicas]  
        - Táctica: "[Mecánica de error común personificada]"  

        3. **[PNJ de Misión]:**  
        - Necesidad: [Problema que requiere completar objetivo técnico]  
        - Recompensa: [Beneficio narrativo + desbloqueo tecnológico]  

        # 🗺️ **Mapa de Aventuras**  
        ''' + ''.join([f'''
        ### 🌟 **Etapa {i+1}: [Nombre épico]**  
        **Ambiente:** [Descripción temática de entorno técnico]  
        *"¡{["Cuidado con", "Descifra el misterio de", "Supera el"][i%3]} [obstáculo narrativo]  
        que bloquea el camino! Para avanzar, deberán [acción técnica equivalente a Misión {i+1}]"*  

        **Interacción Clave:**  
        [Diálogo/Puzzle que requiere usar {components[i%len(components)]}]  
        ''' for i in range(5)]) + '''

        # 🔮 **Conexiones STEM Ocultas**  
        "- [Elemento narrativo] = [Principio científico/matemático]  
        "- [Habilidad mágica] representa [Ley física/tecnológica]  
        "- [Objeto legendario] simboliza [Componente electrónico]  

        # 🎭 **Mecánicas de Rol Técnico**  
        | Rol del Equipo | Habilidad STEM | Responsabilidad Narrativa |  
        |----------------|----------------|---------------------------|  
        | Ingeniero Real | Programación   | Decodificar pergaminos runa (código) |  
        | Arquitecto Mágico | Diseño estructural | Fortificar defensas (chasis) |  
        | Alquimista Digital | Electrónica    | Preparar pócimas (circuitos) |  

        **Reglas de Inmersión:**  
        1. Cada componente es un "artefacto místico" (ej: sensor ultrasónico = Ojo de Dragón)  
        2. Los errores técnicos generan consecuencias narrativas (código erróneo → maldición temporal)  
        3. Los checklists son "pruebas de alineamiento mágico" con parámetros temáticos  
        4. Incluir 3 "pistas ambientales" que sugieran soluciones técnicas mediante lore  

        **Ejemplo para theme="Piratas":**  
        - **Componentes:** Motores DC = Remos Mecánicos, Sensor luz = Brújula Solar  
        - **Misión 2:** "Calibrar la Brújula Solar para navegar entre Sirenas de Rocío (obstáculos ópticos)"  
        - **Antagonista:** Capitán Cortocircuito que corrompe conexiones eléctricas  
        - **Conexión STEM:** "El timón responde a ángulos precisos (geometría) igual que los motores DC
'''

    response = openai_client.chat.completions.create(
        model=text_model,
        messages=[
            {'role': 'system', 'content': [{'type': 'text', 'text': system_prompt}]},
            {'role': 'user', 'content': [{'type': 'text', 'text': problem_statement}]}
        ]
    )
    return response.choices[0].message.content


def create_guide():
    # Configuration
    GRADE_LEVEL = "7mo grado"
    LEARNING_CRITERIA = "Fundamentos de programación, integración de sensores, trabajo en equipo"
    COMPONENTS = ["2 motores", "sensor de luz", "botón pulsador"]
    TEAM_SIZE = 3
    THEME = "Viaje en el tiempo a un castillo medieval"


    # Generate content
    problem = create_robotics_problem(THEME, GRADE_LEVEL, LEARNING_CRITERIA, COMPONENTS, TEAM_SIZE)
    # solution = create_solution(problem)
    # narrative = create_narrative(problem, THEME, COMPONENTS)

    # Output results
    # print("\n\n=== NARRATIVA DEL PROBLEMA ===")
    # print(narrative)
    print("\n\n=== ENUNCIADO DEL PROBLEMA ===")
    print(problem)
    # print("\n\n=== GUÍA DE SOLUCIÓN ===")
    # print(solution)

