# Direktiv: Dagligt Nyhedsbrev

## Formål
Send et nyhedsbrev til `thoresbensenmagnusesbensen@gmail.com` hver hverdag.

## Inputs
- Nyhedsbrevets indhold (specificeres separat — se "Indholdsformat" nedenfor)
- Gmail-afsenderkonto og app-password (i `.env`)

## Outputs
- E-mail sendt til modtager

## Indholdsformat
Indholdet hentes fra `content/nyhedsbrev_indhold.md`. Filen skal indeholde:
```
EMNE: <emnelinjen>

<Brødteksten i HTML eller plaintext>
```

## Trin
1. Læs indhold fra `content/nyhedsbrev_indhold.md`
2. Kør `execution/send_newsletter.py`
3. Scriptet sender e-mailen via Gmail SMTP
4. Log afsendelse til `logs/nyhedsbrev.log`

## Miljøvariabler (i `.env`)
```
GMAIL_USER=din@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
NEWSLETTER_TO=thoresbensenmagnusesbensen@gmail.com
```

## Fejlhåndtering
- Hvis `content/nyhedsbrev_indhold.md` mangler: afbryd og log fejl
- Hvis SMTP fejler: log fejl og prøv én gang mere efter 60 sekunder
- Opdater dette direktiv med nye fejlmønstre efterhånden

## Planlægning
Kør `execution/schedule_setup.bat` én gang for at oprette en Windows Task Scheduler-opgave, der kører scriptet mandag-fredag kl. 08:00.
