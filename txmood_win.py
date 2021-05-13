'''
Usage
-----
    $ txmood [options] [args]

Convert a single file:

    $ txmood <filename> [parent_category] [tex_dir] [xml_dir] [q_type] [q_format]
    
    where <filename> is a mandatory string containing the name of the .tex file to be converted (with extension)
    
Convert all files inside a folder:

    $ txmood -a [parent_category] [tex_dir] [xml_dir] [q_type] [q_format]

Optional arguments:
    [parent_category]: name of the parent category in the Question Bank. Default is 'top'. 
                       The child category is given by the name of the file (without extension).
    [tex_dir]: (optional) name of the folder containing the .tex file(s). Default is 'questions_tex'.
    [xml_dir]: (optional) name of the folder where the .xml file(s) will be saved. Default is 'questions_xml'.
    [q_type]: (optional) type of Moodle question. Default is 'essay'.
    [q_format]: (optional) text format. Default is 'html'.

Available options are:
    -h, --help       Show this help
    -a, --all        Convert all files inside a folder

Contact:
--------
fabiangiana@gmail.com

Open-source development website:
-----------------------------
https://github.com/washiloo/tex2xml_mood
'''

#---------------PACKAGE-----------------------------------

# Last modified: 12may21 (FEG)
#
# Este módulo contiene todas las funciones necesarias para convertir archivos .tex que contienen preguntas (con un formato específico) en archivos .xml compatibles con el Banco de Preguntas de la plataforma Moodle.
#
# Consultas: fabiangiana@gmail.com
#

import base64
import os

curr_dir = os.getcwd() # Directorio actual

#---------------- FUNCIONES -----------------------------
def read_tex_q(filename,tex_dir = 'questions_tex'): # Función que lee el archivo .tex y extrae las preguntas
  questions = [] # Creo una lista vacía para guardar las preguntas
    
  # Leo el archivo LaTeX
  with open(os.getcwd() + '/' + tex_dir + '/' + filename,'r',encoding = 'utf8') as file: # Abro el archivo y lo cierro al terminar
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

def embed_image(line,tex_dir): # Devuelve una línea de código html con una imagen embebida en base64
  idx_0 = line.find('{') # Busco el inicio del nombre de archivo
  idx_1 = line.find('}') # Busco el fin del nombre de archivo

  filename = line[idx_0 + 1:idx_1] # Nombre del archivo
  if('jpg' in filename): # Extensión (jpg o png)
    ext = 'jpeg'
  else:
    ext = 'png'
    
  with open(tex_dir + '/' + filename,"rb") as image_file: # Abro el archivo de imagen
    encoded_string = base64.b64encode(image_file.read()) # Codifico la imagen

  return '<img src="data:image/' + ext + ';base64,' + encoded_string.decode("utf-8") + '" width="50%">'

def format_line(line,tex_dir): # Convierte comandos de LaTeX en formato HTML (falta comentar mejor)
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
  elif('begin{center' in line): # Inicio de bloque centrado
    line = '<center>'
  elif('end{center' in line): # Fin de bloque centrado
    line = '</center>'
  elif('includegraphics' in line): # Imagen
    line = embed_image(line,tex_dir) # Embeber la imagen como base64
  else: # Línea común
    line = escape_chars(line)
    
  return line

def escape_chars(s): # Escapa los caracteres especiales de HTML
  replace_pairs = (('<','&lt;'),('>','&gt;'),('\\$','tempPESO'),('$','$$'),('tempPESO','\$')) # Caracteres conflictivos y su versión escapada
    
  for rp in replace_pairs: # Itero sobre todos los caracteres conflictivos
    s = s.replace(rp[0],rp[1]) 
  
  while('textit{' in s): # Busco texto en italics
    idx_0 = s.index('textit{') - 1 # Inicio del \textit{.}
    idx_1 = idx_0 + s[idx_0:].index('}') # Fin del \textit{.}
    
    s = s[:idx_0] + '<em>' + s[idx_0 + 8:idx_1] + '</em>' + s[idx_1 + 1:] # Convierto el comando \textit{.} a HTML
    
  while('textbf{' in s): # Busco texto en boldface
    idx_0 = s.index('textbf{') - 1 # Inicio del \textit{.}
    idx_1 = idx_0 + s[idx_0:].index('}') # Fin del \textit{.}
    
    s = s[:idx_0] + '<strong>' + s[idx_0 + 8:idx_1] + '</strong>' + s[idx_1 + 1:] # Convierto el comando \textbf{.} a HTML
    
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
    
def insert_question(quiz,q_lines,q_type,q_format,tex_dir,q_name = ''): # Agrega una pregunta al cuestionario
  q_text = '' # Creo un string vacío para guardar el cuerpo de la pregunta

  i = 0 # Índice de la línea

  for i in range(len(q_lines)): # Itero sobre todas las líneas de la pregunta
    q_text = read_question(q_text,format_line(q_lines[i],tex_dir)) # Engordo el string
        
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

def prepare_quiz(questions,tex_dir,q_type = 'essay',q_format = 'html',q_category = 'General'): # Función que prepara el cuestionario con todas las preguntas
  quiz = '' # Creo un string vacío para guardar el cuerpo del "quiz" (lista de preguntas)
  quiz = insert_header(quiz,q_category) # Inserto el header del cuestionario

  for k in range(len(questions)): # Inserto todas las preguntas
    quiz = insert_question(quiz,questions[k],q_type,q_format,tex_dir,q_category + '_' + str(k))
    
  quiz += "</quiz>" # Inserto la línea de cierre del cuestionario

  return quiz

