import socket
import pickle
import os
from _thread import start_new_thread
import random


shared_list = []
shared_file = {}

# shared_file['gjh'] = 11

def main():
    # Defining Socket 
    host = '127.0.0.1'
    port = 8080

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()

    print(f"[Server] Listening as {host}:{port}")

    # accept connection if there is any
    while True:
        client, address = s.accept() 

        start_new_thread(handle_req, (client, address))

        # if below code is executed, that means the sender is connected
        print(f"[Server] {address[0]}:{address[1]} has connected.")


def handle_req(client, address):

    while True:

        package = b''
        package = client.recv(4096)

        if package:

            received_data = b''
            
            while True:

                if package.find(b'<END>') != -1:

                    received_data += package[:package.find(b'<END>')]

                    break

                received_data += package
                package = client.recv(4096)

            full_package = pickle.loads(received_data)

            if full_package['Header'] == 'Any_file':

                print(f'[Server] Server successfully received the file from {address[0]}:{address[1]}!')

                shared_list.append(f'{address} has sent a file: {full_package['Body']['Filename']}')

                while True:
                    rnd_num = random.randint(0, 1000)
                    if rnd_num not in shared_file:
                        break
                    
                shared_file[rnd_num] = {
                    'Filename' : full_package['Body']['Filename'],
                    'Data' : full_package['Body']['Data']
                }

                data = '[Server] Server successfully received the file!'
                package = {
                    'Header':'Text',
                    'Body': {
                        'Data': data
                    }
                }

            elif full_package['Header'] == 'Text':

                print(f'[Server] Server successfully received the text from {address[0]}:{address[1]}!')

                data = full_package['Body']['Data']
                shared_list.append(f'{address}: {data}')

                package = {
                    'Header':'Shared_List',
                    'Body': {
                        'Data': shared_list
                    }
                }

            elif full_package['Header'] == 'Request_Shared_List':
                
                package = {
                    'Header':'Shared_List',
                    'Body': {
                        'Data': shared_list
                    }
                }

            elif full_package['Header'] == 'Request_Files':
                
                print(f'[Server] {address[0]}:{address[1]} request to download files.')

                file_list = []
                for file_id in shared_file.keys():
                    file_list.append((file_id ,shared_file[file_id]['Filename']))
                
                package = {
                    'Header':'Shared_Files',
                    'Body': {
                        'Data': file_list
                    }
                }
                # shared_file[rnd_num] = {f'{full_package['Body']['Filename']}' : full_package['Body']['Data']}

                print(f'[Server] Server sent {package['Body']['Data']} to {address[0]}:{address[1]}')

            elif full_package['Header'] == 'Files_Requested':
                
                print(f'[Server] {address[0]}:{address[1]} sent the requested files.')

                # package = b''
                # package = client.recv(4096)

                # if package:

                #     received_data = b''
                    
                #     while True:

                #         if package.find(b'<END>') != -1:

                #             received_data += package[:package.find(b'<END>')]

                #             break

                #         received_data += package
                #         package = client.recv(4096)

                #     full_package = pickle.loads(received_data)

                # print(full_package)

                client_file = []

                for file_id in full_package['Body']['Data']:
                    
                    file = shared_file[file_id]
                    
                    client_file.append(file)

                package = {
                    'Header':'Multiple_File',
                    'Body': {
                        'Data': client_file
                    }
                }

            client.sendall(pickle.dumps(package) + b'<END>')


if __name__ == '__main__':

    main()