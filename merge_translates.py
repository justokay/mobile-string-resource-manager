import xml.etree.ElementTree as ET
import csv
import os
import shutil
import difflib

placeholders = ["%d", "%s", "%@", "%ld", "%1$s", "%2$s",
                "%3$s", "%4$s", "%1$d", "%2$d", "%3$d", "%4$d"]

# max log lenght
max_len = 120

ios_project_path = "/Users/jo/dev/ios/project/allright-ios-app"
android_project_path = "/Users/jo/dev/android/project/allright-android-app"

ios_res = 'res/ios'
android_res = 'res/android'

output = 'output'


def main():
    copy_android_data_from_project()
    copy_ios_data_from_project()

    android_files = os.listdir(android_res)
    ios_files = os.listdir(ios_res)

    android_languages = []
    ios_languages = []

    # find android languages
    for file in android_files:
        android_languages.append(file.split('.')[0])

    # find ios languages
    for file in ios_files:
        ios_languages.append(file.split('.')[0])

    android_result = {}
    ios_result = {}

    # print_separate_log('fill android data')
    for language in android_languages:
        file_name = f'{android_res}/{language}.xml'

        android_result[language] = parse_android(ET.parse(file_name).findall('string'), )

    # print_separate_log('fill ios data')
    for language in ios_languages:
        ios_result[language] = parse_ios(f'{ios_res}/{language}.strings')

    print_separate_log('merge translates')

    # print_separate_log('ios duplicates')
    # find_duplicates(ios_result['ru'], 'ru')
    # find_duplicates(ios_result['en'], 'en')
    #
    # print_separate_log('android duplicates')
    # find_duplicates(android_result['ru'], 'ru')
    # find_duplicates(android_result['en'], 'en')

    locale = 'ru'

    android = android_result[locale]
    ios = ios_result[locale]

    merged_result = process_translates(android, ios)

    print_separate_log('end merge translates')

    # prepare data to generate csv
    generate_csv(android_languages, merged_result, android_result, ios_result)


# copy android res files from project to android dictionary
def copy_android_data_from_project():
    android_res_folder = f'{android_project_path}/core/src/main/res'
    res_folder = os.listdir(android_res_folder)
    res_file = 'strings.xml'

    dst = ''
    src = ''

    for folder in res_folder:
        if folder == 'values':
            dst = 'en.xml'
            src = f'{android_res_folder}/{folder}/{res_file}'
        else:
            if 'values-' in folder:
                _split = folder.split('-')

                if len(_split) < 2:
                    continue

                dst = f'{_split[1]}.xml'
                src = f'{android_res_folder}/{folder}/{res_file}'

        if len(dst) == 0 or len(src) == 0:
            continue

        if os.path.exists(src):
            _dst = f'{android_res}/{dst}'

            if not os.path.exists(android_res):
                os.makedirs(android_res)

            if os.path.exists(_dst):
                os.remove(_dst)
            shutil.copy(src, _dst)

            dst = ''
            src = ''


# copy iOS res files from project to iOS dictionary
def copy_ios_data_from_project():
    ios_res_folder = f'{ios_project_path}/Allright/Resources'
    res_folder = os.listdir(ios_res_folder)
    res_file = 'Localizable.strings'

    dst = ''
    src = ''

    for folder in res_folder:
        if '.lproj' in folder:
            key = folder.split('.')[0]

            dst = f'{key}.strings'
            src = f'{ios_res_folder}/{folder}/{res_file}'

        if len(dst) == 0 or len(src) == 0:
            continue

        if os.path.exists(src):
            _dst = f'{ios_res}/{dst}'

            if not os.path.exists(ios_res):
                os.makedirs(ios_res)

            if os.path.exists(_dst):
                os.remove(_dst)

            shutil.copy(src, _dst)

            dst = ''
            src = ''


# data - Element string list
# return dictionary to with { 'translate_key' : 'translate' }
def parse_android(data):
    language_dict = {}
    for item in data:
        if 'translatable' not in item.attrib or item.attrib['translatable'] == 'true':
            value = item.text.strip()
            if value[0] == "\"" and value[-1] == "\"":
                value = value[1:-1]
            language_dict[item.attrib['name']] = value.strip()
    return language_dict


# file_name - .strins file in res/iOS folder
# return dictionary to with { 'translate_key' : 'translate' }
def parse_ios(file_name):
    language_dict = {}
    with open(file_name) as fp:
        line = fp.readline()
        while line:
            if ' = ' in line:
                key, value = line.strip().split(' = ')

                _key = key.strip()[1:-1].strip()
                strip_value = value.strip()
                if len(strip_value) > 0 and strip_value[-1] != ';':
                    strip_value = strip_value.split(';')[0][1:-1]
                else:
                    strip_value = strip_value[1:-2]
                _value = strip_value.strip()

                language_dict[_key] = _value
            line = fp.readline()
    return language_dict


# create .csv file
# file_name - path of .csv file
# head - list of column names: ['mobile_key', 'ru', 'en'....]
# rows - list of dictionaries: {['mobile_key':'fucking_key', 'ru':'продолжить', 'en':'continue'...]...}
def generate_csv_file(file_name, head, rows):
    with open(file_name, 'w') as f:
        w = csv.DictWriter(f, head)
        w.writeheader()
        w.writerows(rows)


# custom log
def print_separate_log(message=''):
    message_len = len(message)
    if message_len > 0:
        print(message + '-' * (max_len - message_len))
    else:
        print('-' * max_len)


