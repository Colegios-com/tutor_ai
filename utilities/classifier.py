from init.cohere import cohere_client
from cohere import ClassifyExample

examples = [
    ClassifyExample(text='Identificación de Estándares de Aprendizaje: Incluir más objetivos.', label='rewrite'),
    ClassifyExample(text='Identificación de Estándares de Aprendizaje: Cambiar la sección de objetivos.', label='rewrite'),
    ClassifyExample(text='Identificación de Estándares de Aprendizaje: Reescribir la introducción.', label='rewrite'),
    ClassifyExample(text='Identificación de Estándares de Aprendizaje: Reordenar las conexiones interdisciplinarias.', label='rewrite'),
    ClassifyExample(text='Identificación de Estándares de Aprendizaje: Elaborar planificación semanal.', label='new_document'),
    ClassifyExample(text='Identificación de Estándares de Aprendizaje: Crear una hoja de trabajo.', label='new_document'),
    ClassifyExample(text='Identificación de Estándares de Aprendizaje: Hacer una planificación de clase.', label='new_document'),
    ClassifyExample(text='Identificación de Estándares de Aprendizaje: Elaborar un examen de respuesta corta.', label='new_document'),

    ClassifyExample(text='Planificación de Clase: Extender tiempo de actividad principal.', label='rewrite'),
    ClassifyExample(text='Planificación de Clase: Agregar actividades principales.', label='rewrite'),
    ClassifyExample(text='Planificación de Clase: Cambiar enfoque a uno distinto.', label='rewrite'),
    ClassifyExample(text='Planificación de Clase: Reescribir para alumnos avanzados.', label='rewrite'),
    ClassifyExample(text='Planificación de Clase: Agregar hoja de trabajo.', label='new_document'),
    ClassifyExample(text='Planificación de Clase: Elaborar planificación semanal.', label='new_document'),
    ClassifyExample(text='Planificación de Clase: Crear examen sorpresa.', label='new_document'),
    ClassifyExample(text='Planificación de Clase: Hacer una hoja de vocabulario.', label='new_document'),

    ClassifyExample(text='Planificación Semanal: Reordenar el contenido.', label='rewrite'),
    ClassifyExample(text='Planificación Semanal: Extender el material cubierto del primer día al segundo día.', label='rewrite'),
    ClassifyExample(text='Planificación Semanal: Reescribir el contenido de los primeros dos días.', label='rewrite'),
    ClassifyExample(text='Planificación Semanal: Enfocarse en el tema de la primera clase.', label='rewrite'),
    ClassifyExample(text='Planificación Semanal: Agregar hojas de trabajo para cada día.', label='new_document'),
    ClassifyExample(text='Planificación Semanal: Crear un examen para el final de la semana.', label='new_document'),
    ClassifyExample(text='Planificación Semanal: Identificar los estándares de aprendizaje.', label='new_document'),

    ClassifyExample(text='Planificación Mensual: Cabiar a actividades más creativas.', label='rewrite'),
    ClassifyExample(text='Planificación Mensual: Extender la cantidad de objetivos cada semana.', label='rewrite'),
    ClassifyExample(text='Planificación Mensual: Reescribir para incrementar la dificultad.', label='rewrite'),
    ClassifyExample(text='Planificación Mensual: Agregar más actividades semanales.', label='rewrite'),
    ClassifyExample(text='Planificación Mensual: Identificar las técnicas de enseñanza más apropiadas.', label='new_document'),
    ClassifyExample(text='Planificación Mensual: Elaborar una guía de estudio.', label='new_document'),
    ClassifyExample(text='Planificación Mensual: Crear un examen de repaso.', label='new_document'),
    ClassifyExample(text='Planificación Mensual: Hacer una hoja de trabajo para cada semana.', label='new_document'),

    ClassifyExample(text='Hoja de Trabajo: Simplificar instrucciones.', label='rewrite'),
    ClassifyExample(text='Hoja de Trabajo: Añadir más ejercicios.', label='rewrite'),
    ClassifyExample(text='Hoja de Trabajo: Cambiar el formato de la hoja.', label='rewrite'),
    ClassifyExample(text='Hoja de Trabajo: Generar 25 preguntas.', label='rewrite'),
    ClassifyExample(text='Hoja de Trabajo: Reescribir para estudiantes de nivel básico.', label='rewrite'),
    ClassifyExample(text='Hoja de Trabajo: Crear versión para estudiantes avanzados.', label='new_document'),
    ClassifyExample(text='Hoja de Trabajo: Elaborar hoja de repaso.', label='new_document'),
    ClassifyExample(text='Hoja de Trabajo: Crear examen para validar el aprendijaze.', label='new_document'),
    ClassifyExample(text='Hoja de Trabajo: Hacer una hoja de vocabulario.', label='new_document'),

    ClassifyExample(text='Construcción de Vocabulario: Añadir ejemplos contextuales.', label='rewrite'),
    ClassifyExample(text='Construcción de Vocabulario: Agregar más palabras.', label='rewrite'),
    ClassifyExample(text='Construcción de Vocabulario: Cambiar el orden de las palabras.', label='rewrite'),
    ClassifyExample(text='Construcción de Vocabulario: Cambiarlo para que sean 15 palabras.', label='rewrite'),
    ClassifyExample(text='Construcción de Vocabulario: Vincular con cultura local.', label='rewrite'),
    ClassifyExample(text='Construcción de Vocabulario: Elaborar hoja de trabajo.', label='new_document'),
    ClassifyExample(text='Construcción de Vocabulario: Crear examen para acompañar.', label='new_document'),
    ClassifyExample(text='Construcción de Vocabulario: Hacer planificación para enseñar el material.', label='new_document'),
    ClassifyExample(text='Construcción de Vocabulario: Crear actividad para reforzar el contenido.', label='new_document'),


    ClassifyExample(text='Debates en Grupo: Modificar criterios de participación.', label='rewrite'),
    ClassifyExample(text='Debates en Grupo: Cambiar roles asignados.', label='rewrite'),
    ClassifyExample(text='Debates en Grupo: Reescribir guía de discusión.', label='rewrite'),
    ClassifyExample(text='Debates en Grupo: Añadir preguntas de seguimiento.', label='rewrite'),
    ClassifyExample(text='Debates en Grupo: Preparar guía del moderador.', label='new_document'),
    ClassifyExample(text='Debates en Grupo: Crear lista de vocabulario para participantes.', label='new_document'),
    ClassifyExample(text='Debates en Grupo: Hacer una hoja de trabajo para preparar el debate.', label='new_document'),
    ClassifyExample(text='Debates en Grupo: Crear un examen para evaluar la participación.', label='new_document'),

    ClassifyExample(text='Presentación Oral: Ajustar tiempo de exposición.', label='rewrite'),
    ClassifyExample(text='Presentación Oral: Cambiar el orden de los temas.', label='rewrite'),
    ClassifyExample(text='Presentación Oral: Reescribir guión de presentación.', label='rewrite'),
    ClassifyExample(text='Presentación Oral: Incluir preguntas interactivas.', label='rewrite'),
    ClassifyExample(text='Presentación Oral: Diseñar plantilla de diapositivas.', label='new_document'),
    ClassifyExample(text='Presentación Oral: Crear guía de estudio para acompañar.', label='new_document'),
    ClassifyExample(text='Presentación Oral: Hacer una hoja de trabajo para preparar la presentación.', label='new_document'),
    ClassifyExample(text='Presentación Oral: Crear un examen para evaluar la atención prestada durante la presentación.', label='new_document'),

    ClassifyExample(text='Exámenes de Opción Múltiple: Reformular preguntas ambiguas.', label='rewrite'),
    ClassifyExample(text='Exámenes de Opción Múltiple: Cambiar opciones de respuesta.', label='rewrite'),
    ClassifyExample(text='Exámenes de Opción Múltiple: Extender el examen.', label='rewrite'),
    ClassifyExample(text='Exámenes de Opción Múltiple: Añadir preguntas de repaso.', label='rewrite'),
    ClassifyExample(text='Exámenes de Opción Múltiple: Crear un total de 30 preguntas.', label='rewrite'),
    ClassifyExample(text='Exámenes de Opción Múltiple: Generar versión oral.', label='new_document'),
    ClassifyExample(text='Exámenes de Opción Múltiple: Convertir en examen de respuesta corta.', label='new_document'),
    ClassifyExample(text='Exámenes de Opción Múltiple: Diseñar una clase de repaso.', label='new_document'),
    ClassifyExample(text='Exámenes de Opción Múltiple: Crear un examen de reposición.', label='new_document'),

    ClassifyExample(text='Exámenes de Ensayo: Incluir pregunta de reflexión.', label='rewrite'),
    ClassifyExample(text='Exámenes de Ensayo: Cambiar el formato de la pregunta.', label='rewrite'),
    ClassifyExample(text='Exámenes de Ensayo: Extender la longitud de la respuesta.', label='rewrite'),
    ClassifyExample(text='Exámenes de Ensayo: Recortar a sólo 2 preguntas.', label='rewrite'),
    ClassifyExample(text='Exámenes de Ensayo: Hacerlo de 5 preguntas.', label='rewrite'),
    ClassifyExample(text='Exámenes de Ensayo: Añadir criterios de evaluación.', label='rewrite'),
    ClassifyExample(text='Exámenes de Ensayo: Crear hoja de vocuabulario.', label='new_document'),
    ClassifyExample(text='Exámenes de Ensayo: Agregar examen de respuesta corta para complementar.', label='new_document'),
    ClassifyExample(text='Exámenes de Ensayo: Diseñar guía de estudio.', label='new_document'),
    ClassifyExample(text='Exámenes de Ensayo: Hacer una hoja de trabajo para preparar el examen.', label='new_document'),
]


def classify(instructions):
    response = cohere_client.classify(
            inputs=[instructions],
            examples=examples,
        )
    top_result = response.classifications[0]
    if top_result.confidence >= 0.8:
        return top_result.prediction
    return 'aldous_bot'