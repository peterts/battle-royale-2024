# Nyetsartikkel til tegneseriestripe

Kode laget under Bouvet sin Battle Royale 2024. Løsningen bruker ChatGPT og Dall-E for å konvertere en nyhetsartikkel til en tegneseriestripe bestående av fire ruter.

## Eksempel

Nyhetsartikkel:

https://www.nrk.no/nordland/kvinne-fodte-pa-badegulvet-mens-samboeren-sov-1.16720938

Output:

![Cartoon](./images/cartoon.png)

## Oppsett

Om du ikke allerde har python installert, vil jeg anbefale å gjøre dette med [pyenv](https://github.com/pyenv/pyenv). Dette prosjektet krever python 3.11 eller høyere.

Prosjektet bruker poetry for å håndtere python-miljøet. Installasjonsinstruksjoner kan du finne [her](https://python-poetry.org/docs/#installation).

Når poetry er installert kan du installere python-avhengighetene ved å kjøre `poetry install`.

For å kunne kjøre koden må du opprette en `.env`-fil i roten av dette repoet, som inneholder følgende nøkler:

```.env
DALLE_API_KEY=
CHATGPT_API_KEY=
```

Du kan så kjøre koden ved å kjøre `news_article_to_cartoon.py` i IDEen din, eller du kan kjøre følgende fra kommandolinja:

```
poetry run python battle_royale_2024/
```