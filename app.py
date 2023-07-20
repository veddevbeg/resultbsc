import csv
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from flask import Flask, request, render_template, send_file

app = Flask(__name__)

result_url = 'https://mcbu.ac.in/print_ugmarksheet.php'

def scrape_data(session, exam_name, roll_number):
    form_data = {
        'rtpe': 'Regular',
        'exam_session': session,
        'exam_name': exam_name,
        'rollno': str(roll_number)
    }

    response = requests.post(result_url, data=form_data)
    soup = BeautifulSoup(response.text, 'html.parser')

    error_message_element = soup.find(
        'h3',
        string='Sorry! This Roll Number could not be found or the result is incomplete')
    if error_message_element is not None:
        return None, None, None

    student_name_element = soup.find('td', string='Student Name')
    student_name = student_name_element.find_next('td').b.text.strip()

    marks_obtained_element = soup.find('td', string='Marks Obtained')
    total_marks_obtained = marks_obtained_element.find_next('td').b.text

    return student_name, int(total_marks_obtained), exam_name

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start = int(request.form['start'])
        end = int(request.form['end'])

        data = []
        total_roll_numbers = end - start + 1

        for roll_number in tqdm(range(start, end + 1), desc="Parsing Roll Numbers", unit=""):
            student_name_2023, marks_2023, exam_name_2023 = scrape_data('MAR-2023', 'B.SC.FINAL YEAR', roll_number)

            if student_name_2023 is None:
                continue

            student_name_2022, marks_2022, exam_name_2022 = scrape_data('MAR-2022', 'B.SC.SECOND YEAR', roll_number)
            student_name_2021, marks_2021, exam_name_2021 = scrape_data('MAR-2021', 'B.SC.FIRST YEAR', roll_number)

            total_marks = marks_2023 + marks_2022 + marks_2021

            data.append([roll_number, student_name_2023, marks_2023, marks_2022, marks_2021, total_marks])

        csv_file = "bsc_results.csv"
        header = ['Roll Number', 'Student Name', 'Marks Obtained (2023)', 'Marks Obtained (2022)', 'Marks Obtained (2021)', 'Total Marks']
        with open(csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data)

        return send_file(csv_file, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
