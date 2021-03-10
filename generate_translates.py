import os
import csv
import xml.etree.cElementTree as ET

csv_file = 'res/csv/translates.csv'


def parse_csv():
    if not os.path.exists(csv_file):
        print(f"{csv_file} don't exist")
        exit()

    ios = {}
    android = {}

    with open(csv_file) as f:
        parsed = list(csv.reader(f))

        head = parsed[0]

        languages = parsed[0][2:]
        for language in languages:
            ios[language] = {}
            android[language] = {}

        for t_data in parsed:
            if t_data == head:
                continue

            key_a = t_data[0]
            key_i = t_data[1]

            values = t_data[2:]
            for language in languages:
                value = values[languages.index(language)]

                if key_a != '':
                    android[language][key_a] = value
                if key_i != '':
                    ios[language][key_i] = value

    return android, ios


# android - { 'ua' : { 'key' : 'значення'... } ... }
def generate_android(android):
    output = 'output/generate/android'

    for language, items in android.items():
        root = ET.Element("resources")

        for key, value in items.items():
            ET.SubElement(root, "string", name=key).text = str(value)

        if language == 'en':
            res = 'values'
        else:
            res = f'values-{language}'

        file = 'strings.xml'
        res_output = f'{output}/{res}'
        if not os.path.exists(res_output):
            os.makedirs(res_output)

        file_path = f'{res_output}/{file}'
        if os.path.exists(file_path):
            os.remove(file_path)

        tree = ET.ElementTree(root)
        tree.write(file_path, encoding="UTF-8")


# ios - { 'ua' : { 'key' : 'значення'... } ... }
def generate_ios(ios):
    output = 'output/generate/ios/'

    for language, items in ios.items():
        # root = ET.Element("resources")
        file = 'Localizable.strings'
        res_output = f'{output}/{language}'
        if not os.path.exists(res_output):
            os.makedirs(res_output)

        file_path = f'{res_output}/{file}'
        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, "w") as file:
            for key, value in items.items():
                file.write(f"\"{key}\" = \"{value}\";\n")
        # if language == 'en':
        #     res = 'values'
        # else:
        #     res = f'{language}'

        # tree = ET.ElementTree(root)
        # tree.write(file_path, encoding="UTF-8")


def main():
    android, ios = parse_csv()

    generate_android(android)
    generate_ios(ios)


if __name__ == '__main__':
    main()
