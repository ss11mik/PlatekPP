# Platek++;
#  Individuální statistiky stravování v menzách VUT.
# autor: ss11mik
# 2025

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import datetime as dt
import os
import sys



def filter_matching_descr(dataset, filter_list, negative=False):
    if negative:
        return dataset.loc[~dataset["Description"].str.lower().str.contains('|'.join(filter_list).lower())]
    else:
        return dataset.loc[dataset["Description"].str.lower().str.contains('|'.join(filter_list).lower())]


def filter_payments(dataset):
    return dataset.loc[dataset["Type"] == "Payment"]


def save(plt, filename):
    plt.savefig(os.path.join('out', filename), bbox_inches='tight')


def parse(dataset, seznam, replace=True):
    x = dataset.loc[dataset.str.lower().str.contains('|'.join(seznam).lower())]

    if replace:
        for elem in seznam:
            x.loc[x.str.lower().str.contains(elem.lower())] = elem

    labels, counts = np.unique(x, return_counts=True)
    count_sort_ind = np.argsort(counts)

    return labels[count_sort_ind], counts[count_sort_ind]


def parse_dny(dataset):
    dataset = filter_payments(dataset)
    dataset = filter_matching_descr(dataset, seznam_nejidel, negative=True)
    # nechat jen informaci o tydnu
    dataset = pd.to_datetime(dataset['Billed'], format='%m/%d/%Y').dt.strftime("%A")
    dataset = pd.Categorical(dataset, categories=dny_v_tydnu, ordered=True)
    dataset = dataset.sort_values()
    return dataset


def parse_casy(dataset):
    dataset = filter_payments(dataset)
    dataset = filter_matching_descr(dataset, seznam_nejidel, negative=True)
    return pd.to_datetime(dataset['Submitted at'], format='%I:%M %p')


def parse_casy_v_tydnu(dataset):
    dataset = filter_payments(dataset)
    dataset = filter_matching_descr(dataset, seznam_nejidel, negative=True)
    casy_dnu = []
    for day in dny_v_tydnu:
        x = dataset.loc[pd.to_datetime(dataset['Billed'], format='%m/%d/%Y').dt.strftime("%A") == day]
        casy_dnu += [(pd.to_datetime(x['Submitted at'], format='%I:%M %p')).to_list()]
    return casy_dnu


def parse_tydny(dataset):
    dataset = filter_matching_descr(dataset, seznam_jidel)
    dataset = pd.to_datetime(dataset['Billed'], format='%m/%d/%Y')

    # time between first and last item in dataset, in years
    time_span = (dataset.max() - dataset.min()).days / 365.25

    dataset = dataset.dt.strftime("%U")
    labels, counts = np.unique(dataset, return_counts=True)
    labels = labels.astype(int)

    return labels, counts / time_span


def parse_inflace(dataset, polozka):
    dataset = filter_matching_descr(dataset, [polozka])

    cena = dataset.loc[:, "Payments"]
    datum = dataset.loc[:, "Billed"]
    datum = [dt.datetime.strptime(d,'%m/%d/%Y').date() for d in datum]

    return cena, datum


def parse_vydaje(dataset):
    dataset = filter_payments(dataset)
    ubytovani     = filter_matching_descr(dataset, ["Ubytování"])
    kolejnet      = filter_matching_descr(dataset, ["Služba CVIS", "internet"])
    tisk          = filter_matching_descr(dataset, ["Print", "Tisky a kopie"])
    prani         = filter_matching_descr(dataset, ["Praní", "Sušení"])
    menza_hlavni  = filter_matching_descr(dataset, seznam_nejidel + seznam_priloh + seznam_dezertu + seznam_napoju, negative=True)
    menza_prilohy = filter_matching_descr(dataset, seznam_priloh + seznam_dezertu + seznam_napoju)


    return menza_hlavni["Payments"], menza_prilohy["Payments"], ubytovani["Payments"], kolejnet["Payments"], tisk["Payments"], prani["Payments"]


def parse_balance(data):
    end_date = dt.datetime.strptime(data['Deposited'][0], "%m/%d/%Y")
    start_date = dt.datetime.strptime(data['Deposited'][len(data)-1], "%m/%d/%Y")
    date_list = pd.date_range(start_date, end_date, freq='D')

    input_dates = pd.to_datetime(data['Deposited'])
    balance = []
    for date in date_list:
        for i in reversed(range(len(input_dates))):
            if input_dates[i] >= date:
                balance.append(data['Balance'][i])
                break

    return date_list, balance



