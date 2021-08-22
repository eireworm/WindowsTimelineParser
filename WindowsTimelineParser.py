from os import environ
from os import remove
from PyPDF2 import PdfFileMerger
from time import strftime
from time import localtime
import glob
import json
import matplotlib.pyplot as plt
import pandas
import re
import sqlite3

# returns the absolute path to the ActivitiesCache.db database file
def get_activities_cache_db_absolute_path():
    directory = 'C:\\Users\\' + str(environ['username']) + '\\AppData\\Local\\ConnectedDevicesPlatform\\'
    db_files = glob.glob(directory + "/**/ActivitiesCache.db", recursive = True)
    if len(db_files) == 0:
        print("Couldn't find ActivitiesCache.db")
    elif len(db_files) == 1:
        return str(db_files[0])
    elif len(db_files) > 1:
        print("\nMore than one ActivityCache.db files were found. Please select which one you wish to use. NOTE: If you are unsure, you can try them all until you find what you want!")
        i = 0
        while i < len(db_files):
            print('[' + str((i+1)) + ']', str(db_files[i]))
            i += 1
        hasChosen = False
        while not hasChosen:
            try: 
                choice = int(input("Choose 1,2,...: ")) - 1
                if choice > len(db_files) or choice <= 0:
                    continue
                hasChosen = True
                return str(db_files[choice])
            except: 
                continue
    else:
        print("There was a problem finding the file... ", db_files)
        exit()

# connect to database
def establish_connection():
    con = None
    try:
        con = sqlite3.connect(get_activities_cache_db_absolute_path())
    except:
        print("Error connecting to the database")
        exit()

    return con

# creates csv file containing all activities and their duration
# All activity durations for each applicatiion is aggregated
# some app names contain a guid/uuid in place of the folder path. i replaced these with their folder for readability
def app_usage_report(con):
    cur = con.cursor()
    cur.execute("SELECT AppId, EndTime, StartTime FROM ActivityOperation WHERE EndTime!=0 AND EndTime!=StartTime")
    rows = cur.fetchall()
    csv_data = "App name,Usage duration (seconds)"
    all_apps = {}
    for row in rows:
        duration = row[1] - row[2]
        app_name = str(json.loads(row[0])[0]["application"]) \
            .replace('{6D809377-6AF0-444B-8957-A3773F02200E}', "C:\Program Files", 1) \
            .replace('{7C5A40EF-A0FB-4BFC-874A-C0F2E0B9FA8E}', "C:\Program Files (x86)", 1) \
            .replace('{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}', "C:\Windows\System32", 1) \
            .replace('{D65231B0-B2F1-4857-A4CE-A8E7C6EA7D27}', "C:\Windows\System32", 1) \
            .replace('{F38BF404-1D43-42F2-9305-67DE0B28FC23}', "C:\Windows", 1)
        if not app_name in all_apps:
            all_apps[app_name] = 0
        all_apps[app_name] += duration
    all_apps = sorted(all_apps.items(), key=lambda item: item[1], reverse=True)
    index = 0
    while index < len(all_apps):
        app_name = str(all_apps[index][0])
        duration = str(all_apps[index][1])
        csv_data += "\n" + app_name + "," + duration
        index += 1
    with open('./user_activity_per_app.csv', 'w+') as app_usage_report_file:
        app_usage_report_file.write(csv_data)

