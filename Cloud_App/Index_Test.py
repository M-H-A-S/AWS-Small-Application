#!/usr/bin/env python3
import math
import random
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from pandas_datareader import data as pdr
import os
import logging
import queue
import threading
import time
import http.client
import os
import logging
from flask import Flask, request, render_template

app = Flask(__name__)

# Do Render Function

# This function is resposible for rendering the pages existing in templates folder


def doRender(tname, values={}):
    if not os.path.isfile(os.path.join(os.getcwd(), 'templates/'+tname)):  # No such file
        return render_template('Home.html')
    return render_template(tname, **values)


queue = queue.Queue()  # queue is synchronized, so caters for multiple threads
#
'''runs = 5
count = 1000
'''

@app.route('/Home', methods=['POST'])
def Get_param():
    if request.method == 'POST':
        import yfinance as yf
        Num_of_res = int(request.form.get('nor'))
        Lenght_of_History = int(request.form.get('loph'))
        Number_of_Shots = int(request.form.get('nos'))
        today = date.today()
        decadeAgo = today - timedelta(days=3652)
        data = pdr.get_data_yahoo('AMZN', start=decadeAgo, end=today)
        data['Buy'] = 0
        data['Sell'] = 0

    for i in range(len(data)):
        # Hammer
        b = math.fabs(data.Open[i]-data.Close[i])
        d = 0.3*math.fabs(data.Close[i]-data.Open[i])
        if data.High[i] >= data.Close[i] and data.High[i]-d <= data.Close[i] and data.Close[i] > data.Open[i] and data.Open[i] > data.Low[i] and data.Open[i]-data.Low[i] > b:
            data.at[data.index[i], 'Buy'] = 1
        # Inverted Hammer
        if data.High[i] > data.Close[i] and data.High[i]-data.Close[i] > b and data.Close[i] > data.Open[i] and data.Open[i] >= data.Low[i] and data.Open[i] <= data.Low[i]+d:
            data.at[data.index[i], 'Buy'] = 1
            # Hanging Man
        if data.High[i] >= data.Open[i] and data.High[i]-d <= data.Open[i] and data.Open[i] > data.Close[i] and data.Close[i] > data.Low[i] and data.Close[i]-data.Low[i] > b:
            data.at[data.index[i], 'Sell'] = 1
        # Shooting Star
        if data.High[i] > data.Open[i] and data.High[i]-data.Open[i] > b and data.Open[i] > data.Close[i] and data.Close[i] >= data.Low[i] and data.Close[i] <= data.Low[i]+d:
            data.at[data.index[i], 'Sell'] = 1
    for i in range(Lenght_of_History, len(data)):
        if data.Buy[i] == 1:
            mean = data.Close[i - Lenght_of_History:i].pct_change(1).mean()
            std = data.Close[i-Lenght_of_History:i].pct_change(1).std()
    data_len = len(data)
    return [str(mean), str(std), str(Lenght_of_History), str(Number_of_Shots), str(data_len)]
    


class ThreadUrl(threading.Thread):

    def __init__(self, queue, task_id):
        threading.Thread.__init__(self)
        self.queue = queue
        self.task_id = task_id
        self.data = None  # need something more sophisticated if the thread can run many times

    def run(self):
        # while True: # uncomment this line if a thread should run as many times as it can
        mean, std, Lenght_of_History, Number_of_Shots, data_len = Get_param()
        count = self.queue.get()
        host = "x3utnhvsoe.execute-api.us-east-1.amazonaws.com"
        try:
            c = http.client.HTTPSConnection(host)
            #json= '{ "key1": ' + str(count) + '}'
            json = '{ "key1": "'+str(mean)+'" , "key2": "'+str(std)+'" ,"key3": "'+str(
                Lenght_of_History)+'" ,"key4": "'+str(Number_of_Shots)+'" ,"key5": "'+str(len(data)) + '"}'
            c.request("POST", "/default/VaR", json)
            response = c.getresponse()
            self.data = response.read().decode('utf-8')
            #print( self.data, " from Thread", self.task_id )
            print("Reachable here")
        except IOError:
            # Is the Lambda address correct?
            print('Failed to open ', host)
            # signals to queue job is done
            self.queue.task_done()


