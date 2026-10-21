# Kontrola danych i założeń analiz

Materiał uzupełniający do raportu dotyczącego trwałości wyników CAPL oraz ich związku z matematyką i językiem polskim. Dotyczy przeliczenia poprawionej bazy z 20 października 2026 r. Udostępniono 21 października 2026 r. Zawiera informacje zbiorcze, bez identyfikatorów i rekordów pojedynczych uczniów.

Opis procedur i definicje testów: [Metody analiz](methods.md). Kod zweryfikowany przy przeliczeniu raportu: [commit 79cb3ea](https://github.com/wieslawfirek/CAPL-trwalosc-EDU/tree/79cb3eaba78d58bd4f153c5194419dd4b0015e0a). Poniższe liczby odnoszą się do tej wersji danych; po kolejnej zmianie bazy wymagają ponownego sprawdzenia.

## Przygotowanie i kompletność danych

Nowy arkusz zawierał 695 wierszy danych. Pełny identyfikator miało 626 wierszy, odpowiadających 594 uczniom. Połączono 32 dodatkowe wiersze z powtórzonym ID: w dziewięciu analizowanych zmiennych, wynikach EDU i płci nie było sprzecznych niepustych wartości. Grupy, ośrodki, szkoły i klasy odczytano z pełnego ID; niepuste etykiety grup w arkuszu były z nim zgodne. Nie łączono osób na podstawie podobieństwa wyników.

Z analiz wyłączono 69 wierszy bez pełnego ID: 67 z kodem niepełnym lub tymczasowym oraz dwa bez identyfikatora. Część zawiera wyniki, ale bez potwierdzonego połączenia z uczniem i grupą ich włączenie mogłoby spowodować błędne przypisanie lub podwójne liczenie. Liczebności raportu dotyczą uczniów z pełnym ID, a nie wszystkich wierszy arkusza. Po ewentualnym uzupełnieniu tych ID konieczne będzie kolejne przeliczenie.

W 12 obserwacjach AR było wpisane mimo braku co najmniej jednej domeny; te wartości AR potraktowano jako brak danych, zachowując dostępne wyniki pozostałych zmiennych. Pozostałe AR były zgodne z sumą domen w granicach zaokrągleń 0,051 pkt. Kod −999 traktowano jako brak. Nie odrzucano zera ani wysokich, ale dopuszczalnych wyników. Dla 26 uczniów z pełnym ID nie było żadnego z dziewięciu wyników CAPL lub prób surowych. Brak płci nie wykluczał ucznia z analiz wyników.

### Zestawienie poprzedniej i aktualnej wersji wyników

| Zakres | Poprzedni raport | Po aktualizacji |
| --- | --- | --- |
| Uczniowie z pełnym ID | 586 | 594 |
| Co najmniej jeden wynik w dowolnym terminie | 536 | 568 |
| Pretest / posttest / po roku | 327 / 330 / 490 | 331 / 333 / 541 |
| CAMSA GE post–rok: p po korekcie | 0,039 | 0,291 |
| CAMSA GK post–rok: p po korekcie | 0,028 | 0,134 |
| Wiedza i zrozumienie GE post–rok: p po korekcie | 0,043 | 0,059 |

Wyniki korelacji zmieniły się nieznacznie. Utrzymały się główne wnioski: dodatnie związki AR, kompetencji ruchowych, motywacji i wiedzy z oboma testami, związek CAMSA z matematyką oraz brak potwierdzonego związku zachowań codziennych z testami szkolnymi po korekcie Holma. ICC matematyki i języka polskiego pozostały takie same; ich dane źródłowe nie zmieniły się w analizowanej próbie.

## Uzupełniające porównania z poziomem początkowym

Tabela A1 zawiera kontrasty potrzebne do interpretacji całego przebiegu, w tym sprawdzenia przewagi programu bezpośrednio po interwencji i po roku. Różnica zmian oznacza zmianę GE minus zmianę GK; wartości dodatnie oznaczają korzystniejszą zmianę GE. Korektę Holma wykonano oddzielnie dla dziewięciu wyników w każdej kolumnie. Nie są to dodatkowe, niezależne dowody trwałości.

### Tabela A1 Uzupełniające porównania z poziomem początkowym

| Zmienna | GE post–pre / zmiana; p skoryg. | GE rok–pre / zmiana; p skoryg. | Różnica zmian post–pre / [95% PU]; p skoryg. | Różnica zmian rok–pre / [95% PU]; p skoryg. |
| --- | --- | --- | --- | --- |
| Alfabetyzacja ruchowa | 5,47; 0,019 | 5,10; 0,065 | -0,40 / [-4,86; 4,06] / 1,000 | -1,12 / [-5,93; 3,69] / 1,000 |
| Kompetencje fizyczne | 2,57; 0,019 | 2,93; 0,015 | 0,48 / [-1,47; 2,43] / 1,000 | -0,21 / [-2,17; 1,76] / 1,000 |
| Zachowania codzienne | 2,16; 0,143 | 0,95; 1,000 | -0,99 / [-3,75; 1,77] / 1,000 | -0,84 / [-3,65; 1,98] / 1,000 |
| Motywacja i pewność siebie | 0,10; 1,000 | -0,31; 1,000 | 0,08 / [-0,83; 0,99] / 1,000 | 0,41 / [-0,99; 1,81] / 1,000 |
| Wiedza i zrozumienie | 0,09; 1,000 | 1,01; 0,005 | -0,20 / [-0,84; 0,44] / 1,000 | -0,13 / [-0,66; 0,39] / 1,000 |
| CAMSA | 2,73; 0,012 | 3,64; < 0,001 | 0,64 / [-0,76; 2,04] / 1,000 | 0,13 / [-1,34; 1,61] / 1,000 |
| Plank | 21,56; 0,185 | 13,01; 1,000 | 14,27 / [-10,09; 38,63] / 1,000 | -12,72 / [-53,54; 28,10] / 1,000 |
| Beep test | 6,20; 0,001 | 5,78; 0,013 | 1,20 / [-4,04; 6,45] / 1,000 | 0,30 / [-5,29; 5,89] / 1,000 |
| Liczba kroków | 1151; 0,225 | 42; 1,000 | -638 / [-2210; 934] / 1,000 | -983 / [-2633; 668] / 1,000 |

Testy zmian wewnątrz GE pokazują przebieg jej wyników, ale o dodatkowej korzyści programu rozstrzyga porównanie zmian GE–GK. Dla żadnej z dziewięciu zmiennych nie wykazano takiej różnicy po korekcie Holma ani w postteście względem pretestu, ani po roku względem pretestu.

## Kontrola założeń i analizy wrażliwości

Każdy MMRM miał osobną nieustrukturyzowaną macierz zależności trzech pomiarów w GE i GK. Pozwala to na różne wariancje w terminach i grupach; założenie sferyczności z klasycznej ANOVA nie jest wymagane. Wszystkie dziewięć modeli głównych i warianty analiz wrażliwości zakończyły się zbieżnością. Dwa różne punkty startowe dały praktycznie taki sam wynik dopasowania. Uwzględnienie klasy w CR2 dotyczy niepewności oszacowań; nie jest losowym efektem klasy w HLM.

Oceniono wykresy kwantylowe reszt, test Shapiro–Wilka i test Levene’a dla GE–GK w każdym terminie. Testy te mają charakter orientacyjny: obserwacje są powiązane, a wartość p nie jest automatyczną regułą wyboru modelu. Korelacja Spearmana nie wymaga normalności analizowanych wyników. Korelacje Pearsona wewnątrz klas opisują zależność liniową; ich niepewność oszacowano bootstrapem całych klas. Normalność i równość wariancji nie zostały przyjęte wyłącznie na podstawie nieistotnego testu.

### Tabela A2 Diagnostyka dziewięciu modeli głównych

| Zmienna | N uczniów / obserwacji | Klasy / szkoły | Shapiro reszt p | Levene pre / post / rok p | Liczba reszt \|z\| > 3 |
| --- | --- | --- | --- | --- | --- |
| Alfabetyzacja ruchowa | 349 / 845 | 20 / 7 | 0,541 | 0,771 / 0,267 / 0,072 | 2 |
| Kompetencje fizyczne | 366 / 963 | 20 / 7 | 0,287 | 0,127 / 0,651 / 0,932 | 3 |
| Zachowania codzienne | 359 / 890 | 20 / 7 | 0,005 | 0,555 / 0,049 / 0,075 | 1 |
| Motywacja i pewność siebie | 369 / 967 | 20 / 7 | < 0,001 | 0,327 / 0,298 / 0,280 | 9 |
| Wiedza i zrozumienie | 369 / 967 | 20 / 7 | < 0,001 | 0,276 / 0,147 / 0,662 | 1 |
| CAMSA | 369 / 976 | 20 / 7 | < 0,001 | 0,691 / 0,007 / 0,006 | 4 |
| Plank | 367 / 968 | 20 / 7 | < 0,001 | 0,549 / 0,039 / 0,218 | 20 |
| Beep test | 368 / 969 | 20 / 7 | < 0,001 | 0,536 / 0,425 / 0,374 | 11 |
| Liczba kroków | 357 / 911 | 20 / 7 | < 0,001 | 0,804 / 0,100 / 0,051 | 8 |

Analizy wrażliwości obejmowały uczniów z kompletem trzech wyników, pominięcie trzech niejednoznacznych przypisań grup do klas oraz logarytm dodatnich wyników planku i liczby kroków. Wnioski o braku wykazanej przewagi zmian GE nad GK należy oceniać łącznie z ich precyzją. Poniżej podano skorygowane wartości p dla różnicy zmian posttest–po roku; dla wariantu logarytmicznego podano p bez korekty, ponieważ dotyczył dwóch prób i nie był częścią rodziny dziewięciu wyników.

### Tabela A3 Analizy wrażliwości różnicy zmian posttest–po roku

| Zmienna | Główny / p skoryg. | Komplet 3 pomiarów / p skoryg. | Bez 3 przypisań / p skoryg. | Logarytm / p bez korekty |
| --- | --- | --- | --- | --- |
| Alfabetyzacja ruchowa | 1,000 | 1,000 | 1,000 | — |
| Kompetencje fizyczne | 1,000 | 1,000 | 1,000 | — |
| Zachowania codzienne | 1,000 | 1,000 | 1,000 | — |
| Motywacja i pewność siebie | 1,000 | 1,000 | 1,000 | — |
| Wiedza i zrozumienie | 1,000 | 1,000 | 1,000 | — |
| CAMSA | 1,000 | 1,000 | 1,000 | — |
| Plank | 1,000 | 1,000 | 1,000 | 0,548 |
| Beep test | 1,000 | 1,000 | 1,000 | — |
| Liczba kroków | 1,000 | 1,000 | 1,000 | 0,305 |

Bootstrap po całych szkołach oraz szersze przedziały 99,5% dla dziesięciu korelacji Pearsona wykorzystano jako dodatkową kontrolę. Utrzymywały się dodatnie związki AR, kompetencji ruchowych, motywacji i wiedzy z oboma testami szkolnymi; dla zachowań codziennych wnioski pozostają niepewne. ICC opisuje udział zróżnicowania między klasami, a nie przyczynowy wpływ nauczyciela lub klasy. Nie można zweryfikować założenia MAR ani wykluczyć wpływu niezmierzonych czynników na podstawie tych testów.

## Jak odtworzyć kontrolę

Konwersję arkusza wykonuje `src/capl_analysis/convert_wide.py`, z jawną opcją `--merge-duplicates` dla zgodnych kopii ID. Audyt konwersji zapisuje liczebności i hash pliku źródłowego. `src/capl_analysis/data.py` kontroluje zakresy, kompletność domen oraz zgodność AR z ich sumą. `src/capl_analysis/mmrm.py` zapisuje diagnostykę i zbieżność modeli. Pełny przebieg uruchamia `pipeline.py` z opcją `--sensitivity`. Instrukcje znajdują się w [README](../README.md) i [opisie odtwarzalności](reproducibility.md).

Pliki audytu konwersji, kanoniczne dane i szczegółowe obiekty modeli pozostają lokalne. Ten dokument nie zastępuje bazy potrzebnej do niezależnego odtworzenia wyników. Testy rozkładu i wariancji nie pozwalają samodzielnie potwierdzić wszystkich założeń modeli.
