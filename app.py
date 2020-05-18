


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

time_dir = os.path.join( log_path , time.strftime("%Y%m", time.localtime()))
if  not os.path.exists(time_dir):
    os.mkdir(time_dir)



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

    global    time_dir 
    m_uuid = str(uuid.uuid1())
    time_dir = os.path.join( log_path , time.strftime("%Y%m", time.localtime()))
    if  not os.path.exists(time_dir):
            os.mkdir(time_dir)
  
    if  recived["Type"] == "Html":
    
        uuid_filename = os.path.join(time_dir,m_uuid)
        writestr(uuid_filename, recived["Content"])
        recived["Uuid"] = os.path.join(time.strftime("%Y%m", time.localtime()),m_uuid)

    else:
        recived["Uuid"] = ""

    
    if recived["File_url"] != "" :
        recived["Type"] += "&Accessory"
        writestr(uuid_filename+"_url", recived["File_url"])
        
    return recived
    



@app.route('/send/Message',methods = ['GET','POST'])
def Message():

    try:
        data = request.get_data()
        recived = request_data(json.loads(data))
        DT = DingTalk(*recived["Mobile"], **recived)
        DT.send_message()
    except Exception as e:
        track_error()
        return '{"code":"100"}'

    else:
        return '{"code":"0"}'
     
@app.route('/show/html/<time_dir>/<uuid>',methods = ['GET','POST'])
def html(time_dir, uuid):
    text = "" 
    try:
        uuidfile = os.path.join(time_dir,uuid)
        fd = open(uuidfile,'r')
        text = fd.read()
        fd.close()
    except Exception as e:
        track_error()
        return "{'code':'100'}"
    else:
        if os.path.exists(uuidfile+"_url"):
            fd = open(uuidfile+"_url")
            File_Url = fd.read()
            fd.close()
            return text + " <br><a  href= %s download='w3logo'>¸½¼þÏÂÔØ</a>"%(File_Url)
        else:
            return text


if __name__ == '__main__':
    app.run(debug=True,host = IP,port = port)
