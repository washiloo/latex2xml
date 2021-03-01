# latex2xml

El objetivo de este _software_ es convertir un archivo de LaTeX que contiene preguntas de una misma categoría en un archivo Moodle-XML, para poder importar todas las preguntas de forma eficiente al Banco de Preguntas de Moodle. Es compatible con cualquier plataforma basada en Moodle, como por ejemplo PEDCO.  
<<<<<<< HEAD
Los archivos de salida pueden ser editados para agregar opciones adicionales. Por defecto, este software genera preguntas de tipo "ensayo" (essay) con un cuadro de texto (opcional) de 15 líneas y permite adjuntar archivos de imagen y documentos tipo "word", "excel", etc. Los nombres de las preguntas se colocan automáticamente, con el formato *category_x*, donde _category_ es el nombre de la categoría y _x_ es la posición de la pregunta en el documento (empieza en 0).
=======
Los archivos de salida pueden ser editados para agregar opciones adicionales. Por ahora, este _software_ genera preguntas de tipo "ensayo" (_essay_) con un cuadro de texto (opcional) de 15 líneas y permite adjuntar archivos de imagen y documentos tipo "word", "excel", etc.  
>>>>>>> f656ba80627d2c8d98679cdddfadfd2d4e57df85

## ¿Cómo se usa?
(Cualquier duda, escribir a fabiangiana@gmail.com)

Abrir el _notebook_ de Jupyter llamado _LaTeX_2_xml.ipynb_ y correr todas las celdas de código, modificando únicamente el contenido de la primera.

### Formato del archivo de entrada

El archivo de entrada tiene que ser un documento de LaTeX con extensión _.tex_ que compile bien. Todavía no se soportan imágenes. La estructura del documento debe ser similar a la siguiente (hay 3 preguntas):

---------------------------------------------
    ...

    \begin{document}  
    \begin{enumerate}

    \item
    %q
    ...
    ...

    \item
    %q
    ...
    ...

    \item
    %q
    ...
    ...
    %q
    \end{enumerate}  
    \end{document}

---------------------------------------------

La parte previa a _\begin{document}_ es el preámbulo, y es irrelevante.  El bloque _enumerate_ engloba todas las preguntas. Cada pregunta inicia con un _\item_ seguido inmediatamente por un comentario _%q_ en la siguiente línea. Además, debe haber un comentario _%q_ al final de la última pregunta (justo antes del _\end{enumerate}_). Si se respeta este formato, aunque el archivo de salida sea único, Moodle identificará todas las preguntas de forma individual.  

### Bloques permitidos

Hasta el momento, sólo se permite el uso de bloques de tipo _enumerate_ (lista numerada), _itemize_ (lista con viñetas) y _equation_ (ecuación). Estas funcionalidades deben ser utilizadas en su mínima expresión, sin opciones especiales de formato.  

Todos estos bloques tienen que estar escritos de manera prolija, de la forma siguiente (el ejemplo es un bloque _enumerate_):

-----------------------------------------------

    \begin{enumerate}
    \item ...
    ...
    
    \end{enumerate}
-----------------------------------------------

Es **muy importante** que los comandos _\begin\{X\}_ y _\end{X}_ estén bien escritos, sin espacios en blanco entre los caracteres. Pueden anidarse bloques, por ejemplo _enumerate_ dentro de _enumerate_, _itemize_ dentro de _enumerate_, etc.

# Mejoras propuestas

1. Permitir inserción de imágenes. Usar _base64_ para embeberlas en el archivo _xml_.
