from pathlib import Path
import PySimpleGUI as sg
from utils import has_name_in_file

layout = [
    [sg.Text('Nome do candidato: '), sg.InputText(key='candidato')],
    [
        sg.FileBrowse('Arquivo', file_types=(('Documents File', '.pdf'),),
            initial_folder=Path().home(),
        ),
        sg.InputText(key='path', enable_events=True, readonly=True),
    ],
    [sg.Button('Buscar')],
]

window = sg.Window('Busca Busca nome em arquivos pdfs', layout)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == 'Buscar':
        has_name, page_number = has_name_in_file(values['candidato'], values['path'])
        if not has_name:
            message = 'Infelizmente seu nome não foi encontrado no documento.'
            print(message)
        else:
            message = f'Opa! Seu nome foi encontrado na página {page_number} desse documento.'
            print(message)

window.close()
