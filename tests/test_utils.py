from app.utils import normalize_name


def test_normalize_name():
    input_text = 'Atenção Exceção Impressão Concessão Presunção Você Purê Crochê Metrô Plástico Gráfico Espécie Célebre Àquelas às à Açúcar AÇÚCAR CABEÇA CAROÇO áàãâä ÁÀÂÂÄ Ç'
    expected_text = 'ATENCAO EXCECAO IMPRESSAO CONCESSAO PRESUNCAO VOCE PURE CROCHE METRO PLASTICO GRAFICO ESPECIE CELEBRE AQUELAS AS A ACUCAR ACUCAR CABECA CAROCO AAAAA AAAAA C'
    result = normalize_name(input_text)
    assert result == expected_text
