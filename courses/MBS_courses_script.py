"""Description:
    * author: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technology
    * position: IT Intern
    * date: 03-11-20
    * description:This script extracts the corresponding undergraduate courses details and tabulate it.
"""

import csv
import re
import time
from pathlib import Path
from selenium import webdriver
import bs4 as bs4
import os
import copy
from CustomMethods import TemplateData
from CustomMethods import DurationConverter as dura

option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# read the url from each file into a list
course_links_file_path = Path(os.getcwd().replace('\\', '/'))
course_links_file_path = course_links_file_path.__str__() + '/MBS_courses_links.txt'
course_links_file = open(course_links_file_path, 'r')

# the csv file we'll be saving the courses to
csv_file_path = Path(os.getcwd().replace('\\', '/'))
csv_file = csv_file_path.__str__() + '/MBS_courses.csv'

course_data = {'Level_Code': '', 'University': 'Melbourne Business School', 'City': '',
               'Country': 'Australia', 'Course': '', 'Int_Fees': '', 'Local_Fees': '', 'Currency': 'AUD',
               'Currency_Time': 'year', 'Duration': '', 'Duration_Time': '', 'Full_Time': '', 'Part_Time': '',
               'Prerequisite_1': 'IELTS', 'Prerequisite_2': '', 'Prerequisite_3': '', 'Prerequisite_1_grade': '6.5',
               'Prerequisite_2_grade': '', 'Prerequisite_3_grade': '', 'Website': '', 'Course_Lang': '',
               'Availability': 'A', 'Description': '','Career_Outcomes': '', 'Online': 'no', 'Offline': 'yes',
               'Distance': 'no', 'Face_to_Face': 'yes', 'Blended': 'no', 'Remarks': ''}

possible_cities = {'online': 'Online', 'mixed': 'Online', 'carlton': 'Carlton'}

possible_languages = {'Japanese': 'Japanese', 'French': 'French', 'Italian': 'Italian', 'Korean': 'Korean',
                      'Indonesian': 'Indonesian', 'Chinese': 'Chinese', 'Spanish': 'Spanish'}

course_data_all = []
level_key = TemplateData.level_key  # dictionary of course levels
faculty_key = TemplateData.faculty_key  # dictionary of course levels

# GET EACH COURSE LINK
for each_url in course_links_file:
    actual_cities = []
    remarks_list = []
    browser.get(each_url)
    pure_url = each_url.strip()
    each_url = browser.page_source

    soup = bs4.BeautifulSoup(each_url, 'lxml')
    time.sleep(1)

    # SAVE COURSE URL
    course_data['Website'] = pure_url

    # SAVE COURSE TITLE
    title_tag = soup.find('div', class_='page-title')
    if title_tag:
        title = title_tag.find('h2')
        if title:
            title_text = title.get_text().lower().strip()
            if 'online' in title_text:
                actual_cities.append('online')
                course_data['Online'] = 'yes'
                course_data['Face_to_Face'] = 'no'
                course_data['Offline'] = 'no'
            if 'part-time' in title_text:
                course_data['Part_Time'] = 'yes'
                course_data['Full_Time'] = 'no'
            else:
                course_data['Full_Time'] = 'yes'
                course_data['Part_Time'] = 'no'
            course_data['Course'] = title.get_text().strip()
            print('COURSE TITLE: ', course_data['Course'])
        description = title_tag.find('p', class_='page-subtext')
        if description:
            course_data['Description'] = description.get_text().strip()
            print('COURSE DESCRIPTION: ', course_data['Description'])

        # DECIDE THE LEVEL CODE
        for i in level_key:
            for j in level_key[i]:
                if j in course_data['Course']:
                    course_data['Level_Code'] = i
        print('COURSE LEVEL CODE: ', course_data['Level_Code'])

        # DECIDE THE FACULTY
        for i in faculty_key:
            for j in faculty_key[i]:
                if j.lower() in course_data['Course'].lower():
                    course_data['Faculty'] = i
        print('COURSE FACULTY: ', course_data['Faculty'])

        # COURSE LANGUAGE
        for language in possible_languages:
            if language in course_data['Course']:
                course_data['Course_Lang'] = language
            else:
                course_data['Course_Lang'] = 'English'
        print('COURSE LANGUAGE: ', course_data['Course_Lang'])

    # CITY
    actual_cities.append('carlton')

    # DURATION
    dura_tag = soup.find('div', class_='page-details')
    if dura_tag:
        details_list = dura_tag.find_all('div', class_='course-detail')
        if details_list:
            for i, duration in enumerate(details_list):
                if i == 2:
                    dura_ = duration.find('a')
                    dura_text = dura_.get_text().strip()
                    converted_dura = dura.convert_duration(dura_text)
                    if converted_dura is not None:
                        duration_l = list(converted_dura)
                        if duration_l[0] == 1 and 'Years' in duration_l[1]:
                            duration_l[1] = 'Year'
                        if duration_l[0] == 1 and 'Months' in duration_l[1]:
                            duration_l[1] = 'Month'
                        course_data['Duration'] = duration_l[0]
                        course_data['Duration_Time'] = duration_l[1]
                        print('COURSE DURATION: ', str(duration_l[0]) + ' / ' + duration_l[1])

    # duplicating entries with multiple cities for each city
    for i in actual_cities:
        course_data['City'] = possible_cities[i]
        course_data_all.append(copy.deepcopy(course_data))
    del actual_cities

    # TABULATE THE DATA
    desired_order_list = ['Level_Code', 'University', 'City', 'Course', 'Faculty', 'Int_Fees', 'Local_Fees',
                          'Currency', 'Currency_Time', 'Duration', 'Duration_Time', 'Full_Time', 'Part_Time',
                          'Prerequisite_1', 'Prerequisite_2', 'Prerequisite_3', 'Prerequisite_1_grade',
                          'Prerequisite_2_grade', 'Prerequisite_3_grade', 'Website', 'Course_Lang', 'Availability',
                          'Description', 'Career_Outcomes', 'Country', 'Online', 'Offline', 'Distance',
                          'Face_to_Face', 'Blended', 'Remarks']

    course_dict_keys = set().union(*(d.keys() for d in course_data_all))

    with open(csv_file, 'w', encoding='utf-8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, course_dict_keys)
        dict_writer.writeheader()
        dict_writer.writerows(course_data_all)

    with open(csv_file, 'r', encoding='utf-8') as infile, open('MBS_courses_ordered.csv', 'w', encoding='utf-8',
                                                               newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=desired_order_list)
        # reorder the header first
        writer.writeheader()
        for row in csv.DictReader(infile):
            # writes the reordered rows to the new file
            writer.writerow(row)
