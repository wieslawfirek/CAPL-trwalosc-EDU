# Słownik danych wejściowych

CSV UTF-8, separator przecinek, separator dziesiętny kropka. Jeden wiersz na parę `id,time`; bez kolumny indeksu. Przykład jest w `examples/capl_synthetic_long.csv`.

| Kolumna | Znaczenie |
|---|---|
| id | Stały kod ucznia, dowolny tekst; bez imienia i nazwiska |
| group | GE / GK / GN |
| school | Globalnie jednoznaczny kod szkoły |
| class_id | Globalnie jednoznaczny kod klasy, zawierający odróżnienie szkół |
| center | Ośrodek; tekst |
| sex | F = dziewczęta, M = chłopcy, puste = brak danych |
| time | 1 = pre, 2 = post, 3 = po roku; GN wyłącznie 3 |
| age_year | Wiek w pomiarze po roku; dla 1/2 pozostawić puste |
| PC | Kompetencje fizyczne, 0–30 pkt (KF w raporcie) |
| DB | Zachowania codzienne, 0–30 pkt (ZC) |
| MC | Motywacja i pewność siebie, 0–30 pkt (MiP) |
| KU | Wiedza i zrozumienie, 0–10 pkt (WiZ) |
| AR | Suma czterech domen, 0–100 pkt; brak przy niepełnych domenach |
| CAMSA_sur | Wynik surowy, 0–28 pkt |
| Plank_time | Czas w sekundach, ≥0 |
| PACER_odcinki | Liczba odcinków beep testu, ≥0 |
| StepCount | Średnia dzienna liczba kroków, ≥0 |
| EDU_Matematyka_wynik | Wynik testu 0–18 pkt, tylko time=3 |
| EDU_Polski_wynik | Wynik testu 0–18 pkt, tylko time=3 |

Nie obliczamy wyniku EDU z procentów. Jeśli w innym badaniu skala EDU jest inna, trzeba jawnie zmienić walidację, opisać skalę i ponownie zweryfikować kod.

Kod nie wymaga prawdziwych identyfikatorów z projektu. Po lokalnym pseudonimizowaniu należy zachować tę samą mapę uczniów i klas we wszystkich terminach. Konwerter historycznego XLSX rozpoznaje natomiast konkretny format ID i wymaga wcześniejszego uporządkowania bazy. Nie przesyłaj ani mapy ID, ani wynikowej bazy do repozytorium.
