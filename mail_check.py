import email
import imaplib
import os
import datetime
import time
from email.header import decode_header
from prettytable import PrettyTable
import mysql.connector

# Parametros Mail
# Name: Challenge ML JMFG 2024_07
GMAIL_IMAP = 'imap.gmail.com'
GMAIL_USER = 'challenge.ml.jmf.202407@gmail.com'
GMAIL_PASS = ''

# Parametros DB
DB_USER = 'sql10719407'
DB_PASS = ''
DB_HOST = 'sql10.freesqldatabase.com'
DB_NAME = 'sql10719407'

# Funciones para la DB
def connect_to_db():
    cnx = mysql.connector.connect(user=DB_USER,
                              password=DB_PASS,
                              host=DB_HOST,
                              database=DB_NAME)

    """
    if cnx and cnx.is_connected():
        print("conexion ok")
    else:
        print("conexion no ok")
    """
    return cnx

def crear_tabla():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS incidentes (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        mailUID INT, 
                        fechaRecibido TIMESTAMP,
                        mailFrom VARCHAR(255),
                        subject VARCHAR(255)
                        )''')
    connection.commit()
    cursor.close()
    connection.close()

def fecha_ultimo_mail ():
    connection = connect_to_db()
    cursor = connection.cursor(buffered=True)
    cursor.execute('''SELECT max(fechaRecibido) as fechaRecibido FROM incidentes''')
    connection.commit()
    cursor.close()
    connection.close()
    result = cursor.fetchall()
    return result[-1][-1]

def existe_mail (mailUID: str):
    connection = connect_to_db()
    cursor = connection.cursor(buffered=True)
    cursor.execute('''SELECT
        CASE WHEN EXISTS
        (
            SELECT * FROM incidentes where mailUID = %s
        )
        THEN 'TRUE'
        ELSE 'FALSE'
        END AS existeMail''', (mailUID,))
    connection.commit()
    cursor.close()
    connection.close()
    result = cursor.fetchall()
    return result[-1][-1]

def borra_tabla ():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('''DROP TABLE IF EXISTS incidentes''')
    connection.commit()
    cursor.close()
    connection.close()

def guardar_mail(mailUID, fechaRecibido, mailFrom, subject):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute('''INSERT IGNORE INTO incidentes (mailUID, fechaRecibido, mailFrom, subject) VALUES (%s, %s, %s, %s)''', (mailUID, fechaRecibido, mailFrom, subject))
    connection.commit()
    cursor.close()
    connection.close()

def cant_emails ():
    connection = connect_to_db()
    cursor = connection.cursor(buffered=True)
    cursor.execute('''SELECT count(mailUID) AS cant_email FROM incidentes''')
    connection.commit()
    cursor.close()
    connection.close()
    result = cursor.fetchall()
    return result[-1][-1]

def show_table ():
    connection = connect_to_db()
    cursor = connection.cursor(buffered=True)
    cursor.execute('''SELECT * FROM incidentes''')
    connection.commit()
    cursor.close()
    connection.close()
    result = cursor.fetchall()
    t = PrettyTable(['MailUID', 'Mail From', 'Fecha', 'Subject'])
    for row in result:
        t.add_row([row[1],row[3],row[2],row[4]])
    print(t)


# Funciones para correo
def borra_emails ():
    mail = imaplib.IMAP4_SSL(GMAIL_IMAP)
    mail.login(GMAIL_USER, GMAIL_PASS)

    # Print response
    #print("Server Response: ")
    #print(mail.welcome)

    # selecciono inbox
    mail.select("inbox")

    typ, data = mail.search(None, 'ALL')
    for num in data[0].split():
        mail.store(num, '+FLAGS', '\\Deleted')

    mail.expunge()
    mail.close()
    mail.logout()

def show_mails_casilla ():
    mail = imaplib.IMAP4_SSL(GMAIL_IMAP)
    mail.login(GMAIL_USER, GMAIL_PASS)

    mail.select("inbox")
    busqueda = "*"
    result, data = mail.uid('Search', "All")
    email_ids = data[0].split()

    t = PrettyTable(['MailUID', 'Mail From', 'Fecha', 'Subject'])

    for email_id in email_ids:
        #mailUID
        #print(email_id)

        result, email_data = mail.uid('fetch', email_id, '(RFC822)')

        raw_email = email_data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        # fecha de recepcion
        date_tuple = email.utils.parsedate_tz(email_message['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            local_message_date = "%s" % (str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
        #print("Fecha de recepcion: " + str(local_date))

        #mailFrom
        email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
        #print("From: " + email_from)

        #mailTo
        email_to = str(email.header.make_header(email.header.decode_header(email_message['To'])))
        #print("To: " + email_to)

        #Subject
        subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))
        #print("Subject: " + subject)

        t.add_row([email_id,email_from,local_date,subject])

    mail.close()
    mail.logout()
    print(t)

def search_incident_emails():
    mail = imaplib.IMAP4_SSL(GMAIL_IMAP)
    mail.login(GMAIL_USER, GMAIL_PASS)

    # Print response
    # print("Server Response:")
    # print(mail.welcome)

    # selecciono inbox
    mail.select("inbox")

    fecha_u = fecha_ultimo_mail()

    if fecha_u:
        fecha_u = fecha_ultimo_mail().strftime("%d-%b-%Y")
        busqueda = "BODY incidente SINCE " + fecha_u
    else:
        busqueda = "BODY incidente"

    # busco los mails que tengan en el body Incident y sean mas nuevos que la fecha max de la db
    result, data = mail.uid('Search', None, busqueda)
    email_ids = data[0].split()

    new_mails = 0

    for email_id in email_ids:
        #mailUID
        #print(email_id)

        result, email_data = mail.uid('fetch', email_id, '(RFC822)')

        raw_email = email_data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)

        # fecha de recepcion
        date_tuple = email.utils.parsedate_tz(email_message['Date'])
        if date_tuple:
            local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            local_message_date = "%s" % (str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
        #print("Fecha de recepcion: " + str(local_date))

        #mailFrom
        email_from = str(email.header.make_header(email.header.decode_header(email_message['From'])))
        #print("From: " + email_from)

        #mailTo
        email_to = str(email.header.make_header(email.header.decode_header(email_message['To'])))
        #print("To: " + email_to)

        #Subject
        subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))
        #print("Subject: " + subject)


        #verifico que el mail no esta en la db por uid, si no esta lo guardo
        existe_mail_en_db = existe_mail(email_id)

        if existe_mail_en_db == "FALSE":
            new_mails = 1
            guardar_mail(email_id,local_date,email_from,subject)
            print("Nuevo mail de: ", email_from, " fecha: ", local_date, " subject: ", subject)

    if new_mails == 1:
        print("\n")
        print("Finalizo la verificacion y carga en la DB.")
        print("\n")
    else:
        print("\n")
        print("No hay Mails Nuevos.")
        print("\n")

    mail.close()
    mail.logout()


# Menu

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def set_passwords():
    global GMAIL_PASS, DB_PASS
    GMAIL_PASS = input("Ingrese Password Mail:  ")
    GMAIL_PASS = 'auhd zyci jmak vyrw'
    DB_PASS= input("Ingrese Password DB:  ")
    DB_PASS = 'Kr95An1Jci'

def menu():
    print('''
           Mail Check Menu
           [1] - Verifica Mails
           [2] - Cantidad de mails en db
           [3] - Muestra mails en db
           [4] - Muestra mails en casilla
           [5] - Limpia la base de datos
           [6] - Limpia la casilla
           [7] - Salir
           \n
           ''')


    action = input("Ingrese Opcion:  ")

    if action.isnumeric():
        action = int(action)
    else:
        action = 0

    if action == 1:
        print("\n")
        print("Se esta verificando si hay mails nuevos en la casilla.")
        print("En caso positivo se imprimir'a en pantalla la informaci'on del mail.")
        print("Casilla: ", GMAIL_USER, " Mails que incluyen en el body la palabra incidente")
        print("\n")
        print("Chequeando...")
        print("\n")
        search_incident_emails()
        input("Presione enter para continuar.")
        cls()
    elif action == 2:
        q_mails = cant_emails()
        print("Cantidad de mails en la DB: ", q_mails)
        print("\n")
        input("Presione enter para continuar.")
        cls()
    elif action == 3:
        print("Informacion en la DB")
        print("\n")
        show_table()
        print("\n")
        input("Presione enter para continuar.")
        cls()
    elif action == 4:
        print("Informacion en la casilla")
        print("\n")
        show_mails_casilla()
        print("\n")
        input("Presione enter para continuar.")
        cls()
    elif action == 5:
        borra_tabla()
        crear_tabla()
        print("Tabla en DB limpia")
        print("\n")
        input("Presione enter para continuar.")
        cls()
    elif action == 6:
        borra_emails()
        print("Casilla de mail limpia")
        print("\n")
        input("Presione enter para continuar.")
        cls()
    elif action == 7:
        print("El programa termino.")
        print("\n")
    else:
        print("Opcion invalida.")
        time.sleep(1)
        cls()
    return action


if __name__ == "__main__":
    cls()
    set_passwords()
    cls()
    action = menu()
    while action != 7:
        action = menu()