seznam_jidel = [
    "Guláš",
    "Těstoviny",    # TODO Penne
    "Plátek",
    "Steak",
    "Závitek",
    "Halušky",
    "Nudle",
    "Čočka",
    "Fazole",
    "Filé",
    "Nudličky",
    "Kaše",         # TODO ne bramborova
    "Směs",
    "Smažený sýr",
    "Menu",
    "Palačinky",
    "Pizza",
    "Polévka",
    "Gyros",
    "Rizoto",
    "Nákyp",
    "Salát",
    "Řízek",
    "Špagety",
    "Játra",
    "Kotleta",
    "Sójové maso",
    "Kapsa",
    "Kung Pao",
    "Lívance",
    "Perkelt",
    "Žemlovka",
    "Kynuté knedlíky",
    "Tvarohové knedlíky",
    "Alpský knedlík",
    "Flamendr",
    "Čevapčiči",
    "Paella",
    "Hradní dlabanec",
    "Tortilla",
    "Špíz",
    "Bramborák",
    "Květák",
    "Žebra",
    "Ražniči"
]

seznam_nejidel = [
    "platba",
    "SafeQ",
    "převod",
    "ubytování",
    "hotovost",
    "penále",
    "praní",
    "Sušení",
    "internet",
    "print",
    "Tisky a kopie",
    "sleva",
    "služba",
    "vklad",
    "Krabice na pizzu",
    "Obal pod pizzu",
    "Obal"
]

seznam_priloh = [
    "Brambory americké",
    "Brambory maštěné máslem",
    "Brambory opečené",
    "Brambory vařené",
    "Brambory šťouchané",
    "Bramborová kaše",
    "Bramboráčky 4ks",
    "Rýže Jasmínová",
    "Hranolky",
    "Knedlíky houskové",
    "Těstoviny M"           # " M" pro odliseni od hlavnich jidlel napr. "Těstoviny po italsku"
]

seznam_dezertu = [
    "Dort malakov",
    "Dort Sacher 70g",
    "Dort pohádka",
    "Kostka ovocná s tvarohem",
    "Větrník střední",
    "Dezert Panna Cotta",
    "Dort jogurtový 60g",
    "Věneček žloutkový",
    "Roláda čokoládová 60g",
    "Kostka jahodová 50g",
    "Pudink s ovocem a šlehačkou"
]

seznam_napoju = [
    "Rajec 0,75l",
    "Post Kofola 0,3l",
    "Post Kofola 0,5l",
    "MY Tea 0,5l"
]

seznam_mas = [
    "Kuře",     # match "Kuře na" / "Kuřecí" / ...
    "Vepř",     # match "Vepřové" / "Vepřový" / ...
    "Hovězí",
    "Krůtí",
    "Rybí",         # TODO druhy ryb
    "Dančí",
    "Kančí",
    "Klokan",
    "Sójové",
    "Krkovička",    # TODO započítat do vepřového
    "Robi",
    "Kachna",
    "Losos"
]

dny_v_tydnu = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
dny_v_tydnu_cs = ['pondělí', 'úterý', 'středa', 'čtvrtek', 'pátek']



