

from bs4 import BeautifulSoup
import requests
import pandas as pd

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyodbc
import datetime as dt

headers = {'X-Requested-With': 'XMLHttpRequest'}
# link brings sorted data by date posted. So top records will be "Posted Today"
r = requests.get('https://www.governmentjobs.com/careers/home/index?agency=sdcounty&sort=PostingDate&isDescendingSort=true&_=1580794679579', headers=headers)
soup = BeautifulSoup(r.content, 'lxml')
# getting a container with all we need
all_jobs  = soup.find_all('li', attrs = {'class':'list-item'}) 

# using list comprehension to get position name and link
position_name = [position.find('h3').get_text().strip() for position in all_jobs]
link = ['https://www.governmentjobs.com' + links.find('a').get('href') for links in all_jobs]


salaries= []
dates_posted = []



for jobs in all_jobs:
    all_salary = jobs.find_all('li')
    salary = all_salary[1].get_text(strip=True) # converting to text
    salary = '$' + salary.split('$',1)[1]
    salary = ' '.join(salary.split(' ')[:3])
    salaries.append(salary) 

    # date position was posted
    date_posted = jobs.find('span', attrs={'class': 'list-entry-starts'})
    dates_posted.append(date_posted.text)

df = pd.DataFrame({
    'Position':position_name,
    'Salary':salaries,
    'Posted': dates_posted,
    'Link': link
})

# selecting only rows with "Posted today"
df = df[df['Posted'].isin(['Posted today'])] # or df = df[df.Posted.isin(['Posted today'])]
#print(df)

# today's date in a format like 02-06-2020
today = dt.datetime.now().strftime('%m-%d-%Y')

# decorating a table using css
message_start = f"""
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<h3>County jobs posted today ({today}) </h3>"""
message_style = """
<style type="text/css" media="screen">
    #customers {
    font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
    font-size: 12px;
    border-collapse: collapse;
    width: 100%;
    }

    #customers td, #customers th {
    border: 1px solid #ddd;
    padding: 8px;
    }

    #customers tr:nth-child(even){background-color: #f2f2f2;}

    #customers tr:hover {background-color: #ddd;}

    #customers th {
    padding-top: 12px;
    padding-bottom: 12px;
    text-align: left;
    background-color: #4CAF50;
    color: white;
    }
</style>
</head>
<body>
"""

# Sending Email

def send_email(user, recipients, subject):
    try:
        message_body = df.to_html(index=False, table_id="customers") #set table_id to your css style name
        message_end = """</body>"""
        messages = (message_start + message_style + message_body + message_end)
        dfPart = MIMEText(messages,'html')

        user = "user@email"
        pwd = "password"
        subject = "County jobs posted today"
        recipients = "recipient@email"
        #Container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = user
        msg['To'] = recipients #",".join(recipients)
        msg.attach(dfPart)

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(user, pwd)  

        server.sendmail(user, recipients, msg.as_string())
        server.close()
        print("Mail sent succesfully!")
    except Exception as e:
        print(str(e))
        print("Failed to send email")
# sending email only if dataframe is not empty
if len(df.index)>0:
    send_email("user","recipients","Test Subject")








