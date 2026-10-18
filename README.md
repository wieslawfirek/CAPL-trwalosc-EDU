# CAPL — trwałość efektów i osiągnięcia szkolne

Kod analiz trzech pomiarów CAPL (pretest, posttest, pomiar po roku) w grupie eksperymentalnej GE i kontrolnej GK oraz porównań z nową kohortą GN. Analiza związku CAPL i CAMSA z matematyką oraz językiem polskim dotyczy pomiaru po roku.

**Repozytorium nie zawiera pełnej bazy uczniów.**

- `examples/capl_synthetic_long.csv`: 300 sztucznych uczniów i 700 wierszy, do uruchamiania całej analizy. Wygenerowane niezależnie od rzeczywistych rekordów.
- `examples/real_scores_10.csv`: ilustracyjna próbka rzeczywistych wyników CAPL i CAMSA 10 uczniów z pomiaru po roku. Zawiera wyłącznie wyniki punktowe, zaokrąglone do dwóch miejsc, i techniczne numery wierszy R01–R10. Nie zawiera oryginalnych ID, szkoły, klasy, grupy, ośrodka, wieku, płci ani wyników EDU. Nie publikujemy mapy łączącej wiersze z uczniami. To **przykład formatu wyników**, a nie próba do odtwarzania modeli lub wyników całego badania.

Próbka rzeczywista nie jest wejściem pełnego pipeline: brakuje w niej celowo metadanych i powtarzanych pomiarów. Dla pełnego przykładu użyj bazy syntetycznej.

## Uruchomienie przykładu

Python 3.11 lub nowszy. Polecenia wykonujemy w katalogu repozytorium.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux: source .venv/bin/activate
python -m pip install -e .
python -m capl_analysis.pipeline --input examples/capl_synthetic_long.csv --output outputs/demo --quick
```

`--quick` ogranicza bootstrap do 200 powtórzeń i służy wyłącznie sprawdzeniu działania. Właściwe ustawienia raportu:

```bash
python -m capl_analysis.pipeline --input data_private/capl_long.csv --output outputs/study --sensitivity
```

Bez `--quick`: bootstrap 3000 losowań dla AR i czterech domen, 5000 dla CAMSA oraz 20 000 dla ICC i korelacji wewnątrz klas. `--sensitivity` dodatkowo uruchamia modele dla kompletnych serii, bez rekordów z niejednoznacznym przydziałem oraz modele logarytmiczne planka i kroków. Obliczenia mogą trwać kilka minut lub dłużej, zależnie od komputera.

## Własna baza pozostaje lokalna

Umieść bazę w `data_private/`. Folder ten oraz `outputs/` są wyłączone z wersjonowania. `.gitignore` jest pomocą, a nie techniczną blokadą ręcznego dodania plików — przed `git add` zawsze sprawdź listę plików. Kod niczego nie wysyła przez sieć.

Oczekiwany format CSV opisuje [słownik danych](docs/data_dictionary.md). Jeden wiersz = jeden uczeń w jednym terminie. Stały `id` łączy pomiary, a globalnie jednoznaczny `class_id` łączy uczniów tej samej klasy. Wymagane są osobne oznaczenia szkoły i ośrodka. Wyniki EDU i wiek z pomiaru po roku wpisuje się wyłącznie przy `time=3`. Pusta komórka oznacza brak danych; kod −999 zostaje zamieniony na brak. Zera zachowujemy.

Dla wcześniejszej szerokiej bazy projektu dodano lokalny konwerter:

```bash
python -m pip install openpyxl
python -m capl_analysis.convert_wide --input data_private/source.xlsx --age-file data_private/age.xlsx --output data_private/capl_long.csv
```

Konwerter wymaga pierwszej kolumny ze stałym ID w formacie źródłowym oraz kolumn `AR_1`–`AR_3`, `PC_1`–`PC_3` itd. Starsze nazwy `PLANK_time_1` i `PLANK_time_2` są obsługiwane. `Gender=1` oznacza chłopca, `Gender=2` dziewczynkę. Plik wieku powinien zawierać dwie pierwsze kolumny: ID i wiek **z pomiaru po roku**. Nie ma mechanicznego odejmowania wieku dla pre/post. Należy użyć bazy z wcześniej zweryfikowaną płcią.

## Co wykonuje kod

- waliduje ID, powtarzalność metadanych, zakresy i sumę AR;
- tworzy tabele liczebności według grup, terminów, płci i ośrodków oraz kompletności każdej zmiennej;
- tworzy statystyki opisowe dla dziewięciu zmiennych;
- dopasowuje MMRM z interakcją grupy i terminu, efektem stałym szkoły, osobną macierzą kowariancji GE/GK oraz CR2 dla klas;
- porównuje GE i GK z GN po roku, uwzględniając ośrodek i CR2 dla klas;
- oblicza 12 korelacji Spearmana z EDU wraz z klasową korektą wnioskowania i wspólną korektą Holma;
- oblicza korelacje Pearsona po odjęciu średnich klasowych oraz ICC;
- zapisuje przedziały ufności, diagnostykę, ryciny i metadane uruchomienia.

Szczegóły: [metody i ograniczenia](docs/methods.md), [odtwarzalność](docs/reproducibility.md).

## Gdzie są wyniki

W folderze wskazanym przez `--output`, m.in.:

| Plik | Zawartość |
|---|---|
| `group_sex.csv`, `center_sex.csv` | Liczebności w kolejnych terminach |
| `outcome_counts.csv`, `descriptive.csv` | Kompletność i statystyki opisowe |
| `longitudinal_contrasts.csv` | Zmiany i różnice zmian GE–GK; p oraz p Holma |
| `longitudinal_models.json` | Kowariancje, średnie modelowe, diagnostyka i opcjonalne analizy wrażliwości |
| `GN_comparisons.csv` | GE–GN i GK–GN po roku |
| `spearman.csv` | 12 korelacji, PU, p i p Holma |
| `within.csv`, `icc.csv` | Analizy uzupełniające |
| `supplemental.json` | Również szersze PU i bootstrap szkół |
| `run_manifest.json` | Wersje bibliotek, ustawienia, hash wejścia i audyt |
| `*.png` | Ryciny i wykresy diagnostyczne |

Tabele nie zawierają rekordów pojedynczych uczniów. Wyniki wykonane na rzeczywistej bazie pozostają lokalne. Krótkie komunikaty diagnostyczne nie oznaczają, że wszystkie założenia są spełnione. Przerwanie obliczeń nie powinno być omijane przez usuwanie kontroli błędów.

## Testy

```bash
python -m unittest discover -s tests -v
```

Testy sprawdzają m.in. korektę Holma, zgodność regresji rang z korelacją Spearmana oraz niezmienniczość korelacji wewnątrz klas na przesunięcie średnich klasowych.

## Zakres

To kod **analizy gotowych wyników** CAPL, nie oficjalny kalkulator punktacji CAPL-2 z odpowiedzi na pojedyncze pytania i surowych prób. Nie przypisuje kategorii interpretacyjnych dla wieku/płci. Nie wykonuje testu równoważności ani nie mniejszej skuteczności. Nie dowodzi przyczynowego wpływu WF, nauczyciela lub klasy.
