from flask import Flask, request, jsonify
import os
import subprocess
import shutil
import glob
import socket

app = Flask(__name__)

@app.route('/api/deploy', methods=['POST'])
def post_data():
    # Get the JSON data from the request
    data = request.get_json()
    f = open('C:/Users/Server/Documents/password.txt', 'r')
    password = f.readline()
    f.close()
    if password == data["password"]:
        deploy_fe = data["deploy_frontend"]
        deploy_be = data["deploy_backend"]

        if deploy_fe:
            deploy_frontend()
        if deploy_be:
            deploy_backend()

        # Return a JSON response
        return jsonify("ok"), 200
    return jsonify("Bad password"), 400

def get_local_ip():
    # Create a socket and connect to an external server (e.g., Google's public DNS)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip

    
def deploy_sql_server():
    os.chdir("C:/Users/Server/Desktop")
    os.system("rmdir /S /Q sql-server-docker")
    os.system("git clone https://github.com/2412rock/sql-server-docker")
    os.chdir("C:/Users/Server/Desktop/sql-server-docker")
    os.system("docker stop sql-server")
    os.system("docker rm sql-server")
    os.system("docker build -t sql-server .")
    subprocess.Popen(["docker", "run", "-d", "-p", "1433:1433", "--name", "sql-server"])


def deploy_frontend():
    os.chdir("C:/Users/Server/Desktop")
    os.system("rmdir /S /Q Dorel-angular")
    os.system("git clone https://github.com/2412rock/Dorel-angular")
    for file in os.listdir("C:/Users/Server/Desktop/certs"):
        shutil.copy("C:/Users/Server/Desktop/certs/"+file, "C:/Users/Server/Desktop/Dorel-angular")
    os.chdir("C:/Users/Server/Desktop/Dorel-angular")
    os.system("docker stop angular-app")
    os.system("docker rm angular-app")
    os.system("docker build -t dorel-angular .")
    subprocess.Popen(["docker", "run", "--name", "angular-app", "-p", "443:443", "dorel-angular"])

def deploy_backend():
    os.chdir("C:/Users/Server/Desktop")
    os.system("rmdir /S /Q Dorel-backend")
    os.system("git clone https://github.com/2412rock/Dorel-backend")
    os.chdir("C:/Users/Server/Desktop/Dorel-backend")
    os.system("docker stop dorel-backend")
    os.system("docker rm dorel-backend")
    os.system("docker build -t dorel-backend .")
    email_password_file = open('C:/Users/Server/Documents/email_password.txt', 'r')
    email_password = email_password_file.readline()
    email_password_file.close()
    subprocess.Popen(["docker", "run" , "-e", f'EMAIL_PASSWD="{email_password}"', f'HOST_IP="{get_local_ip()}"',"--name" ,"dorel-backend", "-p" ,"4200:4200" ,"dorel-backend"])

if __name__ == '__main__':
    #app.run(host="192.168.1.239", port="4300",debug=True)
    print(get_local_ip())
