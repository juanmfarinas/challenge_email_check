# challenge_email_check

## Descripción

Mini programita que muestra el siguiente menu:

[1] - Verifica Mails.

Verifica que haya mails nuevos en la casilla seteada y que estos tengan la palabra incidente en el body. En caso afirmativo, y de no existir en la db se almacena uid, sender, fecha y subject.

[2] - Cantidad de mails en db.

Indica cuantos mails hay en la db guardados.

[3] - Muestra mails en db.

Muetra la info de la tabla de incidentes en la base de datos.

[4] - Muestra mails en casilla.

Muestra todos los mails en el inbox de la casilla, demora un par de segundos.

[5] - Limpia la base de datos.

Borra todos los datos de la base de datos.

[6] - Limpia la casilla.

Borra todos los mails de la casilla de correo.

[7] - Salir.

## Ejecución.

Se sugiere correrlo desde consola:

Ejemplo MacOs
/Users/juanmafg/PycharmProjects/challenge_email_check/venv/bin/Python /Users/juanmafg/PycharmProjects/challenge_email_check/mail_check.py

Ejemplo Windows
C:\Users\u199241\PycharmProjects\challenge_email_check\venv\Scripts\python.exe C:\Users\u199241\PycharmProjects\challenge_email_check\mail_check.py 

## Docker

Se encuentra subido en:

https://hub.docker.com/r/juanmafg/challenge-email-check/tags

Ejecutarlo con parametro -ti para poder tener input desde el teclado.

docker run -ti juanmafg/challenge-email-check


