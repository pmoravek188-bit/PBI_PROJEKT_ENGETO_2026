# PBI_projekt_engeto_2026_Patrik_Moravek

## Popis projektu

Druhý projekt Datové Akademie Engeto zaměřený na vizualizaci datasetu v Power BI.
Report analyzuje databázi **4 800+ filmů** z TMDB (The Movie Database) a vizualizuje klíčové ukazatele filmového průmyslu v interaktivním dashboardu ve stylu IMDB.

## Zdroj dat

- **TMDB 5000 Movie Dataset** z [Kaggle](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)
- Dva zdrojové soubory: `tmdb_5000_movies.csv` a `tmdb_5000_credits.csv`
- Data byla předzpracována Python skriptem (`prepare_data.py`) do 12 čistých tabulek

## Struktura reportu (5 stránek)

### 1. Home Page (úvodní stránka)
- Filmový banner s navigačními tlačítky na jednotlivé stránky
- Vizuální úvod do reportu ve stylu filmové databáze

### 2. Overview
- KPI karty s ikonami: počet filmů, průměrné hodnocení, celkové tržby, celkový profit
- Spojnicový graf: vývoj počtu filmů podle roku (1916-2017)
- Prstencový graf: rozložení filmů podle hodnocení (Vynikající/Dobrý/Průměrný/Slabý)
- Průřezy: žánr, jazyk, rok
- Webový odkaz na TMDB databázi
- Tlačítko "Delete filters" pro reset filtrů

### 3. Genres & Revenue
- Pruhový graf: top žánry podle počtu filmů
- Treemap: celkové tržby podle žánru
- Pruhový graf: průměrné hodnocení podle žánru
- Průřez: dekáda (1910s-2010s)

### 4. Top Movies & ROI
- Sloupcový graf: top 10 nejziskovějších filmů
- Tabulka: detaily filmů (název, rok, hodnocení, rozpočet, tržby, profit)
- Záložky (Bookmarks): přepínání mezi "TOP Profits" a "Bigger Flops"
- Průřez: žánr

### 5. Directors & Actors
- Pruhový graf: top režiséři podle průměrného hodnocení
- Pruhový graf: top herci podle počtu filmů
- Azure Map: geografické rozložení produkčních zemí
- Interaktivní cross-filtering mezi vizuály

## Datový model

```
                    calendar
                       |
actors --- movies_cast --- movies --- movies_genres --- genres
                            |
directors --- movies_directors
                            |
companies --- movies_companies
                            |
countries --- movies_countries
```

Všechny bridge tabulky mají obousměrný křížový filtr pro správné filtrování přes průřezy.

### Tabulky:
| Tabulka | Popis | Počet řádků |
|---|---|---|
| movies | Hlavní tabulka filmů | 4 802 |
| genres | Filmové žánry | 20 |
| actors | Herci | 12 418 |
| directors | Režiséři | 2 399 |
| companies | Produkční společnosti | 4 887 |
| countries | Země produkce | 88 |
| calendar | Kalendářní tabulka | 37 256 |
| movies_genres | Bridge: filmy-žánry | 12 160 |
| movies_cast | Bridge: filmy-herci | 22 561 |
| movies_directors | Bridge: filmy-režiséři | 4 397 |
| movies_companies | Bridge: filmy-společnosti | 13 261 |
| movies_countries | Bridge: filmy-země | 6 436 |

## Splnění požadavků projektu

| Požadavek | Splněno | Detail |
|---|---|---|
| Rozsah 2-5 stránek | 5 stránek | Home Page, Overview, Genres, Top Movies, Directors |
| Min. 5 různých typů vizuálů | 8 typů | Karta, Spojnicový graf, Prstencový graf, Pruhový graf, Sloupcový graf, Treemap, Tabulka, Azure Map |
| Filtrování pomocí průřezů | 4 průřezy | Žánr, rok (posuvník), jazyk, dekáda |
| Interaktivní prvky - záložky | 2 záložky | Přepínání "TOP Profits" / "Bigger Flops" na stránce Top Movies |
| Interaktivní prvky - navigace | Obrázkové tlačítka | Overview, Genres, Top Movies, Directors + šipky + Home |
| Interaktivní prvky - webový odkaz | Odkaz na TMDB | Ikona zeměkoule s odkazem na themoviedb.org |
| Interaktivní prvky - Delete filters | Tlačítko reset | Na každé stránce tlačítko pro smazání filtrů |
| Propojení 2+ tabulek | 12 tabulek | Propojení přes bridge tabulky s obousměrným křížovým filtrem |
| Hierarchie (2 úrovně) | Dekáda > Rok | V tabulce calendar, použitelná pro drill-down |
| Min. 1 measure | 8 measures | Movie Count, Avg Rating, Total Revenue, Total Profit, Genre Rank, Rating Genre Rank, Actor Rank, Director Rating Rank |
| Min. 1 kalkulovaný sloupec | 1 sloupec | Rating Category (kategorizace hodnocení filmů) |
| Grafická úprava | IMDB styl | Tmavé pozadí, žlutý akcent, vlastní ikony, filmový banner |

