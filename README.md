# mono-infinito-discord
Bot de Discord que trata de imitar la forma de hablar de los usuarios utilizando los contenidos de la práctica propuesta en la asignatura de Sistemas de Almacenamiento y Recuperación de Información en la UPV. El programa recopila mensajes de usuarios para crear modelos de lenguaje a partir de los cuales obtener mensajes originales. Cabe destacar que las colecciones de mensajes utilizados para generar los modelos de lenguaje están **separados por servidores**, por lo que el bot no tiene la capacidad de obtener un modelo utilizando los mensajes del mismo usuario en diferentes servidores.

## Instrucciones de instalación
1. Crear y registrar un bot en https://discord.com/developers/applications y obtener su token. (IMPORTANTE: los intents "Server Members Intent" y "Message Content Intent" deben estar activados).
2. Introducir dicha token en el archivo token.txt incluido en el repositorio. En este archivo solo debe estar presente la token sin ningún otro tipo de añadido.
3. Añadir el bot a los servidores de Discord donde se quiera utilizar. Para ello, se debe entrar en https://discord.com/api/oauth2/authorize?client_id=APPLICATION_ID&permissions=0&scope=bot%20applications.commands donde hay que sustituir "APPLICATION_ID" por la ID del bot creado. NOTA: el bot debe tener permiso para leer el historial de mensajes y ver los canales de texto en los que pueda recopilar mensajes, además de permisos de lectura y escritura de texto en los canales donde se quiera usar sus comandos.

## Ejecución
```
python botmi.py [-p PREFIX]
```
Donde se puede cambiar el prefijo de los comandos del bot especificándolo en PREFIX. El valor predeterminado es "!".

## Comandos
Hay dos comandos: construct y talk. Ambos deben ir precedidos por el prefijo establecido al ejecutar el bot (por defecto, "!construct" y "!talk").

### Construct
```
!construct [-j] [-l LIMIT]
```
Con este comando, un usuario puede solicitar al bot que construya un modelo de lenguaje usando sus mensajes. Esto supone que ningún usuario puede generar modelos de lenguaje utilizando mensajes de otros usuarios. El proceso suele tardar unos cuantos minutos puesto que recopilar mensajes tiene un coste temporal considerable. No obstante, el bot avisará cuando el proceso haya terminado.

El comando posee dos argumentos opcionales:
+ El primero es -j, que hace que el bot considere que todos los mensajes del usuario forman parte de la misma secuencia de texto. En consecuencia, los mensajes generados por el bot son más variados y largos, pero mucho menos coherentes.
+ El segundo es -l, donde LIMIT representa la cantidad máxima de mensajes del usuario que el bot puede analizar. No obstante, no representa la cantidad real de mensajes añadidos a la colección porque durante el proceso de recopilación se descartan mensajes que no contengan texto (imágenes, vídeos, etc). De todas formas, incrementar este valor supone incrementar la cantidad de mensajes utilizados por el análisis (a no ser que supere la cantidad de mensajes enviados por el usuario que el bot pueda leer). Cabe destacar, además, que cuanto mayor sea este valor, más tardará en construir el modelo. Su valor predeterminado es de 10000.

### Talk
```
!talk MODELNAME [-n N]
```
Una vez el bot haya terminado de construir un modelo con el comando construct, aportará el nombre del modelo al usuario que lo ha solicitado. Dicho nombre ha de insertarse en el lugar de MODELNAME.

El comando posee un único argumento opcional. N es un número entero del 2 al 5 (con valor predeterminado de 3) que es proporcional a la coherencia de los mensajes. No obstante, un valor de N demasiado elevado para un modelo de lenguaje que ha sido entrenado con muy pocos mensajes (por ejemplo, un usuario que solo haya enviado 1000 mensajes de texto en un servidor) puede suponer que las frases generadas sean demasiado similares o directamente idénticas a los mensajes originales del propio usuario. En definitiva, cuantos menos mensajes de texto haya enviado el usuario al que se quiere imitar, menor debe ser la N.

## Consejos
+ Recomiendo empezar generando modelos pequeños, como por ejemplo usando el LIMIT predeterminado. Para usar estos modelos pequeños, recomiendo usar una N con valor de 2.
+ Cuando ya se haya visto cómo se usa el bot, en caso de que un usuario tenga muchos mensajes de texto, es ideal generar un modelo con un LIMIT muy grande (como por ejemplo 1000000). El bot tarda mucho tiempo en generar estos modelos, pero los resultados al usar el comando !talk suelen ser mucho mejores de esta forma.
+ Es recomendable dedicar un tiempo a determinar a qué canales de texto tiene acceso el bot y a qué canales no. Canales dedicados a insertar comandos de otros bots o canales con mensajes privados que no debería leer cualquier persona que pueda utilizar el bot en un servidor no son recomendables.