'''
# Function Chace avoid - it avoid GAE from stack with pages.
@app.route('/cacheavoid/<name>')
def cacheavoid(name):
    # file exists?
    if not os.path.isfile( os.path.join(os.getcwd(), 'static/'+name) ):
        return ( 'No such file ' + os.path.join(os.getcwd(), 'static/'+name) )
        f = open ( os.path.join(os.getcwd(), 'static/'+name) )
        contents = f.read()
        f.close()
    return contents

'''
# Run paralllel


def parallel_run():
    threads = []
    # spawn a pool of threads, and pass them queue instance
    for i in range(0, runs):
        t = ThreadUrl(queue, i)
        threads.append(t)
        t.setDaemon(True)
        t.start()

    # populate queue with data
    for x in range(0, runs):
        queue.put(count)
        # wait on the queue until everything has been processed
        queue.join()
        results = [t.data for t in threads]
        # print(results)
        return doRender('Result.htm', {'note': results})

# This function it 1) calculate the mu and the std of the yahoo. 2) Get parameters from the user 3) send the parameters to Lambda to calculate risk.


@app.route('/Home', methods=['POST'])
def Calculate_Risk_Averages_Funtion():
    parallel_run()


'''

# This Function is resposible for EC2 creation using Lambda
@app.route('/Home', methods=['POST'])
def Creation_of_EC2_By_Lambda():
    if request.method == 'POST':
        start = time.time()
        service_type = str(request.form.get('st'))
        Number_of_Resources = int(request.form.get('nor'))
        
        if service_type == 'EC2':
            c = http.client.HTTPSConnection("s5rnthvsoe.execute-api.us-east-1.amazonaws.com")
            json= '{ "key1": "'+Number_of_Resources+'"}'
            c.request("POST", "/default/Create_EC2_By_Lambda", json)
            response = c.getresponse()
            data = response.read().decode('utf-8')
            return doRender( 'index.htm',
                        {'note3': data} )

'''
'''
# Wirtinng the result from Lambda into S3
@app.route('/s3')
def s3listbuckets():
    os.environ['AWS_SHARED_CREDENTIALS_FILE']='./cred' 
    # Above line needs to be here before boto3 to ensure file is read
    import boto3
    s3 = boto3.resource('s3')
    bucketnames=[bucket.name for bucket in s3.buckets.all()]
    return doRender('index.htm', {'note': ' '.join(bucketnames)})
'''


def parallel_run():
    threads = []
    # spawn a pool of threads, and pass them queue instance
    for i in range(0, runs):
        t = ThreadUrl(queue, i)
        threads.append(t)
        t.setDaemon(True)
        t.start()

    # populate queue with data
    for x in range(0, runs):
        queue.put(count)

    # wait on the queue until everything has been processed
    queue.join()
    results = [t.data for t in threads]
    # print(results)
    return doRender('Result.htm', {'note': results})

# This function suppoed to render the audit infromation about user selection:


@app.route('/s3')
def s3listbuckets():
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = './cred'
    # Above line needs to be here before boto3 to ensure file is read
    import boto3
    s3 = boto3.resource('s3')
    bucketnames = [bucket.name for bucket in s3.buckets.all()]
    return doRender('audit.htm', {'note5': ' '.join(bucketnames)})


# catch all other page requests - doRender checks if a page is available (shows it) or not (index)
@ app.route('/', defaults={'path': ''})
@ app.route('/<path:path>')
def mainPage(path):
    return doRender(path)


@ app.errorhandler(500)
# A small bit of error handling
def server_error(e):
    logging.exception('ERROR!')
    return """
    An  error occurred: <pre>{}</pre>
    """.format(e), 500


if __name__ == '__main__':
    # Entry point for running on the local machine
    # On GAE, endpoints (e.g. /) would be called.
    # Called as: gunicorn -b :$PORT index:app,
    # host is localhost; port is 8080; this file is index (.py)
    app.run(host='127.0.0.1', port=8080, debug=True)
