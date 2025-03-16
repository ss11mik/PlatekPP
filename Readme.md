# Plátek++;

Individuální statistiky stravování v menzách VUT.

## Import dat

V systému ISKAM (v případě VUT https://www.skm.vutbr.cz/app05/IsKAM/InformaceOKlientovi) je potřeba nejprve přepnout rozhraní do angličtiny. Následně zobrazit výpis z Hlavního konta, nastavit parametr "od" tak, aby pokrýval celé studium.

### Import HTML
Stáhnout webovou stránku s tabulkou a uložit jako HTML soubor. Konvertovat přiloženým skriptem na XLSX:
```
python html2xlsx.py ISKAM.html ISKAM.xlsx
```

### Import XLSX
Stačí stáhnout dataset tlačítkem "Export do Excelu". Stažený soubor předat jako parametr skriptu.

Nevýhoda tohoto postupu je, že nezachovává informace o položkách v menu (viz poznámky).


## Spuštění

```
pip install -r requirements.txt
python platek.py ISKaM4_ss11mik_HLA.xlsx
```

## Výstup

Grafy a statistiky jsou uloženy v podsložce `out/`

### Grafy
- dny.png - histogram placení v menze dle dnů.
- inflace.png - inflace zachycená v cenách příloh.
- jidla.png - histogram nejčastěji objednávaných jídel. Položky jsou vybrány ručně, takže některé mohou chybět. Sjednocuje některá jídla do kategorií (např. "Guláš maďarský" i "Guláš 150g hovězí" jsou započítány v kategorii "Guláš").
- masa.png - četnost druhů mas v objednávaných jídlech.
- prilohy.png - četnost různých příloh.
- tydny.png - průměrný počet návštěv menzy v daném týdnu napříč roky. Zobrazuje různá období, jako začátek semestru, zkouškové období, prázdniny. Indexování podle kalendářního týdne. Zelená čára značí celkový průměr.
- vydaje.png - rozdělení výdajů z konta na ubytování, hlavní jídla v menze, přílohy (zahrnuje i dezerty a nápoje), KolejNet, praní (včetně sušení) a tisk.
- casy.png - histogram časů placení v menze.
- casy_v_tydnu.png - histogram časů placení v menze, samostatně pro každý den v týdnu.
- zustatek.png - graf zůstatku na kontě s vyznačenou průměrnou hodnotou.

### Textové statistiky
"Leaderboard" nejčastěji objednávaných položek z kategorie

- dezerty.csv
- pizzy.csv
- platky.csv
- polevky.csv 
- steaky.csv


## Poznámky
- potenciálně může fungovat i s exportem z kteréhokoliv ISKAM systému, ale názvy a kategorie jídel jsou navrženy podle těch, které se vyskytují ve VUT KaM menzách.
- informaci o tom, ve které menze transakce proběhla, není možné z ISKAMu dostat.
- z výpisu není možné rozlišit hlavní jídlo, menu a přílohu jinak, než manuálně vytvořeným seznamem (viz zdrojový kód).
- obědové menu je v XLSX exportu vedeno pouze jako "Menu R 1" / "Menu R 2" / "Menu R 3", takže jej nelze správně započítat do statistik mas, příloh atd. Řešením je stáhnout HTML tabulku a tu konvertovat na XLSX přiloženým skriptem.
- vzorkování dat v některých grafech je provedeno podle magické konstanty (např. `plt.hist(casy, bins=128)`), kterou je možné libovolně měnit.

