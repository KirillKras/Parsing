import pandas as pd


def load_datasets():
    opendata = pd.read_csv('opendata.csv', encoding='cp1251')
    datasets = {}
    for value in opendata.name.unique():
        datasets[value] = opendata[opendata.name == value]
        datasets[value].drop(columns='name', inplace=True)
    return datasets



if __name__ == '__main__':
    ds = load_datasets()
    k = [{'label': s, 'value': s} for s in ds['Количество заявок на потребительские кредиты'].region.unique()]
    pass
