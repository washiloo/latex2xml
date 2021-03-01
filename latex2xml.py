# Last modified: 26feb21 (FEG)
#
# Este módulo contiene todas las funciones necesarias para convertir archivos .tex que contienen preguntas (con un formato específico) en archivos .xml compatibles con el Banco de Preguntas de la plataforma Moodle.
#
# Consultas: fabiangiana@gmail.com
#

import numpy as np
import os
import random

curr_dir = os.getcwd() # Directorio actual

#---------------- FUNCIONES -----------------------------
def read_tex_q(filename): # Función que lee el archivo .tex y extrae las preguntas
  questions = [] # Creo una lista vacía para guardar las preguntas
    
  # Leo el archivo LaTeX
  with open(filename,'r') as file: # Abro el archivo y lo cierro al terminar
    lines = file.readlines() # Leo todas las líneas
    q_idx = find_questions(lines) # Busco los índices de bloques de pregunta
    
    for i in range(0,len(q_idx) - 1): # Itero sobre todas las preguntas 
      q_lines = [] # # Creo una lista vacía para guardar las líneas de una misma pregunta
      
      if(i == len(q_idx) - 2): # Parche para determinar el último índice de la pregunta (todas tienen el %q luego de un \item, menos la última)
        last_idx = q_idx[i + 1]
      else:
        last_idx = q_idx[i + 1] - 1
        
      for line in lines[q_idx[i] + 1:last_idx]: # Itero sobre todas las líneas de la misma pregunta (la primera es %q y la última \item)
        q_lines.append(line) # Engordo la pregunta
      
      questions.append(q_lines) # Agrego la pregunta a la lista

  return questions

def find_questions(q_lines): # Busca los índices de bloques de pregunta
  q_idx = [] # Creo una lista vacía para guardar los índices de bloques de pregunta

  for i in range(len(q_lines)):
    if('%q' in q_lines[i]): # Busco los índices de inicio y fin de los bloques de pregunta
      q_idx.append(i)
  
  return q_idx

def read_question(tmp_string,line): # Función que lee todas las líneas de una pregunta
  if(tmp_string == []):
    tmp_string = line # Inicio el string para esta pregunta con la primera línea
  else:
    tmp_string += line # Concateno esta línea con las anteriores
  
  return tmp_string

def format_line(line): # Convierte comandos de LaTeX en formato HTML (falta comentar mejor)
  if('begin{equat' in line): # Inicio de bloque 'equation'
    line = '<br> $$'
  elif('end{equat' in line): # Fin de bloque 'equation'
    line = '$$ <br>'
  elif('begin{enum' in line): # Inicio de bloque 'enumerate'
    line = '<ol>'
  elif('end{enum' in line): # Fin de bloque 'enumerate'
    line = '</ol>'
  elif('begin{item' in line): # Inicio de bloque 'itemize'
    line = '<ul>'
  elif('end{item' in line): # Fin de bloque 'itemize'
    line = '</ul>'
  elif('\item' in line): # Ítem de una lista (numerada o no)
    line = '</li> ' + escape_chars(line).replace('\item','<li>')
  else: # Línea común
    line = escape_chars(line)
    
  return line

def escape_chars(s): # Escapa los caracteres especiales de HTML
  replace_pairs = (('<','&lt;'),('>','&gt;'),('$','$$')) # Caracteres conflictivos y su versión escapada

  for rp in replace_pairs: # Itero sobre todos los caracteres conflictivos
    s = s.replace(rp[0],rp[1])
    
  return s

def insert_header(quiz,q_category): # Agrega el header al cuestionario, incluyendo la categoría de las preguntas
  quiz += """<?xml version="1.0" encoding="UTF-8"?> 
<quiz>
<!-- question: 0  -->
 <question type="category">
  <category>
   <text>$module$/top/{}</text>
  </category>
  <info format="moodle_auto_format">
  </info>
 </question> \n\n""".format(q_category)

  return quiz
    
def insert_question(quiz,q_lines,q_type,q_format,q_name = ''): # Agrega una pregunta al cuestionario
  q_text = '' # Creo un string vacío para guardar el cuerpo de la pregunta

  i = 0 # Índice de la línea

  for i in range(len(q_lines)): # Itero sobre todas las líneas de la pregunta
    q_text = read_question(q_text,format_line(q_lines[i])) # Engordo el string
        
  quiz += """ <question type='{}'>
  <name>
   <text> {} </text>
  </name>
  <questiontext format='{}'>
   <text>
   <![CDATA[
     {}
   ]]>
   </text>
  </questiontext>
  <responseformat>editorfilepicker</responseformat>
  <responserequired>0</responserequired>
  <responsefieldlines>15</responsefieldlines>
  <attachments>-1</attachments>
  <attachmentsrequired>0</attachmentsrequired>
 </question> \n""".format(q_type,q_name,q_format,q_text)

  return quiz

def prepare_quiz(questions,q_type = 'essay',q_format = 'html',q_category = 'General'): # Función que prepara el cuestionario con todas las preguntas
  quiz = '' # Creo un string vacío para guardar el cuerpo del "quiz" (lista de preguntas)
  quiz = insert_header(quiz,q_category) # Inserto el header del cuestionario

  for k in range(len(questions)): # Inserto todas las preguntas
    quiz = insert_question(quiz,questions[k],q_type,q_format,q_category + '_' + str(k))
    
  quiz += "</quiz>" # Inserto la línea de cierre del cuestionario

  return quiz

def generate_xml_q(filename,q_dir,q_type = 'essay',q_format = 'html',q_category = 'General'): # Función que genera la pregunta
  #----------------- Preguntas ------------------------
  questions = read_tex_q(filename) # Leo las preguntas
  N = len(questions) # Número de preguntas
  quiz = prepare_quiz(questions,q_type = 'essay',q_format = 'html',q_category = q_category) # Preparo el cuestionario con todas las preguntas
  
  if not os.path.exists(q_dir): # Si no existe el directorio, lo creo
    os.mkdir(q_dir)

  # Genero el archivo con las preguntas
  os.chdir(curr_dir + '/' + q_dir) # Creo un contexto para guardar la pregunta y luego re
  with open(filename[:-3] + 'xml','w+') as q_file: # Creo un archivo, guardo todo y cierro al terminar
    q_file.write(quiz) # Copio todo el string s en el archivo
  os.chdir(curr_dir) # Vuelvo al directorio actual

  print('\n Voilà! Se generó un archivo .xml con un total de {} preguntas de tipo \"{}\" en la categoría \"{}\"'.format(len(questions),q_type,q_category))
#------------------------------------------------------------------------