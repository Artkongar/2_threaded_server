import socket
import threading
import random
import json


def open_f(file_name):
	try:
		with open(file_name, 'r') as f:
			data = json.load(f)
	except:
		with open(file_name, 'w') as f:
			json.dump({} ,f)
		with open(file_name, 'r') as f:
			data = json.load(f)
	return data
	
	
def record_f(file_name, data):
	try:
		with open(file_name, 'r') as f:
			data_old = json.load(f)
		data_old.update(data)
		with open(file_name, 'w') as f:
			json.dump(data_old ,f)
	except:
		with open(file_name, 'w') as f:
			json.dump(data ,f)


def open_t(file_name):
	file = open(file_name, 'r')
	return file
	file.close()


def record_t(file_name, line):   #ЗАписывает в txt файл
	file = open(file_name, 'a')
	file.write(line + ' ;\n')
	file.close()


def reader(conn, addr, lst, login):
	right = 1
	while right:
		msg = conn.recv(1024).decode()
		if msg != 'exit':
			record_t('hist.txt', login + ', ' + str(addr[1])+") "+msg)
			for i in lst:
				if i != conn:
					i.send((str(addr[1])+', '+login+') '+ msg).encode('utf-8'))
		else:
			print('Вышел из беседы: '+ login+ ', '+ str(addr[1])+', ' + str(addr[0]))
			lst.remove(conn)
			if len(lst) != 0:
				print('Количество пользователей: '+ str(len(lst)))
			else:
				print('Порт пуст')
			break
	conn.close()


def main(lst,sock, port):
	conn, addr = sock.accept()
	
	right = 1
	try:
		data = open_t('book.txt')
	except:
		data = record_t('book.txt','')
		data = open_t('book.txt')
	nal = 'NO'
	for i in data:
		if i != ' ;\n':
			if i.split(', ')[2] == addr[0]:
				nal = 'YES'
				login = i.split(', ')[0]
	conn.send(str(nal).encode('utf-8'))
	if nal == 'YES':
		stata = open_f('stata.json')
		if stata[login] == conn.recv(1024).decode():
			conn.send('Пароль верен'.encode('utf-8'))
			record_t('book.txt', login+', '+str(port)+', '+str(addr[0])+ ', '+ str(addr[1]))
		else:
			conn.send('Пароль не верен'.encode('utf-8'))
			right = 0
	else:
		login = conn.recv(1024).decode()
		password = conn.recv(1024).decode()
		record_f('stata.json',{login:password})
		record_t('book.txt', login+', '+str(port)+', '+str(addr[0])+ ', '+ str(addr[1]))
	
	if right == 1:
		threading.Thread(target  = reader, args = (conn, addr, lst,login), daemon=True).start()
		lst.append(conn)
		print('Присоединился к беседе: '+ login+ ', '+ str(addr[1])+', ' + str(addr[0]))
	print('Количество пользователей: '+ str(len(lst)))
	main(lst, sock, port)

def start(sock, l):
	global lst
	port = 8080
	try:
		sock.bind(('', port))
	except:
		port = random.randint(8080,8300)
		sock.bind(('', port))
	print("Свободный порт:", port)
	sock.listen(1)
	lst = []
	main(lst,sock, port)
	
sock = socket.socket()
s1 = threading.Thread(target = start, args = (sock,1), daemon = True)
s1.start()

def menu(): 
	choice = input('(1 - exit\n2 - очистить файл)\n')
	if choice == '1':
		if len(lst) == 0:
			del_ = input('Глаза у меня добрые, но рубашка смирительная... (д/н?) ')
			if del_ == 'Д' or del_ == 'д' or del_ == '1': 
				sock.close()
			else:
				menu()
		else:
			print('Порт не пуст')
			menu()
	elif choice == '2':
		if len(lst) == 0:
			if input('Доверяй, но ... ') == 'проверяй':
				del_ = input("Вы уверенны, что хотите удалить все данные? (д/н?) ")
				if del_ == 'Д' or del_ == 'д' or del_ == '1': 
					with open('stata.json', 'w') as f:
						json.dump({}, f)
					book = open('book.txt', 'w')
					book.close()
					menu()
				else:
					print('Отмена')
					menu()
			else:
				print('Отмена')
				menu()
		else:
			print('Порт не пуст')
			menu()
	else:
		print('Выберите что -то')
		menu()
		
menu()
