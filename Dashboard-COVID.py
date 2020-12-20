# IMPORTANT: make sure to install packages imported before running
# pip install package_name
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os, time

# Dataset of COVID-19 positive cases in Colombia (GOV.CO)
# https://www.datos.gov.co/Salud-y-Protecci-n-Social/Casos-positivos-de-COVID-19-en-Colombia/gt2j-8ykr/data

# Shows some information when probing
DEBUG = False

# COVID csv dataset file
FILE = 'Casos_positivos_de_COVID-19_en_Colombia.csv'
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#//                                                                                                                                    //
#//                                                             FUNCTIONS                                                              //
#//                                                                                                                                    //
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Caches the information
@st.cache(persist=True)
def load_csv_data(address):
    '''
    Action: Loads and organizes COVID-19's data from csv dataset

    Output
    Returns a tuple with three items:
        1. DataFrame from pandas wich contains COVID information.
        2. ndarray with all Colombia departments.
        3. ndarray with all Colombia municipalities.
    '''
    print("Reading data...")

    # Names of the columns to read from the csv file
    read_col = ['ID de caso','Fecha de notificación','Nombre municipio','Nombre departamento','Ubicación del caso', 'Recuperado',
                'Edad','Sexo','Estado','Fecha de muerte','Fecha de diagnóstico','Fecha de recuperación', 'fecha reporte web']

    #Reads the csv file and converts it to a DataFrame
    data = pd.read_csv(address, usecols = read_col, low_memory = False)

    # Replace in 'Sex' the values filled with 'f' and 'm' by 'F' and 'M'
    data = data.replace({'Sexo': {'f': 'F', 'm': 'M'}})

    # Replace in 'Sex' the values filled with 'F' and 'M' by 'Femenino' and 'Masculino'
    data = data.replace({'Sexo': {'F': 'Femenino', 'M': 'Masculino'}})

    # Some special districts are changed to its respective department
    data = data.replace({'Nombre departamento': {'BARRANQUILLA': 'ATLANTICO',
                                                      'CARTAGENA': 'BOLIVAR',
                                                      'Buenaventura D.E.': 'VALLE',
                                                      'STA MARTA D.E.': 'MAGDALENA'}})

    # Replace nan values with 'Fallecido NO COVID' in the 'Ubicación del caso' column
    data['Ubicación del caso'] = data['Ubicación del caso'].fillna('Fallecido NO COVID')

    # Replace nan values with 'N/A' in the 'Estado' column
    data['Estado'] = data['Estado'].fillna('N/A')

    # Takes all departments and municipalities with COVID cases reported
    dptos = data['Nombre departamento'].dropna().unique()
    towns = data['Nombre municipio'].dropna().unique()

    # Date in format 'dd/mm/yyyy' is changed to 'yyyy-mm-dd' format in all date columns
    data['fecha reporte web'] = pd.to_datetime(data['fecha reporte web'], infer_datetime_format=True, dayfirst=True)
    data['Fecha de muerte'] = pd.to_datetime(data['Fecha de muerte'], infer_datetime_format=True, dayfirst=True)
    data['Fecha de notificación'] = pd.to_datetime(data['Fecha de notificación'], infer_datetime_format=True, dayfirst=True)
    data['Fecha de diagnóstico'] = pd.to_datetime(data['Fecha de diagnóstico'], infer_datetime_format=True, dayfirst=True)
    data['Fecha de recuperación'] = pd.to_datetime(data['Fecha de recuperación'], infer_datetime_format=True, dayfirst=True)

    # Changes all cases of same field written different in some columns
    data = data.replace({'Ubicación del caso': {'casa': 'Casa', 'CASA': 'Casa'}})
    data = data.replace({'Estado': {'moderado': 'Moderado', 'LEVE': 'Leve'}})
    data = data.replace({'Recuperado': {'fallecido': 'Fallecido'}})

    #A different way to capitalize fields in a column is using 's.str.capitalize()'
    #method, where 's' is a pandas serie.

    return (data, dptos, towns)
