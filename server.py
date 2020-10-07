from flask import Flask,jsonify, request
import os
import shutil
import pathlib


app = Flask(__name__)

#==============================================heartbeat<3=========================

@app.route('/heartbeat' , methods=['GET', 'POST'])
def heartbeat():
    return "204"

#==============================================reading file=========================
@app.route('/GET/<string:pathToFile>', methods=['GET'])
def GetFile(pathToFile):
    if os.path.exists(pathToFile):
        f = open(pathToFile, "r")
        text=f.read()
        f.close()
        return text
    else:
        return "404"
#       return jsonify({"text : ":pathToFile})

    
#==============================================create file=========================

def Create_File0(pathToFile,fileContent):   #this is an auxiliary function to create a simple file 

    folder=pathToFile[0:pathToFile.rfind('\\')]
    f = open(pathToFile, "w")
    f.write(fileContent)
    f.close()
    memory = shutil.disk_usage(folder)  
    return "200  \nthe amount of free storage on the storage server in bytes is: "+str(memory[2])

    
@app.route('/POST/<string:pathToFile>', methods=['GET', 'POST'])
def Create_File1():                         
    data = request.get_json()
    fileContent=data['files']
    
    folder=pathToFile[0:pathToFile.rfind('\\')]    #to keep the path without the name of the file
    if os.path.exists(pathToFile):
        return "400"
    else:  
        if os.path.exists(folder):
            Create_File0(pathToFile,fileContent)
        else:
            #print("no existing folder")
            os.makedirs(folder)
            Create_File0(pathToFile,fileContent)
          
        
#==============================================Update file=========================

def Update_File0(pathToFile,fileContent):       #this is an auxiliary function to update a simple file with keeping the old content
    folder=pathToFile[0:pathToFile.rfind('\\')]
    f = open(pathToFile, "a+")
    f.write(fileContent)
    f.close()
    memory = shutil.disk_usage(folder)  
    return "200  \nthe amount of free storage on the storage server in bytes is: "+str(memory[2])

@app.route('/PUT/<string:pathToFile>', methods=['GET', 'POST'])
def Update_File1():                             #this is the main function to update 
    data = request.get_json()
    fileContent=data['files']
    
    folder=pathToFile[0:pathToFile.rfind('\\')]
    if os.path.exists(pathToFile):
        Update_File0(pathToFile,fileContent)
    else:  
        if os.path.exists(folder):
            Create_File0(pathToFile,fileContent)
        else:
            #print("no existing folder")
            os.makedirs(folder)
            Create_File0(pathToFile,fileContent)

#==============================================Delete file=========================

@app.route('/DELETE/<string:path>', methods=['GET'])
def Delete_File(path) :
    folder=path[0:path.rfind('\\')]
    if os.path.exists(path):
        os.remove(path)
        memory = shutil.disk_usage(folder) 
        if len(os.listdir(folder))==0:
            shutil.rmtree(folder)    #to delete a folder if it's empty
            #print("folder deleted")
        return "200 \nthe amount of free storage on the storage server in bytes is: "+str(memory[2]) 
    else:
        return "404"
        
#==============================================Initialize folder=========================
    
@app.route('/INITIALIZE/<string:pth>', methods=['GET'])    
def initialize_folder(pth) :
    folder=path[0:path.rfind('\\')]
    for sub in os.listdir(pth) :
        if os.path.isdir(folder+"\\"+sub) :
            shutil.rmtree(folder+"\\"+sub)
        else:
            os.remove(folder+"\\"+sub)
    memory = shutil.disk_usage(folder)  
    return "the amount of free storage on the storage server in bytes is: "+str(memory[2]) 
            
if __name__ == '__main__':
    app.run()


