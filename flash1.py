


from flask import Flask, jsonify,request,send_from_directory
import json
import time
import uuid
import os 
import uuid
from  DingTalkApi import DingTalk
import logging
import traceback
import  sys
from  config import *



app = Flask(__name__)
time_dir = ""


def track_error():
    (type,value,trace)=sys.exc_info()
    logging.error("*"*150)
    logging.error("Error_Type:\t%s\n"%type)
    logging.error("Error_Value:\t%s\n"%value)
    logging.error("%-40s %-20s %-20s %-20s\n"%("Filename", "Function","Linenum", "Source"))
    for filename, linenum, funcname, source in traceback.extract_tb(trace):
        logging.error("%-40s %-20s %-20s%-20s" % (os.path.basename(filename),funcname,linenum, source))
    logging.error("*"*150)
    
def writestr(m_file,m_str):

    fd = open(m_file,'w')
    fd.write(m_str)
    fd.close()
   
def request_data(recived):

    
    
    if recived["Type"] == "Html":
    
        global  time_dir
        time_dir = os.path.join( os.getcwd() , time.strftime("%Y%m", time.localtime()))
        if  not os.path.exists(time_dir):
            os.mkdir(time_dir)
        m_uuid = str(uuid.uuid1())
        uuid_filename = os.path.join(time_dir,m_uuid)
        writestr(uuid_filename, recived["Content"])
        
        recived["Uuid"] = m_uuid
        recived["uuid_filename"] = uuid_filename
        
    else:
        recived["Uuid"] = ""
        recived["uuid_filename"] = ""
    
    return recived
    



@app.route('/send/Message',methods = ['GET','POST'])
def Message():

    try:
        data = request.get_data()
        #print(data.repl)
        print(type(data))
          
        print(str(data, encoding = "utf-8").replace("\r\n",""))
        #return data
        print(json.loads(data))
        #return data
        
        recived = request_data(json.loads(data))
        print(recived)
        DT = DingTalk(*recived["Mobile"], **recived)
        DT.send_message()
    except Exception as e:
        track_error()
        return "{'code':'100'}"

    else:
        #return  recived["uuid_filename"]
        return "{'code':'0'}"
     
@app.route('/show/html/<uuid>',methods = ['GET','POST'])
def html(uuid):
    text = "" 
    try:
        global time_dir
    
        uuidfile = os.path.join(time_dir,uuid)
        fd = open(uuidfile,'r')
        text = fd.read()
        fd.close()
    except Exception as e:
        track_error()
        return "{'code':'100'}"
    else:
        return text
    
if __name__ == '__main__':
    app.run(debug=True,host = IP,port = port)
