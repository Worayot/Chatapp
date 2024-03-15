import tkinter as tk
from tkinter import filedialog
import socket
import os
import pickle
from _thread import start_new_thread
import time

host = "0.tcp.ap.ngrok.io" # change to 127.0.0.1
port = 14751              # change to any

s = socket.socket()
s.connect((host, port))

print(f"[Client] Connecting to {host}:{port}")
print("[Client] Connected.")

def send_file():

    file_path = filedialog.askopenfilename()
    file_name = os.path.basename(file_path)

    with open(file_path, 'rb') as f:

        data = f.read()

    package = {
        'Header':'Any_file',
        'Body': {
            'Filename': file_name,
            'Data': data
        }
    }

    total_package = pickle.dumps(package) + b'<END>'

    s.sendall(total_package)

    print(f'Sent package')

    received_package = s.recv(4096)

    if received_package:

        received_data = b''
            
        while True:

            if received_package.find(b'<END>') != -1:

                received_data += received_package[:received_package.find(b'<END>')]

                break

            received_data += received_package
            received_package = s.recv(4096)

        full_package = pickle.loads(received_data)

        if full_package['Header'] == 'Text':
            
            print(full_package['Body']['Data'])


def get_text_input(event=None):

    msg = my_msg.get() 
    my_msg.set("")
    if msg != '':
        send_text(msg)
    

def send_text(msg):

    package = {
        'Header':'Text',
        'Body': {
            'Data': msg
        }
    }

    s.sendall(pickle.dumps(package) + b'<END>')

    received_package = b''
    received_package = s.recv(4096)

    if received_package:

        received_data = b''

        while True:

            if received_package.find(b'<END>') != -1:

                received_data += received_package[:received_package.find(b'<END>')]

                break

            received_data += received_package
            received_package = s.recv(4096)

        full_package = pickle.loads(received_data)

        if full_package['Header'] == 'Text':

            msg_list.insert(tk.END, full_package['Body']['Data'])

        elif full_package['Header'] == 'Shared_List':
            
            shared_list = full_package['Body']['Data']

            msg_list.delete('0', 'end')

            for msgs in shared_list:

                msg_list.insert(tk.END, msgs)


def req_download():

    package = {
        'Header':'Request_Files',
        'Body': {
            'Data': 'msg'
        }
    }

    s.sendall(pickle.dumps(package) + b'<END>')

    received_package = b''
    received_package = s.recv(4096)

    if received_package:

        received_data = b''

        while True:

            if received_package.find(b'<END>') != -1:

                received_data += received_package[:received_package.find(b'<END>')]

                break

            received_data += received_package
            received_package = s.recv(4096)

        full_package = pickle.loads(received_data)

        file_list = []

        if full_package['Header'] == 'Shared_Files':
            
            file_list = full_package['Body']['Data']

            print(f'Received File List From Server: {file_list}')

        top = tk.Toplevel(master=window) 
        top.title('Downloadable files')
        top.geometry('350x150')

        checkboxes_vars = []
        row = 1

        for f in file_list:

            var = tk.BooleanVar()
            checkboxes_vars.append(var)
            tk.Checkbutton(top, text=f"{f[1]}", variable=var, onvalue=True, offvalue=False).grid(row=row, column=1)

            row+=5

        button = tk.Button(top, text="Download files", command=lambda: send_req_files(file_list, checkboxes_vars, top))
        button.place(x=250, y=0)


def send_req_files(file_list, checkboxes_vars, top):

    req_list = []
    for f in file_list:

        if [v.get() for v in checkboxes_vars][file_list.index(f)]:

            req_list.append(f[0])

    package = {
        'Header':'Files_Requested',
        'Body': {
            'Data': req_list
        }
    }

    s.sendall(pickle.dumps(package) + b'<END>')

    top.destroy()

    received_package = b''
    received_package = s.recv(4096)

    if received_package:

        received_data = b''

        while True:

            if received_package.find(b'<END>') != -1:

                received_data += received_package[:received_package.find(b'<END>')]

                break

            received_data += received_package
            received_package = s.recv(4096)

        full_package = pickle.loads(received_data)

        if full_package['Header'] == 'Multiple_File':

            client_file = full_package['Body']['Data']

            print('Rendering received files')
            for fi in client_file:
                
                with open('Downloads/'+fi['Filename'], 'wb') as f:

                    f.write(fi['Data'])


def update_chat():

    while True:

        package = {
            'Header':'Request_Shared_List',
            'Body': {
                'Data': ''
            }
        }

        s.sendall(pickle.dumps(package) + b'<END>')

        received_package = b''
        received_package = s.recv(4096)

        if received_package:

            received_data = b''

            while True:

                if received_package.find(b'<END>') != -1:

                    received_data += received_package[:received_package.find(b'<END>')]

                    break

                received_data += received_package
                received_package = s.recv(4096)

            full_package = pickle.loads(received_data)

            if full_package['Header'] == 'Shared_List':
                
                shared_list = full_package['Body']['Data']
                msg_list.delete('0', 'end')

                for msgs in shared_list:

                    msg_list.insert(tk.END, msgs)

        time.sleep(.5)


# Create the main window
window = tk.Tk()
window.title("Chat Room")

# Size of the window
window.geometry("600x700") 

# Stop execution when exit
window.protocol('WM_DELETE_WINDOW', exit)

messages_frame = tk.Frame(window)
my_msg = tk.StringVar()  
my_msg.set("")

scrollbar = tk.Scrollbar(messages_frame)  
msg_list = tk.Listbox(messages_frame, height=15, width=100, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
msg_list.pack(side=tk.LEFT, fill=tk.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tk.Entry(window, textvariable=my_msg)
entry_field.bind("<Return>", get_text_input)
entry_field.pack()

send_button = tk.Button(window, text="Send", command=get_text_input)
send_button.pack()

# Create a button
button = tk.Button(window, text="Send file", command=send_file)
button.pack()

button = tk.Button(window, text="Download file", command=req_download)
button.pack()

# Run the main event loop
start_new_thread(update_chat, ())

window.mainloop()




# tkinter.mainloop()