#=======================================================================================================================================#
#=======================================================================================================================================#
def data_report(info, report, label, acum = False):
    '''
    Inputs:
        acum   -> True:  process the accumulated sum
                  False: process the partial sum

        info   -> An object of type Pandas DataFrame with at least two columns:
                  one called with name in 'report' param and the other 'ID de caso'
                  this must be the second column of the Dataframe

        report -> String with the column name of the report needed

        label  -> String with the column name where the data sum will be written

    Output:
        Returns an object of type DataFrame from the pandas library whose index
        is the param 'report' and has a single column whose name is the respective
        param 'label'
    '''
    # Counts how many times each field in 'report' column is repeated and save
    # it in 'ID de caso' column
    info = info.groupby(report).count()[[info.columns[1]]]

    # 'ID de caso' is renamed to the string in 'label' param
    info = info.rename(columns = {info.columns[0]:label})

    # Acumulated sum in the 'report' column is made if 'acum' param is True
    if acum :
        info = info.cumsum()

    return info
#=======================================================================================================================================#
#=======================================================================================================================================#
# Caches the information
@st.cache(persist=True)
def get_summary(info, key_list, dpto_info = True):
    '''
    Inputs:
        info      -> An object of type DataFrame from pandas.

        key_list  -> List with all the departments or municipalities
                     to obtain the report.

        dpto_info -> True: Departmental report (default)
                     False: Municipal report.

    Output:
        Returns an object of type DataFrame with five columns:

            1. Departamento/Municipio, name of the department
               or municipality from which the report is made.

            2. Casos confirmados, number of accumulated cases confirmed.

            3. Recuperados, number of recovered cases.

            4. Fallecidos, number of deceased cases.

            5. Atendidos en UCI, number of cases seen in ICU.

    '''
    info = info.reset_index()
    info = info.drop(columns=info.columns[0])

    if dpto_info:
        info = info.set_index('Nombre departamento')
        col_name = 'Departamento'
    else:
        info = info.set_index('Nombre municipio')
        col_name = 'Municipio'

    info_dict = {}
    diag_acum = []
    recu = []
    fallecidos = []
    UCI = []

    for key in key_list:

        nun_fallecidos = 0
        num_UCI = 0
        num_recuperados = 0
        casos_diag = 0

        # Checks that the department/municipality info isn't a pandas series.
        if not isinstance(info.loc[key], pd.Series):

            # Takes number of accumulated cases.
            casos_diag = data_report(info.loc[key], 'fecha reporte web', 'Casos', True).max()[0]

            # Take cases based on their case location
            d = data_report(info.loc[key], 'Ubicación del caso', 'Casos')

            # Extract number of deceased patients
            if 'Fallecido' in d.index:
                nun_fallecidos = d.loc['Fallecido'].array[0]

            # Extracts number of patients seen in ICU
            if 'Hospital UCI' in d.index:
                num_UCI = d.loc['Hospital UCI'].array[0]

            # Take cases according to the recovered column
            d = data_report(info.loc[key], 'Recuperado', 'Casos')

            # Extract number of recovered patients
            if 'Recuperado' in d.index:
                num_recuperados = d.loc['Recuperado'].array[0]

        # If department/municipality info is a pandas series
        # it means that there's just one case confirmed.
        else:
            casos_diag = 1
            atencion = info.loc[key].loc['Ubicación del caso']

            # Checks patient care.
            if atencion == 'Recuperado':
                num_recuperados = 1
            elif atencion == 'Fallecido':
                nun_fallecidos = 1
            elif atencion == 'Hospital UCI':
                num_UCI = 1

        diag_acum.append(casos_diag)
        recu.append(num_recuperados)
        fallecidos.append(nun_fallecidos)
        UCI.append(num_UCI)

    info_dict.setdefault(col_name, key_list)
    info_dict.setdefault('Confirmados', diag_acum)
    info_dict.setdefault('Recuperados', recu)
    info_dict.setdefault('Fallecidos', fallecidos)
    info_dict.setdefault('En UCI', UCI)

    df = pd.DataFrame(data=info_dict)
    df = df.sort_values(by = 'Confirmados', ascending = False).reset_index()
    df.pop('index')

    return df
