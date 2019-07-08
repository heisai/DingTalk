import hmac
from hashlib import sha1
import base64
import sys
import datetime
import time
import os 
import traceback
import logging as logger
import requests
import json
from  urllib3 import encode_multipart_formdata
from  config import *


    
class Custom_Info:

    def __init__(self,name,unionid,userid,department,mobile,email = ""):
    
        self.name = name				    #客户名称 
        self.unionid = unionid				#客户唯一表识
        self.userid = userid 				#客户的使用id 
        self.department = department		#客户所在部门
        self.email = email 				    #客户绑定有邮箱
        self.mobile = mobile				#客户绑定手机号
    
    
class DingTalk:
    def __init__(self,*argc,**argv):

        self.Mobile_list = argc
        self.Type = argv["Type"]
        self.Content = argv["Content"]
        self.UUID = argv["Uuid"]
        self.appkey = appkey
        self.appsecret = appsecret
        self.AgentId = AgentId
        self.Url = ""
        self.Token = ""
        self.Info_List = {}
        
        self.__get_Token()
       
        self.__depart_custome_info("1","0","10")
        
        
        
    def __POST(self,data):
        data = json.dumps(data) 
        data = requests.post(url = self.Url,data = data) 
        return json.loads(data.text)
    def __GET(self):
        data = requests.get(self.Url) 
        return json.loads(data.text)
    '''
	获取Token
    '''
    def __get_Token(self):
        
        url = "https://oapi.dingtalk.com/gettoken?"
        self.__URL(url,False,appkey = self.appkey, appsecret = self.appsecret)
        recive = self.__GET()
        self.Token = recive["access_token"]

    def __URL(self,url,token_flag,**kwargs):
    
        if token_flag:
            url = url + "access_token="+ self.Token
        for key,value in kwargs.items():
            url += "&{0}={1}".format(key,value)
        self.Url = url
    '''
	获取当前部门下 客户的具体信息
    m_department_id:    部门ID 1:代表根部门
    m_offset:           读取偏移量
    m_size:             获取客户信息数量
    '''
    def __depart_custome_info(self,m_department_id ="1", m_offset = "0",m_size= "10"):
        
        url = "https://oapi.dingtalk.com/user/listbypage?"
        self.__URL(url,True,department_id = m_department_id, offset = m_offset,size = m_size)
        recive = self.__GET()
        
        if recive["errcode"] == 0:
            userlist = recive["userlist"]
            for  user in userlist:
                value = Custom_Info(user["name"],user["unionid"],user["userid"],user["department"],user["mobile"],email = "")
                key = user["mobile"]
                self.Info_List[key] = value
                     
        else:
            raise Exception(recive)
    
        
            
    def send_message(self):
    
        url = "https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?"
        self.__URL(url,True)
        for  Mobile  in self.Mobile_list:
            data = {'agent_id':self.AgentId , 'userid_list': self.Info_List[Mobile].userid} 
            data.update(self.MimeType())
            self.__POST(data)
        
	'''
		发送消息有三种
		1:text        纯文本格式
		2:File        上传文件
		3:Html 	      在网页显示
	'''
    def  MimeType(self,url = "https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?"):
        msg_dict = None
        if self.Type == "Text":
            msg_dict = self.Text()
        elif self.Type ==  "File":
            recive  = self.upload_file()
            self.__URL(url,True)
            msg_dict = self.File(str(recive["media_id"]))
        elif self.Type == "Html":
            msg_dict = self.Html()
        return  msg_dict
            

    def Text(self):
        time_str = "["+time.strftime("%H:%M:%S",time.localtime())+"]"
        content = "消息通知:\n\t\t%s\n%s"%(self.Content, time_str)
        msg_dict = {}
        msg_dict["msg"] ={ "msgtype":"text", "text":{"content": content}}

        return msg_dict
        
    def File(self,recive):
        
        msg_dict = {}
       
        
        msg_dict["msg"] = {
                                "msgtype": "file",
                                "file": {
                                    "media_id":recive
                                }
                          }
        
        return msg_dict
        
    def Html(self):
        recive = msg_dict = {}
        msg_dict["msg"]={
                            "msgtype": "action_card",
                            "action_card": {
                                "title": "消息通知",
                                "markdown": '消息通知:',
                                "btn_orientation": "1",
                                "btn_json_list": 
                                [
                                    {
                                        "title": "查看",
                                        "action_url": Action_Url + self.UUID
                                    }
                                ]
                                    }
                        }

        return msg_dict
        
     
    def upload_file(self):

        url = "https://oapi.dingtalk.com/media/upload?"
        self.__URL(url,True,type = "file")
        data ={}
        header = {}
        #data['media']= ("aaaa.txt",open(filename,'rb').read())
        data['media']= ("消息通知.txt",self.Content)
        encode_data = encode_multipart_formdata(data)
        data = encode_data[0]
        
        header['Content-Type'] = encode_data[1]
        r = requests.post(self.Url, data = data , headers = header)
        return json.loads(r.text)
        
       
       
        
       
        
      
        
        
if __name__ == '__main__':
    DT = DingTalk("13474248914", Type = "Html", Content = "12345678987654321",Title = "通知消息" )
    DT.send_message()
     
    
