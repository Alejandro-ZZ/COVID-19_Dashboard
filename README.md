# COVID-19_Dashboard
Dashboard programed in python and made with Streamlit framework. Shows a brief information about COVID-19 status in Colombia based in open data taken from [GOV.CO](https://www.gov.co/home/). All data in the csv file is procesed and cleaned with the [pandas library](https://pandas.pydata.org/docs/reference/frame.html), graphics are construted with [plotly library](https://plotly.com/python/) and finally, everything is showing up locally with the [streamlit framework](https://docs.streamlit.io/en/stable/api.html).

To know more info, visit: [AlejandroZZ](https://alejandrozz.pythonanywhere.com/dash-covid/) website.

## Running locally
To run this dashboard on you PC, go to the local address where you will save the project, open a bash/windows console there and follow this steps:

**1. Clone this repository** 
      
      git clone https://github.com/Alejandro-ZZ/COVID-19_Dashboard.git

**2. Install the required packages** 
      
      cd COVID-19_Dashboard
      pip install -r requirements.txt

**3. Run the Streamlit server** 
      
      streamlit run Dashboard-COVID.py

   After running the previous line, a message like the next one should be printed in your console and a pop-up window will open in your default browser.

      You can now view your Streamlit app in your browser.

      Local URL: http://localhost:XXXX
      Network URL: http://XX.XXX.X.XX:XXXX

  The four number after the colon are the port where the app is been executed. The app can be stopped at anytime by pressing **ctrl + C** in the console

**Note:**
The information showed in the streamlit app is the one read in the "Casos_positivos_de_COVID-19_en_Colombia.csv" file, this is a short data set for probing it. You can go to the complete [dataset](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Casos-positivos-de-COVID-19-en-Colombia/gt2j-8ykr/data) and download it by clicking on the "export" link and then choosing the CSV option. Replace the old dataset by coping the .csv file downloaded and pasting it in the "COVID-19_Dashboard" folder.

Everytime any change is done, a message in the upper right corner of your app (in the browser) will appers showing the option to rerun the app.

## Clearing cache
Because the code uses the streamlit.chache utility, when updating the CSV data, you must clear the cache it before reruning the app. The chache can be cleared with a built-in menu in the streamlit app (hidden by default in the code). To display it just comment the line 282 and run again the app.

A "hamburguer menu" should apper at the upper right corner, click it and select the "clear cache" option. Then rerun the app and you will see the updated information.

## Using Ngrok to share with others
Once you have runned correctly the app in your computer, you can share it with other people by using ngrok service. Just follow this steps:

**1. Download ngrok:**
[Download](https://ngrok.com/download) the ngrok.zip file to your Downloads folder and then extract it in a folder. It will make a folder like "ngrok_2.0.19_windows_386" and in that folder, you will find a single file named ngrok.exe. You can put this file anywhere on your computer but for now we will just execute it from the Downloads folder. 

**2. Execute it:**
Make sure your Streamlit application is up and running and then open up the folder unzipped. Then use the follow command

**For windows**
 
      ngrok http XXXX
     
**For Linux**

      ./ngrok http XXXX

The four numbers (XXXX) are the port where the app is been executing. Finally it will shows a message like this:

      Tunnel Status       online                                            
      Version             2.0.19/2.0.19                                     
      Web Interface       http://127.0.0.1:4040                             
      Forwarding          http://c5343c6e.ngrok.io -> localhost:XXXX        
      Forwarding          https://c5343c6e.ngrok.io -> localhost:XXXX       

      Connections         ttl     opn     rt1     rt5     p50     p90       
                          0       0       0.00    0.00    0.00    0.00 

Use the link provide (http://c5343c6e.ngrok.io) to share with others. This link will be available for 7 hours or until you stop the app.
