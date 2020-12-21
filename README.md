# COVID-19_Dashboard
Dashboard programed in python and made with Streamlit framework. Shows a brief information about COVID-19 status in Colombia based in open data taken from [GOV.CO](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Casos-positivos-de-COVID-19-en-Colombia/gt2j-8ykr/data). All data in the csv file is procesed and cleaned with the [pandas library](https://pandas.pydata.org/docs/reference/frame.html), graphics are construted with [plotly library](https://plotly.com/python/) and finally, everything is showing up locally with the [streamlit framework](https://docs.streamlit.io/en/stable/api.html).

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

  The four number after the colon are the port where the app is been executed

**Note:**
The information showed in the streamlit app is the one read in the "Casos_positivos_de_COVID-19_en_Colombia.csv" file, this is a short data set for probing it. You can go to the complete [dataset](https://www.datos.gov.co/Salud-y-Protecci-n-Social/Casos-positivos-de-COVID-19-en-Colombia/gt2j-8ykr/data) and download it by clicking on the "export" link and then choosing the CSV option. Replace the old dataset by coping the .csv file downloaded and pasting it in the "COVID-19_Dashboard" folder.

Everytime any change is done, a message in the upper right corner of your app (in the browser) will appers showing the option to rerun the app.

## Clearing cache
Because the code uses the streamlit.chache utility, when updating the CSV data, you must clear the cache it before reruning the app. The chache can be cleared with a built-in menu in the streamlit app (hidden by default in the code). To display it just comment the line 282 and run again the app.

A "hamburguer menu" should apper at the upper right corner, click it and select the "clear cache" option. Then rerun the app and you will see the updated information.
