# 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
import openai
import re
import json
import urllib.request as request_url

from data import Data

import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.request import urlopen
from bs4 import BeautifulSoup


openai.api_key = "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" #! ISSUE WITH API KEY
GMAIL_SECRET_KEY = 'leoijzvqxsmpzngp'

class Main():
    
    def __init__(self):
        self.data = Data()

    def get_img(self, prompt):  
        try:
            response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
            )
            response = response['data'][0]['url']
            print(response)
        except: response='../static/images/fallback-img.jpg'
        return response
   
    
    def get_text(self, prompt):
        response = openai.Completion.create( 
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.25, #EXPERIMENT WITH TEMP!
            max_tokens=300, 
            top_p=1, 
            frequency_penalty=0.25,
            presence_penalty=0
        )
        return response['choices'][0]['text']
    
    def get_babynames(self, prompt, gender): 
        names = self.get_text(("What " + gender + " baby names best suit this person (provide detailed reasoning)(max 5 names, min 2 names)" + prompt))

        print('NAMES:', names)
        
        # Define a regular expression pattern to match the numbered order, name, and description
        #? patter = ' #r'(\d+)\. (\w+) - (.+)'

        # Compile the regular expression pattern with the re.MULTILINE flag
        regex = re.compile(r'(?P<order>\d+)\. (?P<name>[^:]+):\s(?P<description>.+?)(?=\s*\d+\.|\Z)', re.MULTILINE) #? works?

        # Find all matches in the input string
        matches = regex.findall(names)
        
        if matches: pass
        else:
            regex = re.compile(r"(\d+)\.\s*([^\s:]+)\s*[:\-]\s*(.*)", re.MULTILINE) #r'(?P<order>\d+)\. (?P<name>[^–]+)–\s(?P<description>.+?)(?=\d+\.|\Z)'
            matches = regex.findall(names)
            
        print(matches)

        # Create a dictionary to store the output
        output_dict = {}

        # Loop over the matches and add them to the dictionary
        for match in matches:
            order = int(match[0])
            name = match[1].strip()
            description = match[2].strip()
            output_dict[order] = (name, description)
          
        keys, names_list, descriptions = [], [], []  
            
        keys = list(output_dict.keys())    
           
        for key, value in output_dict.items():
            names_list.append(value[0])
            descriptions.append(value[1]) 
            
        return keys, names_list, descriptions
        
    
        
    def get_name_data_ai(self, name, genders, origins):
        url = "https://www.behindthename.com/api/lookup.json/?name=" + name + "&key=na759038243"  #TODO pass through url
        fileobj = request_url.urlopen(url) 
        fileobj = fileobj.read().decode('utf-8')
        name_data = json.loads(fileobj)
        print(name_data)
        try:
            origin_list = []
            gender = name_data[0]['gender']  
            genders.append('male' if gender == 'm' else ('female' if gender == 'f' else 'male and female'))
            for origin in name_data[0]['usages']:
                origin_list.append(origin['usage_full'])
            origins[name] = origin_list 
        except: genders.append('unknown'); origins[name] = ['unknown']
        return genders, origins
    
    def get_100_names(self, gender):
        url = 'https://www.data.qld.gov.au/api/3/action/datastore_search?resource_id=9368a6bb-b6ae-4e47-a4f5-48299333047d&limit=100'
        fileobj = request_url.urlopen(url) 
        fileobj = fileobj.read().decode('utf-8')
        fileobj = json.loads(fileobj)
        names_list = []
        counts = []
        for names in fileobj['result']['records']:
            names_list.append(names[gender + ' Names'])
            counts.append(names['Count of ' + gender + ' Names'])
        return names_list, counts     
    
    def send_email(self, email, name):

        smtp_server = "smtp.gmail.com"
        port = 465
       
        msg = MIMEMultipart('alternative') 
        msg['Subject'] = 'BabyNameAI - ' + str(name)
        msg['From'] = 'BabyNameAI'
        msg['To'] = str(name)

        html = open('/workspaces/babyname-generator/templates/email.html').read()

        html = BeautifulSoup(html, features="html.parser")
        html = html.prettify()

        html = MIMEText(html, 'html')
        
        msg.attach(html)

        s_email = 'aibabyname@gmail.com'
        
        context = ssl.create_default_context()
        # Try to log in to server and send email
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            try:
                server.login(s_email, GMAIL_SECRET_KEY)
                server.sendmail(s_email, email, str(msg))
                print('EMAIL SENT')
            except Exception as e: print('Email Error -- ', e)
        
    def check_email(self, email, pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'):
        return re.fullmatch(pattern, email)