# creates csv file containing all app launches and their parameters if applicable
# some app names contain a guid/uuid in place of the folder path. i replaced these with their folder for readability
def app_launch_times_and_params_report(con):
    cur = con.cursor()
    cur.execute("SELECT AppId, StartTime, Payload FROM ActivityOperation")
    rows = cur.fetchall()
    csv_data = "StartTime,AppName,DisplayName,DisplayText,TimeZone"
    for row in rows:
        app_name = str(json.loads(row[0])[0]["application"]) \
            .replace('{6D809377-6AF0-444B-8957-A3773F02200E}', "C:\Program Files", 1) \
            .replace('{7C5A40EF-A0FB-4BFC-874A-C0F2E0B9FA8E}', "C:\Program Files (x86)", 1) \
            .replace('{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}', "C:\Windows\System32", 1) \
            .replace('{D65231B0-B2F1-4857-A4CE-A8E7C6EA7D27}', "C:\Windows\System32", 1) \
            .replace('{F38BF404-1D43-42F2-9305-67DE0B28FC23}', "C:\Windows", 1)
        start_time = str(strftime('%Y-%m-%d %H:%M:%S', localtime(row[1])))
        payload = row[2].decode("utf-8")
        if payload[0] == '{':
            payload = json.loads(payload)
            try: display_name = payload["appDisplayName"] 
            except: display_name = ''
            try: display_text = payload["displayText"] 
            except: display_text = ''
            try: time_zone = payload["userTimezone"] 
            except: time_zone = ''
            csv_data += "\n" + start_time + "," + app_name + "," + display_name + "," + display_text + "," + time_zone
    with open('./app_launch_times_and_params.csv', 'w+') as app_launch_times_and_params_file:
        app_launch_times_and_params_file.write(csv_data)

# creates a pdf with the top 10 most used applications based on the user_activity_per_app.csv
def generate_top_10_apps_bar_chart_pdf():
    user_activity_data = None
    with open('./user_activity_per_app.csv', 'r') as app_usage_report_file:
        user_activity_data = pandas.read_csv(app_usage_report_file)
    # aggregate everything after first 10 to 'other'
    app_names = list(user_activity_data['App name'])[0:9]
    app_names.append("other")
    durations = list(user_activity_data['Usage duration (seconds)'])
    dur_index = 10
    total_other = 0
    while dur_index < len(durations):
        total_other += durations[dur_index] 
        dur_index += 1
    durations = durations[0:9]
    durations.append(total_other)
    # create bar chart from data
    df = pandas.DataFrame({'App name': app_names, 'Usage duration (seconds)': durations})
    df.plot.barh(y='Usage duration (seconds)', x='App name', figsize=(14.04, 8.3))
    plt.title('Top 10 Applications')
    plt.yticks(fontsize=10)
    plt.subplots_adjust(left=0.5, bottom=0.1, right=0.95, top=0.9, wspace=None, hspace=None)
    plt.savefig('Top10AppsBar.pdf')

# creates a pdf with the top 5 most used apps based on the user_activity_per_app.csv in a pie chart
def generate_top_5_apps_pie_chart_pdf():
    user_activity_data = None
    with open('./user_activity_per_app.csv', 'r') as app_usage_report_file:
        user_activity_data = pandas.read_csv(app_usage_report_file)
    # aggregate everything after first 10 to 'other'
    app_names = list(user_activity_data['App name'])[0:5]
    app_names.append("other")
    durations = list(user_activity_data['Usage duration (seconds)'])
    dur_index = 6
    total_other = 0
    while dur_index < len(durations):
        total_other += durations[dur_index] 
        dur_index += 1
    durations = durations[0:5]
    durations.append(total_other)
    # create bar chart from data
    fig, ax1 = plt.subplots()
    ax1.pie(durations, labels=app_names, autopct='%1.1f%%', textprops={'fontsize': 10.5})
    ax1.axis('equal')
    ax1.set_title('Top 5 Applications') 
    fig.set_size_inches(14.04, 8.3, forward=True)
    plt.subplots_adjust(left=0, bottom=0.1, right=0.95, top=0.9, wspace=None, hspace=None)
    plt.savefig('Top5AppsPie.pdf')

# merges the existing pdfs and deletes the individual ones
def merge_pdf_reports():
    pdfs = ['Top10AppsBar.pdf', 'Top5AppsPie.pdf']
    merger = PdfFileMerger()
    for pdf in pdfs:
        merger.append(pdf)
    merger.write("UsageReportFor" + str(environ['username']) + ".pdf")
    merger.close()
    for pdf in pdfs:
        remove(pdf)

def main():
    con = establish_connection()
    app_usage_report(con)
    app_launch_times_and_params_report(con)
    generate_top_10_apps_bar_chart_pdf()
    generate_top_5_apps_pie_chart_pdf()
    merge_pdf_reports()

main()
