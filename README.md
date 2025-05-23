# Real-Time-Gmail-Inbox-Sentiment-Analysis
This project calculates sentiments score for snippet of every gmail messages in i the inbox. This project can be implemented in any company irrespective of the industry. Benefits of such projects includes; Improved Customer Service, Development of Quality Products and services, Discovering New Markets Increasing Sales Revenue, Improved Crisis Management and etc. I am unable to deploy the app on the web since i use my personal email inbox as the dataset. I used Docker to run the ETL pipelines from start to finish.

    
# Database, Libraries, and Visualization Tools:
   ## Data Extraction From Gmail
  - Gmail API 
       - googleapiclient.discovery
       - google_auth_oauthlib.flow
       - google.auth.transport.requests
  - dateutil.parser
  - time
  - os
  - pickle
  - codecs
  - beautiful soup
  - pymongo - connection to dowlond extracted data into Docker container (mongodb)

   ## Data Extraction, Transformation and Loading :
   - vaderSentiment.vaderSentiment
   - codecs
   - pandas
   - sqlachemy
   - regex
   - time
   - datetime
   - pymongo for connection to extract data from Docker container (mongodb)
   - sqlachemy - connection to load cleaned data into Docker container (postgresql)
   
   ## Data Visualization:
   - dash
   - dash_bootstrap_components
   - dash.dependencies
   - dash_table
   - plotly.express
   - plotly.graph_objs
   - pandas
   - numpy
   - plotly.graph_objs
   - time
   - sqlachemy - connection to read cleaned data from Docker container (postgresql)
 


## Basic Workflow Overviewc
![App Screenshot](https://raw.githubusercontent.com/joRic20/Real-Time-Gmail-Inbox-Sentiment-Analysis/main/Basic%20Workflow%20Overview.png?token=GHSAT0AAAAAABW7676GJWCOWBCWCSLG4UOYYXMQWEQ)


## Deployment

To deploy this project:
- activate your virtual enviroment
```bash
  conda activate <env name>
```

- run your docker containers containing your ETL pipelines
```bash
  Docker start <container name>
```

- run app.py file to visualize the live streaming on plotly dashboard
```bash
  python app.py
```


## Screenshot of the Plotly Dashboard

![App Screenshot](https://raw.githubusercontent.com/joRic20/Real-Time-Gmail-Inbox-Sentiment-Analysis/main/Screenshot%20of%20local%20app.png?token=GHSAT0AAAAAABW7676GMBNHEB4QJ2DX6Y4CYXMQX7Q)
