# Alexa skill for reading German local news (Mittelschwaebische Nachrichten)

This skill reads current headlines and more detailed information about news articles of a local German newspaper (<a href="http://www.augsburger-allgemeine.de/krumbach/">Mittelschäbische Nachrichten</a>).

The lambda code is written in Python 3.6.

## Interaction model

- Create a new Alexa Skill in the Amazon developer console
- The following interaction model needs to be set up

### Intents
```json
{
  "intents": [
    {
      "intent": "Ueberschriften"
    },
    {
      "slots": [
        {
          "name": "ArtikelNummer",
          "type": "AMAZON.NUMBER"
        }
      ],
      "intent": "Detail"
    },
    {
      "intent": "NoIntent"
    }
  ]
}
```

### Sample utterances for intents
```
Ueberschriften Lies alle Überschriften vor
Ueberschriften Was gibt es neues
Ueberschriften Ja
Ueberschriften Mach das
Ueberschriften Okay
Detail Lies mir Artikel {ArtikelNummer} vor
Detail Was steht in Artikel {ArtikelNummer}
Detail Nummer {ArtikelNummer}
Detail {ArtikelNummer} vorlesen
NoIntent Nein
NoIntent Geh weg
```