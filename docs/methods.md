# Metody analiz

## Próba i braki danych

Główne analizy podłużne obejmują GE i GK z przynajmniej jednym wynikiem danej zmiennej. GN wchodzi wyłącznie do analiz pomiaru po roku. Demografia w każdym terminie obejmuje osoby z co najmniej jedną z dziewięciu zmiennych; nie oznacza kompletu CAPL. Liczebność każdej analizy jest zapisywana osobno.

Nie imputuje się wyników. AR jest usuwany z danego terminu, gdy brakuje którejkolwiek domeny. Prawidłowe zero pozostaje wynikiem. Dostępny AR musi zgadzać się z sumą domen w granicach 0,051 pkt tolerancji zaokrągleń; nie przelicza się go potajemnie.

Nie ma losowania przydziału do grup w kodzie. Nie zakładamy, że historyczny przydział klas był losowy. Metadane klasy muszą odzwierciedlać faktyczne przypisanie; kod nie odgaduje nowej klasy z roku pomiaru. W analizach uzupełniających, zgodnie z historyczną decyzją, pomija się rekordy z grupą inną niż dominująca w klasie. Liczba takich osób jest raportowana; remisy wymagają wyjaśnienia. Główne analizy zachowują oznaczenia grup ze źródła.

## MMRM

Dla każdej zmiennej model zawiera sześć średnich grupa × termin (GE/GK × pre/post/rok) oraz wskaźniki szkoły z jedną szkołą referencyjną. Estymacja REML z nieustrukturyzowaną 3×3 kowariancją pomiarów tej samej osoby, odrębną dla GE i GK. Brak założenia równej odległości lub liniowego przebiegu zmian. Szkoła jest efektem stałym, nie ośrodek. Klasy wchodzą do odpornej macierzy kowariancji CR2, a nie jako losowy wyraz wolny.

Macierze parametryzuje się rozkładem Cholesky'ego. Optymalizację L-BFGS-B wykonuje się z dwóch punktów startowych. Kontroluje się zbieżność, zgodność minimum oraz równania GLS. MMRM z niepełnymi seriami opiera się na założeniu MAR; nie można dowieść go z dostępnych wyników. Błędy standardowe CR2 i stopnie swobody Satterthwaite'a uwzględniają zależność w klasach; nie usuwają wszystkich możliwych źródeł zakłócenia.

Kontrasty: `immediate` = różnica zmian GE–GK pre→post; `lasting` = różnica zmian pre→rok; `erosion` = różnica zmian post→rok. Nazwa `erosion` jest etykietą techniczną i nie przesądza o spadku. Dodatkowe kontrasty objęte korektą to GE pre→post, GE pre→rok oraz GE i GK post→rok. Każdy z siedmiu typów tworzy osobną rodzinę dziewięciu testów Holma. Przedziały 95% są punktowe. Standaryzowana zmiana wykorzystuje łączone SD wyjściowe; nie jest klasycznym d dla sparowanych prób.

Diagnostyka: reszty po wybieleniu, wykresy Q–Q, Shapiro–Wilk, Levene według terminu, wyniki skrajne oraz stabilność po opuszczeniu klasy przy ustalonej kowariancji. Nominalne testy rozkładu/wariancji są pomocnicze: nie uwzględniają całej zależności danych. Nie są automatyczną bramką „parametryczny albo nieparametryczny”.

Opcja `--sensitivity`: kompletne serie, pominięcie niejednoznacznych rekordów oraz naturalny logarytm dodatnich wyników planka i kroków. Modele logarytmiczne są eksploracyjne; dla nich nie tworzy się wspólnej rodziny Holma z głównymi wynikami.

## GN

Regresja OLS: wynik po roku ~ grupa + ośrodek, GN jako odniesienie. Macierz CR2 dla klas i stopnie swobody Satterthwaite'a. Holm łącznie dla 9×2=18 porównań. Ośrodek wpływa na oszacowanie różnicy, klasa na SE/PU/p. Nie jest to korekta przyczynowego wpływu szkoły; GN pochodzi z innych szkół.

## Związek z EDU

