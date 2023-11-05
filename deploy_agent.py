from flask import Flask, request, jsonify
import os
import subprocess
import shutil
import glob

app = Flask(__name__)

@app.route('/api/deploy', methods=['POST'])
def post_data():
    # Get the JSON data from the request
    data = request.get_json()
    f = open('C:/Users/Server/Documents/password.txt', 'r')
    password = f.readline()
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
    subprocess.Popen(["docker", "run" ,"--name" ,"dorel-backend", "-p" ,"4200:4200" ,"dorel-backend"])

if __name__ == '__main__':
    app.run(host="192.168.1.239", port="4300",debug=True)