def generate_xml_q(filename,params): # Función que genera la pregunta
  '''
  Parameters:
    filename: name of the file (with extension .tex included)
    params: dictionary with configuration parameters
    
  Keys in config_param:
    tex_dir: name of the folder containing the .tex file(s). Default is 'questions_tex'
    xml_dir: name of the folder where the .xml file(s) will be saved. Default is 'questions_xml'
    q_type: type of Moodle question. Default is 'essay'
    q_format: text format. Default is 'html'
    parent_category: name of the parent category in the Question Bank. Default is 'top'. 
                     The child category is given by the name of the file (without extension)
  '''
  #---------- Configuration parameters ----------------
  tex_dir = params['tex_dir']
  xml_dir = params['xml_dir']
  q_type = params['q_type']    
  q_format = params['q_format']
  par_cat = params['parent_category']
    
  #----------------- Questions ------------------------
  questions = read_tex_q(filename,tex_dir = tex_dir) # Read the questions
  N = len(questions) # Number of questions

  if(par_cat is None): # Si no se ingresa un nombre para la categoría progenitora, pongo por defecto 'top'
    q_category = filename[:-4] # Nombre de la categoría = nombre del archivo (sin la extensión .tex)
  else:
    q_category = par_cat + '/' + filename[:-4] # Nombre de la categoría = nombre del archivo (sin la extensión .tex)

  quiz = prepare_quiz(questions,tex_dir,q_type = q_type,q_format = q_format,q_category = q_category) # Preparo el cuestionario con todas las preguntas
  
  if not os.path.exists(xml_dir): # Si no existe el directorio, lo creo
    os.mkdir(xml_dir)

  # Genero el archivo con las preguntas
  os.chdir(curr_dir + '/' + xml_dir) # Creo un contexto para guardar la pregunta y luego regresar al directorio posta
  with open(filename[:-3] + 'xml','w+') as q_file: # Creo un archivo, guardo todo y cierro al terminar
    q_file.write(quiz) # Copio todo el string s en el archivo
  os.chdir(curr_dir) # Vuelvo al directorio actual

  print('\n Voilà! Se generó un archivo .xml con un total de {} preguntas de tipo \"{}\" en la categoría \"{}\"'.format(len(questions),q_type,q_category))

def generate_xml_q_folder(params): # Función que convierte todos los archivos de una misma carpeta
  '''
  Parameters:
    params: dictionary with configuration parameters
    
  Keys in config_param:
    parent_category: name of the parent category in the Question Bank. Default is 'top'. 
                     The child category is given by the name of the file (without extension)
    tex_dir: name of the folder containing the .tex file(s). Default is 'questions_tex'
    xml_dir: name of the folder where the .xml file(s) will be saved. Default is 'questions_xml'
    q_type: type of Moodle question. Default is 'essay'
    q_format: text format. Default is 'html'
  '''
  #---------- Configuration parameters ----------------
  tex_dir = params['tex_dir']

  #----------------- Conversions ------------------------
  for filename in os.listdir(tex_dir): # Busco todos los archivos en la carpeta de preguntas LaTeX
    if(filename.endswith(".tex")): # Selecciono los archivos .tex
      generate_xml_q(filename,params) # Convierto el archivo a XML de Moodle 
#------------------------------------------------------------------------

#------------------------------------------------------------------------
#------------------------------PROGRAMA-----------------------------
#------------------------------------------------------------------------

# Standard modules import
import sys

# MAIN function
def main():  # type: () -> None
    """
    COMPLETAR este help
    """
    args = [a for a in sys.argv[1:] if not a.startswith("-")] # Arguments
    opts = [o for o in sys.argv[1:] if o.startswith("-")] # Options
    
    # Show help message
    if(("-h" in opts) or ("--help" in opts)):
      print(__doc__)
      return
    
    # Whole folder or single file
    all_files = ("-a" in opts) or ("--all" in opts)

    # Handle common errors
    if((not all_files) and (args == [])): # If no arguments are given
      print('ERROR: argument "filename" is required for single conversion.')
      return
    elif(all_files): # Conversion of multiple files
      args = [0] + args # First argument is not used
      
    
    nargs = len(args) # Number of arguments
    
    # Configuration
    config_param = {} # Empty dictionary to store configuration parameters
    
    if(nargs > 1): # Manual or automatic category name
      config_param['parent_category'] = args[1] # Name of the category
    else:
      config_param['parent_category'] = None # Default name
    
    if(nargs > 2): # Manual or automatic tex folder name
      config_param['tex_dir'] = args[2] # Folder containing the .tex file(s)
    else:
      config_param['tex_dir'] = 'questions_tex' # Default name
    
    if(nargs > 3): # Manual or automatic xml folder name
      config_param['xml_dir'] = args[3] # Folder where the .xml file(s) will be saved
    else:
      config_param['xml_dir'] = 'questions_xml' # Default name
    
    if(nargs > 4): # Manual or automatic question type
      config_param['q_type'] = args[4] # Type of question
    else:
      config_param['q_type'] = 'essay' # Default type
    
    if(nargs > 5): # Manual or automatic text format
      config_param['q_format'] = args[5] # Text format
    else:
      config_param['q_format'] = 'html' # Default format
    
    # Convert the file(s)
    if(not all_files): # Single file conversion
      generate_xml_q(args[0],config_param) # Convert!     
    else: # Complete folder conversion
      generate_xml_q_folder(config_param) # Convert!    
    
# EXECUTE code
if(__name__ == "__main__"):
  main()
