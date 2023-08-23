from datetime import date


# Function accept a date or a int
def mes_em_portugues(mes_data: date or int) -> str:
    """
    Retorna o nome do mês em português
    :param mes_data: date or int - data ou número do mês (1-12)
    :return: str - month name in portuguese
    """

    month_number = mes_data.month if isinstance(mes_data, date) else mes_data

    months_in_portuguese = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }

    return months_in_portuguese.get(month_number, "Mês inválido")
