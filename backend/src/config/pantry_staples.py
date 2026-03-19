"""Konfiguracja produktów podstawowych spiżarni

Kuratorowana lista typowych produktów spiżarkowych/lodówkowych, które użytkownicy zazwyczaj posiadają.
Najczęstsze produkty powodujące marnotrawstwo gdy nie są śledzone.
"""

# Kuratorowana lista nazw produktów podstawowych
# Muszą dokładnie odpowiadać nazwom produktów w bazie danych
PANTRY_STAPLES = [
    # Oleje i tłuszcze
    "Oliwa z oliwek",
    "Olej roślinny",
    "Olej sezamowy",
    "Olej kokosowy",
    "Masło",
    # Podstawowe przyprawy
    "Sól",
    "Pieprz czarny",
    "Czosnek granulowany",
    "Cebula granulowana",
    "Papryka słodka",
    "Kmin rzymski",
    "Oregano",
    "Bazylia",
    "Tymianek",
    "Cynamon",
    # Sosy i przyprawy
    "Soy sauce",  # Keep as is - it's a brand/type name
    "Miód",
    "Musztarda",
    "Ketchup",
    "Majonez",
    "Sos pomidorowy",
    "Oliwa z oliwek",
    "Ocet balsamiczny",
    "Sok z cytryny",
    # Zboża i skrobie
    "Ryż",
    "Ryż biały",
    "Ryż brązowy",
    "Mąka",
    "Mąka pszenna",
    "Makaron",
    "Spaghetti",
    "Chleb",
    "Płatki owsiane",
    # Nabiał i jaja
    "Jaja",
    "Mleko",
    "Masło",
    "Ser",
    "Jogurt grecki",
    "Parmezan",
    # Warzywa (długi okres przydatności)
    "Cebula",
    "Czosnek",
    "Ziemniaki",
    "Marchewka",
]

# Usuń duplikaty zachowując kolejność
PANTRY_STAPLES = list(dict.fromkeys(PANTRY_STAPLES))