Współczynnik Spearmana dla AR, PC, DB, KU, MC i CAMSA z matematyką i językiem polskim. Pochodna statystyka p: nachylenie regresji standaryzowanych rang z CR2 dla klas, a nie standardowe p z `scipy.stats.spearmanr`. Numerycznie sprawdzana jest zgodność nachylenia ze współczynnikiem Spearmana.

Holm wspólnie dla 12 testów. Po rozdzieleniu rycin na przedmioty rodzina korekty pozostaje ta sama. PU 95%: percentylowy bootstrap całych klas (AR/domeny B=3000, ziarno 20261015; CAMSA B=5000, ziarno 20261017). Pierwotne dziesięć par przetwarzane jest w kolejności matematyka/polski, wewnątrz AR/PC/DB/KU/MC; CAMSA jako osobne rozszerzenie. Nieliczne zmiany kolejności rekordów mogą zmienić końce bootstrapowych PU, dlatego dla ścisłego odtworzenia należy zachować kolejność źródła.

## Analizy wewnątrz klas i ICC

Korelacja Pearsona wyników po odjęciu średnich klasy, osobno dla każdej dostępnej pary CAPL–EDU. Pomija się klasy z mniej niż dwiema osobami w parze. Nie jest to korelacja Spearmana ani przyczynowy model efektu klasy.

ICC oblicza się z jednoczynnikowej ANOVA przy nierównych liczebnościach, z korektą efektywnej liczebności klasy. Ujemną estymatę wariancji między klasami ogranicza się do zera. Punktowe 95% PU i pomocnicze 99,5% PU korelacji wewnątrz klas (Bonferroni dla 10 par) uzyskuje się z bootstrapu 20 000 całych klas warstwowanego GE/GK vs GN, ziarno 20261016. Analiza wrażliwości losuje całe szkoły. Nie oblicza się „p Holm” dla tych 10 współczynników poprzez użycie wartości z głównych korelacji.

## Interpretacja

Brak istotnej różnicy nie dowodzi równości ani pełnej trwałości. Kod nie ustala po fakcie dopuszczalnej straty i nie wykonuje testów równoważności. ICC nie jest udziałem wyników „spowodowanym przez nauczyciela”. Dodatnia korelacja nie dowodzi, że poprawa CAPL spowoduje poprawę EDU. Wyniki punktowe nie są automatycznie normami wieku/płci. Główne analizy różnią się liczebnościami od uzupełniających, co jest ujawnione w wyjściu.

## Przygotowanie poprawionej bazy i dodatkowe porównanie kroków

W konwerterze pełne ID ma postać `O[1-5][A-Z]_cyfra-litera_GE/GK/GN_trzy-cyfry`. Niepełne i tymczasowe kody są pomijane i liczone osobno od pustych ID. Przed modelowaniem trzeba sprawdzić audyt; pominięcie kodu nie oznacza, że osoba nie miała żadnych wyników. Połączenie kopii ID wymaga jawnej opcji `--merge-duplicates`. Łączenie uzupełnia tylko brakujące wartości; sprzeczne wyniki lub płeć zatrzymują procedurę. Nie uśredniamy sprzecznych wpisów i nie tworzymy połączeń z podobnych wyników. Dla kontroli duplikatów brane są pod uwagę wyłącznie zmienne analizowane, wyniki EDU i płeć; pozostałe narzędzia w źródłowym arkuszu nie należą do zakresu konwersji.

Eksploracyjne porównanie liczby kroków po roku z pretestem w GK pochodzi z tego samego modelu MMRM i tej samej macierzy CR2 co pozostałe kontrasty. Jest przechowywane w `exploratory_contrasts.GK_pre_year`. Plik `stepcount_pre_year.csv` zawiera oba porównania GE/GK, punktowe 95% PU i **surowe p**. Ten dodatkowy wynik nie zmienia siedmiu pierwotnych rodzin Holma; kolumna `p_adjustment` jawnie wskazuje brak korekty. Nie wolno interpretować nieistotnego p jako dowodu powrotu do identycznego poziomu początkowego.

## Wyniki kontroli dla aktualnego raportu

Zbiorcze liczebności audytu, wyniki testów diagnostycznych oraz analizy wrażliwości przeliczenia z 20 października 2026 r. przedstawiono w [Kontroli danych i założeń analiz](data_quality.md). To uzupełnienie metodologiczne do raportu, bez udostępniania bazy jednostkowej.