if __name__ == '__main__':
    #
    # load data
    #
    data = pd.read_excel(sys.argv[1])
    popisy = data.loc[:, "Description"]
    os.makedirs('out', exist_ok=True)


    #
    # parse data
    #
    masa, masa_counts = parse(popisy, seznam_mas)
    jidla, jidla_counts = parse(popisy, seznam_jidel)
    platky, platky_counts = parse(popisy, ["plátek"], replace=False)
    steaky, steaky_counts = parse(popisy, ["steak"], replace=False)
    pizzy, pizzy_counts = parse(popisy, ["pizza"], replace=False)
    polevky, polevky_counts = parse(popisy, ["Polévka"], replace=False)
    dezerty, dezerty_counts = parse(popisy, seznam_dezertu, replace=False)
    prilohy, prilohy_counts = parse(popisy, seznam_priloh)
    casy = parse_casy(data)
    dny = parse_dny(data)
    tydny, tydny_counts = parse_tydny(data)
    casy_v_tydnu = parse_casy_v_tydnu(data)


    #
    # display data
    #
    fig, ax = plt.subplots()
    plt.barh(jidla, jidla_counts)
    plt.title("Druh jídla")
    save(plt, 'jidla.png')


    fig, ax = plt.subplots()
    ax.pie(masa_counts, labels=masa)
    plt.title("Druh masa v hlavním jídle")
    save(plt, 'masa.png')


    fig, ax = plt.subplots()
    ax.pie(prilohy_counts, labels=prilohy)
    plt.title("Přílohy")
    save(plt, 'prilohy.png')


    pd.DataFrame({"Pocet": platky_counts, "Druh platku": platky}).sort_values(by=['Pocet'], ascending=False).to_csv(os.path.join('out', 'platky.csv'), index=None, sep=' ')


    pd.DataFrame({"Pocet": steaky_counts, "Druh steaku": steaky}).sort_values(by=['Pocet'], ascending=False).to_csv(os.path.join('out', 'steaky.csv'), index=None, sep=' ')


    pd.DataFrame({"Pocet": pizzy_counts, "Druh pizzy": pizzy}).sort_values(by=['Pocet'], ascending=False).to_csv(os.path.join('out', 'pizzy.csv'), index=None, sep=' ')


    pd.DataFrame({"Pocet": polevky_counts, "Druh polévky": polevky}).sort_values(by=['Pocet'], ascending=False).to_csv(os.path.join('out', 'polevky.csv'), index=None, sep=' ')

    pd.DataFrame({"Pocet": dezerty_counts, "Druh dezertu": dezerty}).sort_values(by=['Pocet'], ascending=False).to_csv(os.path.join('out', 'dezerty.csv'), index=None, sep=' ')


    fig, ax = plt.subplots()
    plt.ylabel("počet jídel")
    plt.xlabel("čas")
    plt.title("Čas zaplacení jídla")
    xformatter = mdates.DateFormatter('%H:%M')
    plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)
    plt.hist(casy, bins=128)
    save(plt, 'casy.png')


    fig, ax = plt.subplots()
    plt.ylabel("počet jídel")
    plt.title("Jídla dle dnů v týdnu")
    plt.bar(dny_v_tydnu_cs, dny.value_counts().values, width=0.5)
    save(plt, 'dny.png')


    fig, ax = plt.subplots()
    plt.ylabel("průměrný počet jídel")
    plt.xlabel("kalendářní týden")
    plt.title("Jídla dle týdnů")
    plt.bar(tydny, tydny_counts)
    ax.axhline(tydny_counts.mean(), color='green')
    save(plt, 'tydny.png')


    fig, ax = plt.subplots()
    plt.ylabel("Kč")
    plt.xlabel("čas")
    plt.title("Inflace cen příloh")
    for priloha in seznam_priloh:
        cena, datum = parse_inflace(data, priloha)
        plt.plot(datum, cena, label=priloha)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    save(plt, 'inflace.png')


    plt.subplots()
    (n, bins, _) = plt.hist(casy_v_tydnu, bins=40)
    plt.close()
    fig, ax = plt.subplots()
    bins = mdates.num2date(bins)
    range_len = max(bins) - min(bins)
    hours = pd.date_range('1900-01-01 00:00:00', '1900-01-01 23:00:00', freq='1h', tz=bins[0].tzinfo)
    tick_locations = []
    tick_labels = []
    for i in range(len(hours)):
        tick = (hours[i] - min(bins)) / range_len
        if tick >= 0 and tick <= 1:
            tick *= len(bins)
            tick_locations.append(tick)
            # tick_labels.append("{}:00".format(hours[i].hour))
            tick_labels.append("{}:00".format(i))

    ax.set_xticks(tick_locations, labels=tick_labels)
    ax.set_yticks(np.arange(len(dny_v_tydnu_cs)), labels=dny_v_tydnu_cs)
    ax.imshow(n)
    plt.xlabel("čas")
    plt.title("Čas placení pro jednotlivé dny v týdnu")
    save(plt, 'casy_v_tydnu.png')


    vydaje = parse_vydaje(data)
    sumy_vydaju = [vydaj.sum() for vydaj in vydaje]
    celkova_suma_vydaju = sum(sumy_vydaju)
    fig, ax = plt.subplots()
    plt.title("Výdaje z ISKAM účtu")
    labels = ['{} - {:,.0f} Kč'.format(i, j) for i, j in zip(['hlavní jídla', 'přílohy', 'ubytování', 'KolejNet', 'tisk', 'praní'], sumy_vydaju)]
    patches, texts = ax.pie(sumy_vydaju)
    plt.legend(patches, labels)
    save(plt, 'vydaje.png')


    date_list, balance = parse_balance(data)
    fig, ax = plt.subplots()
    plt.ylabel("Zůstatek na kontě")
    plt.xlabel("čas")
    plt.title("Zůstatek na kontě [Kč]")
    ax.axhline(data["Balance"].mean(), color='green')
    plt.plot(date_list, balance)
    save(plt, 'zustatek.png')