def remove_spec_symbols(value):
    # for pl in placeholders:
    #     if pl in value:
    #         value = value.replace(pl, "%s")
    #     if len(value) > 0 and value[-1] == ".":
    #         value = value[:-1]
    #
    # value = value.replace("\\n", "")
    value = value.replace('–', '-')
    # value = value.replace('\\', '')
    value = value.replace('«', "\"")
    value = value.replace('»', "\"")
    return value


# split translates to general = 0, android only = 1, ios only = 2


# split android and ios translates data to 3 lists
# first with general translates for both os: ['android_key', 'ios_key', 'value']
# second with only android translates: ['key', 'value']
# third with only ios translates: ['key', 'value']
#
# return - list of list ['general, 'android_only', 'ios_only']
def split_translates(android, ios):
    _android = {}
    _ios = {}

    # replace placeholders
    for key, value in android.items():
        _android[key] = remove_spec_symbols(value).lower()

    # replace placeholders
    for key, value in ios.items():
        _ios[key] = remove_spec_symbols(value).lower()

    keys = []
    same_translates = []
    android_translates = []
    ios_translates = []

    keys.append(same_translates)
    keys.append(android_translates)
    keys.append(ios_translates)

    for k, v in _android.items():
        ios_data = list(_ios.values())
        ios_keys = list(_ios.keys())

        if v in ios_data:
            key = ios_keys[ios_data.index(v)]
            same_translates.append([k, key, v])
        else:
            # ratio = difflib.SequenceMatcher(None, 'hello world', 'hello').ratio()
            android_translates.append([k, v])

    for k, v in _ios.items():
        if v not in _android.values():
            ios_translates.append([k, v])

    return keys


# android - dict: {'key':'value'}
# ios - dict: {'key':'value'}
#
# return - list of list ['general, 'android_only', 'ios_only']
def process_translates(android, ios):
    print(f'found android resources {len(android)}')
    print(f'found ios resources {len(ios)}')

    merge_result = split_translates(android, ios)
    android_translates = merge_result[1]
    ios_translates = merge_result[2]
    general_translates = merge_result[0]

    print(f'same translates {len(general_translates)}')
    print(f'only android translates {len(android_translates)}')
    print(f'only ios translates {len(ios_translates)}')

    write_output('android_only.txt', android_translates)
    write_output('ios_only.txt', ios_translates)
    write_output('general.txt', general_translates)

    return merge_result


# write processed translates data to file
# translates - dict: {'key':'value'}
def write_output(file_name, translates):
    path = f'{output}/{file_name}'

    if os.path.exists(path):
        os.remove(path)

    if not os.path.exists(output):
        os.mkdir(output)

    with open(f'{output}/{file_name}', 'w') as f:
        for item in list(sorted(translates, key=lambda item: item[1])):
            f.write(str(item) + '\n')


# languages = [ 'en', 'ru, ... ]
# android_dict - { 'en' : { 'key' : 'value' }, ... }
# ios_dict - { 'en' : { 'key' : 'value' }, ... }
# merged_data result from, split_translates method
def generate_csv(languages, merged_data, android_dict, ios_dict):
    a_k = 'android_key'
    i_key = 'ios_key'
    head = [a_k, i_key]
    # [{'a_key':'key', 'ios_key':'key', 'en':'value', 'ua':'значення'},...]
    rows = []

    # add language rows
    for language in languages:
        head.append(language)

    # fill general translates
    for item in merged_data[0]:
        _android_key = item[0]
        _ios_key = item[1]
        row = {a_k: _android_key, i_key: _ios_key}

        for language in languages:
            if _android_key in android_dict[language]:
                row[language] = android_dict[language][_android_key]
            else:
                row[language] = ''

        rows.append(row)

    # separate general translates
    empty_row = {}
    for item in head:
        empty_row[item] = ''

    rows.append(empty_row)
    # fill only android translates
    for item in merged_data[1]:
        _android_key = item[0]
        _ios_key = ''
        row = {a_k: _android_key, i_key: _ios_key}

        for language in languages:
            if _android_key in android_dict[language]:
                row[language] = android_dict[language][_android_key]
            else:
                row[language] = ''

        rows.append(row)

    rows.append(empty_row)
    # fill only ios translates
    for item in merged_data[2]:
        _android_key = ''
        _ios_key = item[0]
        row = {a_k: _android_key, i_key: _ios_key}

        for language in languages:
            if _ios_key in ios_dict[language]:
                row[language] = ios_dict[language][_ios_key]
            else:
                row[language] = ''

        rows.append(row)

    # for item in android_dict['en']:
    #     row = {a_k: item}
    #
    #     for language in languages:
    #         if item in android_dict[language]:
    #             row[language] = android_dict[language][item]
    #         else:
    #             row[language] = ''
    #
    #     rows.append(row)

    translate_file = f'{output}/translates.csv'

    if os.path.exists(translate_file):
        os.remove(translate_file)

    generate_csv_file(translate_file, head, rows)


# language_dict - {'translate_key':'translate'}
# locale - language code 'en'
def find_duplicates(language_dict, locale):
    seen = {}
    for k, v in language_dict.items():
        if v in seen:
            seen[v].append(k)
        else:
            seen[v] = [k]

    duplicates = {}
    for k, v in seen.items():
        if len(v) > 1:
            duplicates[k] = v

    print_separate_log(f"duplicates({locale}) {len(duplicates)}")
    for k, v in duplicates.items():
        print(f'{k}={v}')
    # print(duplicates)
    print_separate_log()


if __name__ == "__main__":
    main()