#=======================================================================================================================================#
#=======================================================================================================================================#
def get_info(csv_data, key_list, dpto_summary = True):
    '''
    Inputs:
        csv_data     -> Pandas DataFrame Type Object

        key_list     -> List with all the departments or
                        municipalities to obtain the report

        dpto_summary -> True:  process the accumulated sum
                        False: process the partial sum
    Output:
        Returns a tuple with five elements:

        1. cases, sum of diagnostic cases per day.
        2. status, summary of patients according to their health status.
        3. dpto_info, summary of data by department or municipality.
        4. atention, summary of patients by case location.
        5. recu, summary of patients by 'Recuperado' columns info.
    '''
    # Cumulative sum of diagnosed patients
    cases = data_report(csv_data, 'fecha reporte web', 'Casos diagnosticados')

    # Gets all departments or municipalities summary report depending on
    # 'dpto_summary' param
    if len(key_list) == 0:
        dpto_info = None
    else:
        dpto_info = get_summary(csv_data, key_list, dpto_summary)

    # Patients according to the type of location of the case
    atention = data_report(csv_data, 'Ubicación del caso', 'Número de pacientes')

    # Patients according to medical status
    status = data_report(csv_data, 'Estado', 'Número de pacientes')

    # Patients according to the column 'Recuperado'
    recu = data_report(csv_data, 'Recuperado', 'Número de pacientes')

    return (cases, status, dpto_info, atention, recu)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#//                                                                                                                                    //
#//                                                        STAGE OF PREPROCESS                                                         //
#//                                                                                                                                    //
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Loads COVID information
(all_data, all_dptos, all_muni) = load_csv_data(FILE)

