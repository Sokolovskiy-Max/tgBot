import csv

age = 18
alko = ['пиво', 'Пиво', 'вино', 'Вино', 'коньяк', 'Коньяк', 'водка', 'Водка', 'виски', 'Виски', 'джин', 'Джин', 'Текила', 'текила']


def extract_alko(file_name):
    raw_data = []
    with open(file_name, encoding='utf-16') as r_file:
        file_reader = csv.reader(r_file, delimiter="\t")
        count = -1
        for row in file_reader:
            raw_data.append(row)
            count += 1
    with open(file_name, 'w', encoding='utf16', newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        for line in raw_data:
            if not (any(i in line[0] for i in alko)):
                writer.writerows([line])


def delete_alko(file_name):
    raw_data = []
    with open(file_name, encoding='utf-16') as r_file:
        file_reader = csv.reader(r_file, delimiter="\t")
        count = -1
        for row in file_reader:
            raw_data.append(row)
            count += 1
    with open(file_name, 'w', encoding='utf16', newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        for line in raw_data:
            if any(i in line[0] for i in alko):
                writer.writerows([line])
