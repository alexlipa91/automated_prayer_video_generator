import datetime


def get_date_string(date: datetime.date, with_year: bool = True):
    months = {
        1: "Gennaio",
        2: "Febbraio",
        3: "Marzo",
        4: "Aprile",
        5: "Maggio",
        6: "Giugno",
        7: "Luglio",
        8: "Agosto",
        9: "Settembre",
        10: "Ottobre",
        11: "Novembre",
        12: "Dicembre"
    }
    res = f"{date.day} {months[date.month]}"
    if with_year:
        res += f" {date.year}"
    return res