## DAX Measures

```dax
Movie Count = COUNTROWS(movies)
Avg Rating = AVERAGE(movies[vote_average])
Total Revenue = SUM(movies[revenue])
Total Profit = SUM(movies[profit])
Genre Rank = RANKX(ALL(genres[genre_name]), [Movie Count], , DESC)
Rating Genre Rank = RANKX(ALL(genres[genre_name]), [Avg Rating], , DESC)
Actor Rank = RANKX(ALL(actors[actor_name]), [Movie Count], , DESC)
Director Rating Rank = RANKX(ALL(directors[director_name]), [Avg Rating], , DESC)
```

## Kalkulovaný sloupec

```dax
Rating Category =
    SWITCH(TRUE(),
        VALUE(movies[vote_average]) >= 8, "Vynikající (8+)",
        VALUE(movies[vote_average]) >= 6, "Dobrý (6-8)",
        VALUE(movies[vote_average]) >= 4, "Průměrný (4-6)",
        "Slabý (pod 4)"
    )
```

## Barevné schéma (IMDB styl)

| Prvek | HEX |
|---|---|
| Pozadí stránek | #1F1F1F |
| Pozadí vizuálů | #121212 |
| Hlavní akcent (IMDB žlutá) | #F5C518 |
| Text | #FFFFFF |
| Sekundární text | #AAAAAA |
| Sekundární akcent (oranžová) | #E8952E |
| Zelená (Vynikající 8+) | #27AE60 |
| Žlutá (Dobrý 6-8) | #F5C518 |
| Oranžová (Průměrný 4-6) | #E67E22 |
| Červená (Slabý pod 4) | #C0392B |

## Interaktivní prvky

- **Navigace po stránkách** - obrázkové tlačítka (Overview, Genres, Top Movies, Directors) + šipky vlevo/vpravo + Home
- **Záložky (Bookmarks)** - přepínání pohledů TOP Profits / Bigger Flops
- **Webový odkaz** - ikona zeměkoule odkazující na TMDB (themoviedb.org)
- **Cross-filtering** - kliknutí na vizuál filtruje ostatní vizuály na stránce
- **Delete filters** - tlačítko pro reset všech filtrů na stránce
- **Drill-down** - hierarchie Dekáda > Rok v časových vizuálech

## Struktura souborů

```
PBI_ENGETO_Projekt/
├── PBI_projekt_engeto_2026_Patrik_Moravek.pbix  # Power BI report (obsahuje všechna data)
├── README.md                       # Dokumentace projektu
├── prepare_data.py                 # Python skript pro přípravu dat
├── tmdb_5000_movies.csv            # Zdrojová data - filmy
├── tmdb_5000_credits.csv           # Zdrojová data - herci a režiséři
├── clean_data/                     # Vyčištěná data (12 CSV/TXT souborů)
│   ├── movies.txt
│   ├── genres.csv
│   ├── actors.csv
│   ├── directors.csv
│   ├── companies.csv
│   ├── countries.csv
│   ├── calendar.csv
│   ├── movies_genres.csv
│   ├── movies_cast.csv
│   ├── movies_directors.csv
│   ├── movies_companies.csv
│   └── movies_countries.csv
└── ikony/                          # Grafické prvky pro report
    ├── icon_movies.png
    ├── icon_rating.png
    ├── icon_revenue.png
    ├── icon_trend.png
    ├── icon_directors.png
    ├── btn_overview.png
    ├── btn_genres.png
    ├── btn_topmovies.png
    ├── btn_directors.png
    ├── btn_left.png
    ├── btn_right.png
    ├── btn_home.png
    ├── btn_web.png
    └── klik na web.png
```

## Technické požadavky

- **Power BI Desktop** (ke stažení zdarma na [powerbi.microsoft.com](https://powerbi.microsoft.com))
- Soubor `.pbix` obsahuje všechna data — není potřeba stahovat další soubory
- Pro zobrazení Azure Map je vyžadováno povolení vizuálu Azure Maps v Power BI

## Příprava dat

Data byla předzpracována Python skriptem `prepare_data.py`, který:
1. Rozparsoval JSON sloupce (genres, cast, crew, production_companies, countries)
2. Vytvořil separátní dimenzní a bridge tabulky
3. Vyčistil a převedl datové typy
4. Vytvořil kalendářní tabulku pro časovou hierarchii
5. Přidal kalkulované sloupce (release_year, release_month, decade, profit)

## Autor

Patrik Moravek - Datová Akademie Engeto 2026