# Hide the MENU icon
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stButton button {border-color: #f63366;color: #f63366; transform: translate(50%,50%);}
.stButton button:hover {border-color: #f63366;color: #fff; background: #f63366;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Shows AlejandroZZ icon
import base64
img_path = 'favicon_io/favimg.png'
link = 'https://alejandrozz.pythonanywhere.com/'
with open(img_path, "rb") as imageFile:
    image_base64 = base64.b64encode(imageFile.read()).decode()
html = f"<a href={link} target='_blank'><img src='data:image/png;base64,{image_base64}' style='margin: auto; display: flex; height: 150px;'></a>"
st.sidebar.markdown(html, unsafe_allow_html=True)

st.title('Información COVID-19')
st.sidebar.title('Filtros')

tipo_reporte = st.sidebar.radio('Por tipo de reporte',['Nacional', 'Departamental', 'Municipal'])
tipo_grafica = st.sidebar.radio('Por tipo de pacientes', ['Reportados', 'Fallecidos', 'Recuperados'])

if tipo_reporte == 'Nacional':
    report_data = all_data
    report_list = all_dptos
    report_name = 'Colombia'
    summary_dpto = True

elif tipo_reporte == 'Departamental':
    # List of all departments
    dpto_select = st.sidebar.selectbox('Departamento',all_dptos)

    # Takes the departments as the index of the information
    dpto_info = all_data.set_index('Nombre departamento')

    report_data = dpto_info.loc[dpto_select]
    report_list = all_data[all_data['Nombre departamento'] == dpto_select]['Nombre municipio'].dropna().unique()
    report_name = dpto_select
    summary_dpto = False

elif tipo_reporte == 'Municipal':
    # List of all departments
    dpto_select = st.sidebar.selectbox('Departamento',all_dptos)

    # Takes municipalities in the selected department
    muni_per_dpto = all_data[all_data['Nombre departamento'] == dpto_select]['Nombre municipio'].unique()

    # Save the selected municipality
    muni_select = st.sidebar.selectbox('Municipio',muni_per_dpto)

    muni_info = all_data.set_index(['Nombre departamento', 'Nombre municipio'])

    report_data = muni_info.loc[dpto_select, :].loc[muni_select]
    report_list = []
    report_name = muni_select
    summary_dpto = True

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#//                                                                                                                                    //
#//                                                        DATA PROCESSING                                                             //
#//                                                                                                                                    //
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def general_info():
    '''
    get_info() loads general information from COVID data and stores it in 5 variables:

        |==========|========================================================|
        | Variable |                    Description                         |
        |==========|========================================================|
        |     a    |  sum of diagnostic cases per day.                      |
        |     b    |  summary of patients according to their health status. |
        |     c    |  summary of data by department or municipality.        |
        |     d    |  summary of patients by case location.                 |
        |     e    |  summary of patients by 'Recuperado' columns info.     |
        |==========|========================================================|
    '''
(a, b, c, d, e) = get_info(report_data, report_list, summary_dpto)

# Shows last updated datetime of csv dataset
last_updated(FILE)

# Verifies if there are recovered and deceased cases according to the type of distribution chosen
if (tipo_grafica == 'Recuperados' and 'Recuperado' in e.index) or (tipo_grafica == 'Fallecidos' and 'Fallecido' in e.index) or (tipo_grafica == 'Reportados'):

    # Checks the type of distribution chosen to graph
    if tipo_grafica != 'Reportados':
        report_data = report_data.reset_index().set_index('Recuperado').loc[tipo_grafica[0:len(tipo_grafica)-1]]

    # SEX data
    sex_report = data_report(report_data, 'Sexo', 'Número de pacientes').reset_index()

    # AGE data
    age_data = report_data.copy()

    # takes the 'Edad' column and converts it to Str type
    age_data['Edad'] = age_data.loc[:,'Edad'].astype(str)

    age_data = data_report(age_data, 'Edad', 'Número de pacientes').reset_index()

    # Inclusive age range from left
    bins = pd.IntervalIndex.from_tuples([(0, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 60),
                                         (60, 70), (70, 80), (80, 90), (90, 120)], closed = 'left')

    # Interval labels
    names = ["0 - 9", "10 - 19", "20 - 29", "30 - 39", "40 - 49","50 - 59", "60 - 69", "70 - 79", "80 - 89",
             "Mayor de 89"]

    age_data['Intervalos'] = pd.cut(age_data['Edad'].astype(int), bins)
    age_data.pop('Edad')
    age_data = age_data.groupby('Intervalos').sum().reset_index()
    age_data['Intervalos'] = age_data['Intervalos'].categories = names

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#//                                                                                                                                    //
#//                                                          GRAPHIC STAGE                                                             //
#//                                                                                                                                    //
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Graph of accumulated diagnosed cases
fig1 = px.line(a.cumsum(), y = a.columns[0], labels={'fecha reporte web':'Fecha de reporte'},
               title = "Histórico de casos reportados en " + report_name)
st.plotly_chart(fig1)

# Graph of diagnostic cases per day
fig2 = px.line(a, y = a.columns[0], labels={'fecha reporte web':'Fecha de reporte'},
               title = "Histórico de casos diarios reportados en " + report_name)
st.plotly_chart(fig2)

# Pie diagram according to the location of the patient's case
fig_A = px.pie(e.reset_index(), values='Número de pacientes', names='Recuperado',
               title='Distribución por atención de casos reportados')
st.plotly_chart(fig_A)

# Pie diagram according to the status of the patients
fig_B = px.pie(b.reset_index(), values='Número de pacientes', names='Estado',
               title='Distribución por estado de casos reportados')
st.plotly_chart(fig_B)

# Summary report is shown just if record type selected is either nacional or departmental
if tipo_reporte != 'Municipal':
    st.header("Resumen " + tipo_reporte.lower())
    fig_C = px.bar(c, x = c.columns[0], y=[c.columns[4], c.columns[3], c.columns[2], c.columns[1]],
                   labels={c.columns[0]:'', 'value': 'Número de pacientes', 'variable': 'Variable'})
    st.plotly_chart(fig_C)

st.markdown("## Para filtrar las gráficas siguientes use el filtro 'Por tipo de pacientes' ubicado al costado izquierdo")

try:
    # Sex pie diagram according to the chosen distribution
    fig_D = px.pie(sex_report, values=sex_report.columns[1], names=sex_report.columns[0],
                   title='Distribución por sexo de casos ' + tipo_grafica.lower())
    st.plotly_chart(fig_D)

    # Bar chart by age according to the chosen distribution
    fig_E = px.bar(age_data, x='Intervalos', y='Número de pacientes',
                   labels={'Intervalos': 'Edad'},height=400, title = "Distribución por edad de casos " + tipo_grafica.lower())
    st.plotly_chart(fig_E)

# An exception would rise if both or either 'sex_report' and 'age_data' variables doesn't exists
# what it means is that the chosen department or municipality has no recovered or deceased patients
except NameError:
    st.markdown("### ❌ No existen pacientes " + tipo_grafica.lower())
