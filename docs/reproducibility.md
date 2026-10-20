# Odtwarzalność

Kod jest uporządkowaną wersją obliczeń wykorzystanych przy opracowaniu raportu. Rdzeń MMRM/CR2 zachowuje oryginalne wzory i ustawienia optymalizacji. Pełna baza rzeczywista nie jest częścią repozytorium, dlatego odbiorca może zweryfikować procedurę na danych sztucznych, lecz nie może niezależnie odtworzyć liczbowych wyników badania bez dostępu do danych.

Dla ścisłego odtworzenia potrzebne są: ten sam lokalny zbiór wejściowy po uzgodnionych korektach, identyczne grupy/szkoły/klasy, decyzje o brakach danych, zakresy testów EDU, kolejność danych, wersje bibliotek, ustawienia i ziarna losowania. Samo uruchomienie przykładu nie odtwarza tabel raportu.

`run_manifest.json` zapisuje hash SHA-256 lokalnego wejścia, wersje Python/NumPy/pandas/SciPy, ustawienia bootstrapu, ziarna, czas i liczbowe informacje audytu. Nie zapisuje nazwy pliku źródłowego ani listy rzeczywistych ID. Zachowaj ten plik lokalnie wraz z wynikami i dokładnym SHA commita kodu.

Dla właściwego obliczenia nie używaj `--quick`. Przykład syntetyczny powstaje deterministycznie (`seed=8675309`) i ma 300 sztucznych uczniów oraz 700 wierszy. Wyniki nie zostały dobierane tak, aby odtwarzały wnioski badania.

Poza ograniczoną ilustracją 10 wierszy samych wyników CAPL/CAMSA w repozytorium nie ma danych jednostkowych ani map identyfikatorów, prywatnych logów, rzeczywistych modeli w JSON ani plików źródłowych Excel. Nie gwarantuje się automatycznego wyeksportowania layoutu dokumentu Word; wyjściem są sprawdzalne tabele CSV, modele JSON i ryciny.

Przed cytowaniem kodu w raporcie użyj stałego odnośnika do konkretnego commita albo oznaczonej wersji. Jeśli repozytorium pozostaje prywatne, czytelnik raportu nie zobaczy jego zawartości bez uprawnień.

CSV jest odczytywany z `float_precision="round_trip"`. To zachowuje zapisane liczby zmiennoprzecinkowe: nawet różnica rzędu 10⁻¹⁵ może zmienić remisy w korelacji rangowej. Nie zaokrąglaj punktacji domen przed analizą.


## Aktualizacja 20 października 2026

Do przeliczenia poprawionego szerokiego arkusza użyj konwertera z `--merge-duplicates`, jeśli wcześniej potwierdzono zgodność kopii ID. Zachowaj również audyt konwersji obok kanonicznego CSV. Audyt pipeline jest drugim etapem kontroli: obejmuje m.in. AR z niepełnymi domenami i dostępne liczebności. Nie publikuj źródłowego arkusza, wejściowego CSV ani prywatnych modeli.

Dodano odtwarzalne porównanie kroków GK pre→rok oraz ryciny 1–6 z przedziałami ufności. W GE/GK wykresy przebiegu wykorzystują średnie modelowe; GN jest osobnym opisem z CR2. PNG można wstawić do Worda, ale repozytorium nie generuje automatycznie podświetleń zmian w dokumencie ani jego składu stron. Dane syntetyczne pozostają przykładem działania, a wcześniejsza próbka rzeczywistych 10 wyników nie została rozszerzona.
