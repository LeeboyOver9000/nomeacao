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
    [sg.Text('', key='saida')],
]

window = sg.Window('Busca Busca nome em arquivos pdfs', layout, element_justification='c')

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == 'Buscar':
        message = ''
        has_name, page_number = has_name_in_file(values['candidato'], values['path'])

        if not has_name:
            message = 'Infelizmente seu nome não foi encontrado no documento.'
        else:
            message = f'Opa! Seu nome foi encontrado na página {page_number} desse documento.'

        window['saida'].update(message)

window.close()
