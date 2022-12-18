import PySimpleGUI as sg


def trigger_reader(d_t, d_n):
    l_b = 0
    r_b = 0
    if d_t in d_n:
        text1 = d_n.split(d_t)[2]
        text2 = d_n.split(d_t)[0]
        trigger = ''
        for char in text1:
            if char == '{':
                l_b += 1
            if char == '}':
                r_b += 1
            if l_b != 0:
                if l_b > r_b:
                    trigger = trigger + char
                else:
                    trigger = trigger + char
                    break
        l_b = 0
        c = 0
        tag = ''
        for char in text2[::-1]:
            if char == '{':
                l_b += 1
            if l_b == 2:
                c += 1
                tag = tag + char
                if c == 7:
                    break
        return trigger[1::], tag[-1:-4:-1]


def static_template(s_t, d, c, c_l):
    if s_t[0] == '#':
        comment = '\n\t' + s_t.replace('VFM ', '') + '\n'
        return comment
    else:
        loc_tag = 'RU_CL_' + d + '_' + s_t
        if loc_tag in c_l:
            template = '\t\ttext = {\n\t\t\ttrigger = {\n\t\t\t\texists = c:' + s_t + \
                       '\n\t\t\t\tthis = c:' + s_t + '\n\t\t\t}\n\t\t\tlocalization_key = RU_CL_' \
                       + d + '_' + s_t + ' ' + c[d] + '\n\t\t}\n'
            return template


def dynamic_template(d_t, d, c, c_l, d_n):
    if d_t[0] == '#':
        comment = '\n\t' + d_t.replace('VFM ', '') + '\n'
        return comment
    else:
        loc_tag = 'RU_CL_' + d + '_' + d_t
        if loc_tag in c_l:
            try:
                trigger = trigger_reader(d_t, d_n)[0].replace('\n', '\n\t')
                tag = trigger_reader(d_t, d_n)[1]
                template = '\t\ttext = {\n\t\t\ttrigger = {\n\t\t\t\texists = c:' + \
                           tag + '\n\t\t\t\tthis = c:' + tag + '\n' \
                           + trigger + '\n\t\t\tlocalization_key = RU_CL_' + d + '_' + d_t + ' ' + c[d] + '\n\t\t}\n'
            except AttributeError:
                template = ''
            except TypeError:
                template = ''
            return template


sg.theme('LightBlue')
layout = [[sg.Text('Static Tag List'), sg.Input(), sg.FileBrowse(key='input_static_tags')],
          [sg.Text('Dynamic Tag List'), sg.Input(), sg.FileBrowse(key='input_dynamic_tags')],
          [sg.Text('Custom Tag Localization'), sg.Input(), sg.FileBrowse(key='custom_tag_loc_file')],
          [sg.Text('Dynamic Names File'), sg.Input(), sg.FileBrowse(key='dynamic_names_file')],
          [sg.Text('Custom Localization'), sg.Input(), sg.FileBrowse(key='custom_loc_file')],
          [sg.Button('Submit')]]

window = sg.Window('Vic3 Ru Loc Gen', layout)
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Submit':
        f1_path = values['input_static_tags']
        f2_path = values['input_dynamic_tags']
        f3_path = values['custom_tag_loc_file']
        f4_path = values['dynamic_names_file']
        f5_path = values['custom_loc_file']
        break
window.close()
try:
    static_tag_file = open(f1_path, 'r', encoding='utf-8')
    static_tag_array = static_tag_file.readlines()
    static_tag_file.close()
except FileNotFoundError:
    static_tag_array = ''
try:
    dynamic_tag_file = open(f2_path, 'r', encoding='utf-8')
    dynamic_tag_array = dynamic_tag_file.readlines()
    dynamic_tag_file.close()
except FileNotFoundError:
    dynamic_tag_array = ''
try:
    custom_tag_loc_file = open(f3_path, 'r', encoding='utf-8')
    custom_tag_loc = custom_tag_loc_file.read()
    custom_tag_loc_file.close()
except FileNotFoundError:
    custom_tag_loc = ''
try:
    dynamic_names_file = open(f4_path, 'r', encoding='utf-8')
    dynamic_names = dynamic_names_file.read()
    dynamic_names_file.close()
except FileNotFoundError:
    dynamic_names = ''
try:
    custom_loc_file = open(f5_path, 'r', encoding='utf-8')
    custom_loc = custom_loc_file.read()
    custom_loc_file.close()
except FileNotFoundError:
    custom_loc = 'def'
output_file = open('output.txt', 'w', encoding="utf-8")
static_tags = []
dynamic_tags = []
for line in static_tag_array[1::]:
    line = line.strip()
    if "_" not in line and line != '':
        static_tags.append(line.split(':')[0])
for line in dynamic_tag_array[1::]:
    line = line.strip()
    if "adj" not in line and line != '':
        dynamic_tags.append(line.split(':')[0])
declensions = ["RP", "DP", "VP", "TP", "PP"]
comments = {'RP': "# genitive", "DP": "# dative", "VP": "# accusative", "TP": "# instrumental",
            "PP": "# prepositional"}
for declension in declensions:
    output = ''
    for dynamic_tag in dynamic_tags:
        if dynamic_template(dynamic_tag, declension, comments, custom_tag_loc, dynamic_names) is not None:
            output = output + dynamic_template(dynamic_tag, declension, comments, custom_tag_loc, dynamic_names)
    for static_tag in static_tags:
        if static_template(static_tag, declension, comments, custom_tag_loc) is not None:
            output = output + static_template(static_tag, declension, comments, custom_tag_loc)
    default_tag = '\n\ttext = {\n\t\tlocalization_key = RU_CL_' + declension + '_DEFAULT'
    custom_loc = custom_loc.replace(default_tag, output + default_tag)
output_file.write(custom_loc)
output_file.close()
