from datetime import date


# Function accept a date or a int
def get_month_name(month_data: date or int) -> str:
    """
    Get the month name in portuguese
    :param month_data: date or int - date to get the month name or the month number
    :return: str - month name in portuguese
    """

    month_number = month_data.month if isinstance(month_data, date) else month_data

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

    return months_in_portuguese[month_number]
