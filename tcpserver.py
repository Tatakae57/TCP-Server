import tkinter as tk
from tkinter import simpledialog, messagebox
import socket
from threading import Thread
from subprocess import run

#Ventana
ventana = tk.Tk()
ventana.title("TCP Chat")

#Posiciones
frame = tk.Frame(ventana)
frame.pack()
frame.grid_rowconfigure(0, weight = 1)
frame.grid_rowconfigure(1, weight = 1)
frame.grid_columnconfigure(0, weight = 1)
frame.grid_columnconfigure(1, weight = 1)
frame.grid_columnconfigure(2, weight = 1)

#Medidas
ventana.geometry("640x480")
ventana.resizable(False, False)

###			Socket
conexion = socket.socket()
conectados = 0
conexiones = []
salir, servidor = False, False
name = run(["whoami"], capture_output = True, text = True).stdout
name = name.rstrip()

###			Funciones
##		Interfaz
def dissapear_init():
	global server_button, connect_button
	server_button.grid_forget()
	connect_button.grid_forget()

def show_interface():
	global clients_list, messages_box, message_box, scroll_messages, disconnect_button, send_button
	clients_list.grid(row = 0, column = 0)
	disconnect_button.grid(row = 1, column = 0, sticky = "nsew")
	messages_box.grid(row = 0, column = 1, sticky = "nsew")
	scroll_messages.grid(row = 0, column = 2, sticky = "nsew")
	message_box.grid(row = 1, column = 1, sticky = "nsew")
	send_button.grid(row = 1, column = 2, sticky = "nsew")

def add_client(name):
	global clients_list
	clients_list.insert(tk.END, "+ " + str(name))

def add_message(message):
	global messages_box
	messages_box.config(state = tk.NORMAL)
	messages_box.insert("end", message + "\n")
	messages_box.config(state = tk.DISABLED)

def send_message(message = None):
	if (server == False):
		if (message == None):
			message = str("S3RV3R_MSG=%" + name + ":" + message_box.get("1.0", "end")).encode()
			conexion.send(message)
			message_box.delete("1.0", tk.END)
		else:
			conexion.send(message)
	else:
		if (message == None):
			message = str("S3RV3R_MSG=%" + name + ":" + message_box.get("1.0", "end")).encode()
			for i in conexiones:
				i.send(message)
			add_message(name + ":" + message_box.get("1.0", "end")[:-1])
			message_box.delete("1.0", tk.END)
		else:
			for i in conexiones:
				i.send(message)
			add_message(message)

##		Conexión
#	Esperar mensajes
def wait_messages(c):
	while not salir:
		message = c.recv(1024).decode()
		if (message != None):
			if "S3RV3R" in message:
				separar = message.split('%')
				separar[1] = separar[1].rstrip()
				if "NAME=%" in message:
					add_client(separar[1])
					add_message("Se conectó: " + str(separar[1]))
				elif "MSG=%" in message:
					add_message(separar[1])
			c.send(message.encode())

#	Esperar mensajes del servidor
def wait_server_messages():
	while not salir:
		message = conexion.recv(1024).decode()
		if (message != None):
			if "S3RV3R" in message:
				separar = message.split('%')
				separar[1] = separar[1].rstrip()
				if "NAME=%" in message:
					add_client(separar[1])
					add_message("Se conectó: " + str(separar[1]))
				elif "MSG=%" in message:
					add_message(separar[1])

#	Esperar clientes
def wait_clients():
	global conexion
	while not salir:
		c, a = conexion.accept()
		conexiones.append(c)
		Thread(target = wait_messages, args = (c, )).start()

#	Crear servidor
def create_server():
	global messages_box, server
	#Recibir info del servidor
	ip = simpledialog.askstring("Get IP", "IP (without port): ")
	port = simpledialog.askstring("Get port", "Port of server: ")
	listen = simpledialog.askstring("Clients", "Number of clients: ")
	
	#Intentar crear
	try:
		conexion.bind((ip, int(port)))
		conexion.listen(int(listen))
		dissapear_init()
		show_interface()
		add_client(name)
		add_message("Server created.")
		server = True
		Thread(target = wait_clients).start()
		messagebox.showinfo("Server created", "Server created succesfully!")
	except socket.error as e:
		messagebox.showinfo("Creation failed", "Cant create the server.")
	
#	Conectar a servidor
def connect_server():
	global server
	#Recibir info del cliente
	ip = simpledialog.askstring("Get IP", "IP (without port): ")
	port = simpledialog.askstring("Get port", "Port of server: ")
	
	#Intentar conectar
	try:
		conexion.connect((ip, int(port)))
		dissapear_init()
		show_interface()
		message = str("S3RV3R_NAME=%" + name).encode()
		server = False
		send_message(message)
		Thread(target = wait_server_messages).start()
		messagebox.showinfo("Connected", "Connected to server.")
	except:
		messagebox.showinfo("Connection failed", "Cant connect to server.")

#Botones de inicio
server_button = tk.Button(frame, text = "Create server", command = create_server)
server_button.grid(row = 1, column = 0, sticky = "nsew")
connect_button = tk.Button(frame, text = "Connect to server", command = connect_server)
connect_button.grid(row = 2, column = 0, sticky = "nsew")

#		Interfaz de mensajes
#	Clientes
clients_list = tk.Listbox(frame, width = 15, height = 35)

#	Mensajes recibidos
#Texto
messages_box = tk.Text(frame, width = 70, height = 10, state = tk.DISABLED)
#Scroll
scroll_messages = tk.Scrollbar(frame, command = messages_box.yview)
messages_box.config(yscrollcommand = scroll_messages.set)

#	Enviar mensaje
message_box = tk.Text(frame, width = 60, height = 10)

#Botones
disconnect_button = tk.Button(frame, text = "Disconnect")
send_button = tk.Button(frame, text = "Send", width = 3, command = send_message)

#Bucle
ventana.mainloop()
