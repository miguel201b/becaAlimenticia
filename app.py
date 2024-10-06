from flask import Flask, render_template, jsonify, request
from models import Tutor, Alumno, ApoyoAlimenticio, Session
from sqlalchemy import func

class AlumnoResult:
    def __init__(self, nombre_completo, cuenta, prioridad, comentarios):
        self.nombre = nombre_completo
        self.cuenta = cuenta
        self.prioridad = prioridad
        self.comentarios = comentarios

    def __repr__(self):
        return (f"AlumnoResult(nombre={self.nombre}, cuenta={self.cuenta}, "
                f"prioridad={self.prioridad}, comentarios={self.comentarios})")


def obt_tutores():
    session = Session()
    tutores = session.query(Tutor).all()
    return tutores
    pass

app = Flask(__name__)


@app.route('/enviar/<int:cuenta>', methods=['POST'])
def enviar_datos(cuenta):
    session = Session()
    # Obtener los datos enviados desde el formulario o frontend
    data = request.json  # Esto asume que los datos se envían como JSON
    # Buscar el registro en ApoyoAlimenticio que corresponde a la cuenta del alumno
    apoyo = session.query(ApoyoAlimenticio).filter_by(cuenta=cuenta).first()
    if not apoyo:
        return jsonify({"error": "Alumno no encontrado"}), 404
    # Actualizar los campos de prioridad y comentarios
    prioridad = data.get('prioridad')
    comentarios = data.get('comentarios')
    # Asignar los nuevos valores si existen
    if prioridad:
        apoyo.prioridad = int(prioridad)
    apoyo.comentarios = comentarios
    # Guardar los cambios en la base de datos
    try:
        session.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route('/guardar_todos', methods=['POST'])
def guardar_todos():
    session = Session()
    try:
        # Obtener los datos enviados desde el frontend
        data = request.json  # Esto asume que los datos se envían como JSON

        # Iterar sobre la lista de alumnos modificados
        for alumno in data:
            cuenta = alumno.get('cuenta')
            prioridad = alumno.get('prioridad')
            comentarios = alumno.get('comentarios')

            # Buscar el registro en ApoyoAlimenticio que corresponde a la cuenta del alumno
            apoyo = session.query(ApoyoAlimenticio).filter_by(cuenta=cuenta).first()
            if not apoyo:
                continue  # Si el alumno no existe, continuar con el siguiente

            # Actualizar los campos de prioridad y comentarios
            if prioridad:
                apoyo.prioridad = int(prioridad)
            apoyo.comentarios = comentarios

        # Guardar los cambios en la base de datos
        session.commit()
        return jsonify({"status": "success"}), 200

    except Exception as e:
        session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route('/')
def index():
    return 'aplicacion web para filtrar a los alumnos que recibiran la beca alimenticia'

@app.route('/<string:id>')
def tutor_pagina(id):
    session = Session()
    # Buscar el tutor por identificador
    tutor = session.query(Tutor).filter_by(identificador=id).first()
    # Validar si el tutor existe
    if not tutor:
        return jsonify({"error": "Tutor no encontrado"}), 404
    # Hacer el JOIN y devolver objetos de la clase AlumnoResult
    alumnos_query = (session.query(
                        func.concat(Alumno.nombre, ' ', Alumno.p_apellido, ' ', Alumno.s_apellido).label('nombre_completo'),
                        Alumno.cuenta,
                        ApoyoAlimenticio.prioridad,   # Acceso a prioridad
                        ApoyoAlimenticio.comentarios)
                        .join(ApoyoAlimenticio, ApoyoAlimenticio.cuenta == Alumno.cuenta)
                        .filter(ApoyoAlimenticio.tutor == tutor.id))
    # Crear instancias de AlumnoResult con los resultados de la consulta
    alumnos = [AlumnoResult(nombre_completo, cuenta, prioridad, comentarios) for nombre_completo, cuenta, prioridad, comentarios in alumnos_query.all()]
    # Pasar los alumnos como objetos a la plantilla
    return render_template('tutor.html', Tutor=tutor, Alumnos=alumnos)

if __name__ == '__main__':
    app.run()

