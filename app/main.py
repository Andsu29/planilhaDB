from flask import Flask, request, jsonify
import pymysql
import pandas as pd
import dotenv
import os

dotenv.load_dotenv()

app = Flask(__name__)

def create_connection():
  try:
    return pymysql.connect(
      host=os.environ['MYSQL_HOST'],
      user=os.environ['MYSQL_USER'],
      password=os.environ['MYSQL_PASSWORD'],
      database=os.environ['MYSQL_DATABASE'],
    )
  except pymysql.Connection.Error as e:
    return jsonify({"Erro de conexão com o banco de dados": e})


def inserir_dados(dados):
  try:
    connection = create_connection()
    with connection:
      with connection.cursor() as cursor:
        for index, dado in dados.iterrows():
          query = "INSERT INTO usuarios (nome, sobrenome, idade) VALUES (%s, %s, %s)"
          values = (dado['Nome'], dado['Sobrenome'], dado['Idade'])
          cursor.execute(query, values)
        connection.commit()
  except pymysql.DataError as e:
    return jsonify({"Erro ao inserir dados": e})


@app.route('/upload', methods=['POST'])
def upload_csv():
  if 'file' not in request.files:
    return jsonify({"Erro": "Sem arquivo"}), 400
  
  file = request.files['file']

  if file.filename == '':
    return jsonify({"Erro": "Selecione um arquivo"}), 400
  
  if 'file' and file.filename.endswith('csv'):
    dados = pd.read_csv(file)
    inserir_dados(dados)
    return jsonify({"Mensagem": "Dados inseridos"}), 200
  

@app.route('/')
def dados():
  try:
    connection = create_connection()
    with connection:
      with connection.cursor() as cursor:
        query = "SELECT * FROM usuarios"
        cursor.execute(query)
        connection.commit()
  except pymysql.MySQLError as e:
    return jsonify({"Erro ao buscar dados": e})



if __name__ == '__main__':
  app.run(host="0.0.0.0", port=8000)