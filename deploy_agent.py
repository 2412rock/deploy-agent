from flask import Flask, request, jsonify
import os
import subprocess
import shutil
import glob
import socket
import time

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
        should_deploy_redis = data["deploy_redis"]
        should_deploy_sql = data["deploy_sql"]
        should_deploy_minio = data["deploy_minio"]

        if should_deploy_redis:
            deploy_redis_server()
        if should_deploy_sql:
            deploy_sql_server()
        if deploy_fe:
            deploy_frontend()
        if deploy_be:
            deploy_backend()
        if should_deploy_minio:
            deploy_minio_server()

        # Return a JSON response
        return jsonify("ok"), 200
    return jsonify("Bad password"), 400

def get_redis_password():
    file = open('C:/Users/Server/Documents/redis_password.txt', 'r')
    redis_password = file.readline()
    file.close()
    return redis_password

def deploy_minio_server():
    password = readLineFromFile("C:/Users/Server/Documents/minio_password.txt")

    os.system("docker stop minio-server")
    os.system("docker rm minio-server")
    os.system("docker pull minio/minio")
    subprocess.Popen(["docker", "run", "--name", "minio-server","-p", "9000:9000", "-e", "MINIO_ROOT_USER=minioadmin", "-e",
                       f"MINIO_ROOT_PASSWORD={password}",
                         "minio/minio", "server",
                           "/data"
                           ])

def deploy_redis_server():
    os.chdir("C:/Users/Server/Desktop")
    os.system("rmdir /S /Q redis-docker")
    os.system("git clone https://github.com/2412rock/redis-docker")
    os.chdir("C:/Users/Server/Desktop/redis-docker")
    os.system("docker stop redis-server")
    os.system("docker rm redis-server")
    os.system("docker build -t redis .")
    
    subprocess.Popen(["docker", "run", "-d", "-p", "6379:6379", "--name", "redis-server", "-e", f"REDIS_PASSWORD={get_redis_password()}", "redis"])

def getSqlPassword():
    f = open('C:/Users/Server/Documents/sql_password.txt', 'r')
    password = f.readline()
    f.close()
    return password

def deploy_sql_server():
    os.chdir("C:/Users/Server/Desktop")
    os.system("rmdir /S /Q sql-server-docker")
    os.system("git clone https://github.com/2412rock/sql-server-docker")
    os.chdir("C:/Users/Server/Desktop/sql-server-docker")
    os.system("docker stop sql-server")
    os.system("docker rm sql-server")
    os.system("docker build -t sql-server .")
    #docker run, -e, SA_PASSWORD=MyP@ssword1!,-d -p 1433:1433 --name sql-server sql-server
    subprocess.Popen(["docker", "run", "-e", f'SA_PASSWORD={getSqlPassword()}',"-d", "-p", "1433:1433", "--name", "sql-server", "sql-server"])
    print('Waiting for server to start')
    time.sleep(10)
    os.system("docker cp init.sql sql-server:/usr/src")
    os.system(f"docker exec -it sql-server /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P {getSqlPassword()} -d master -i /usr/src/init.sql")


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
    subprocess.Popen(["docker", "run", "--name", "angular-app", "--network=host", "-p", "443:443", "dorel-angular"])

def readLineFromFile(file):
    f = open(file)
    result = f.readline()
    f.close()
    return result

def deploy_backend():
    os.chdir("C:/Users/Server/Desktop")
    os.system("rmdir /S /Q Dorel-backend")
    os.system("git clone https://github.com/2412rock/Dorel-backend")
    shutil.copy("C:/Users/Server/Desktop/certs/backendcertificate.pfx", "C:/Users/Server/Desktop/Dorel-backend")
    os.chdir("C:/Users/Server/Desktop/Dorel-backend")
    os.system("docker stop dorel-backend")
    os.system("docker rm dorel-backend")
    os.system("docker build -t dorel-backend .")
    email_password_file = open('C:/Users/Server/Documents/email_password.txt', 'r')
    email_password = email_password_file.readline()
    email_password_file.close()
    pfx_pass_file = open('C:/Users/Server/Documents/pfx_pass.txt', 'r')
    pfx_pass = pfx_pass_file.readline()
    pfx_pass_file.close()
    jwt_secret = readLineFromFile("C:/Users/Server/Documents/JWT_SECRET.txt")
    minio_password = readLineFromFile("C:/Users/Server/Documents/minio_password.txt")
    subprocess.Popen(["docker", "run" , "-e", f'EMAIL_PASSWD={email_password}', "-e", f'SA_PASSWORD={getSqlPassword()}',
                       "-e", f'REDIS_PASSWORD={get_redis_password()}', "-e", f'PFX_PASS={pfx_pass}',
                       "-e", f"JWT_SECRET={jwt_secret}",
                       "-e", f"MINIO_PASS={minio_password}",
                         "--name" ,"dorel-backend", "-p" ,"4200:4200" ,"dorel-backend"])

if __name__ == '__main__':
    app.run(host="172.26.17.97", port="4300",debug=True)
