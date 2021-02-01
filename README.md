# iCMS Personal Grades Crawler HsH

Docker container that checks with `cron` every 20 minutes your current performance list as an HTML table from the iCMSs.
Using [Scrapy](https://scrapy.org) this script logs in with your credentials runs automatically through a rocky road of links.
Then it will compare to the last crawl if there are differences in grading. 
If there are, it will inform you immediately via Telegram notification using [Python-Telegram-Bot](https://github.com/python-telegram-bot/python-telegram-bot).
Within this message you'll receive a `png`-image of your performance list rendered with [`imgkit`](https://pypi.org/project/imgkit/).


## Overview
  * [Installation & Usage](#installation---usage)
    + [Set Credentials](#set-credentials)
    + [Run Container](#run-container)
  * [Logs](#logs)
  * [Manual Crawling](#manual-crawling)
  * [Without Docker](#without-docker)
  * [Background](#background)
  * [QISPOS CSS](#qispos-css)
  * [Links:](#links-)

## Installation & Usage

### Set Credentials

HS-Login:
```
$ nano icms_crawler/login_credentials.py

# LOGIN_NAME='XXX-XXX-XX'
# LOGIN_PW='undercover?'
```
! Ja, der Login der Hochschule. Lasst das Script also nur laufen (und die Dateien liegen) auf Maschinen, denen Ihr vertraut ;)

Telegram Token and Chat-ID:
```
$ nano icms_crawler/notify_with_telegram.py
# CHAT_ID='000000000'
# TOKEN='0000000000:0000000000000000000000000000000000'
```
The token you'll get from the _Botfather_ (See Telegram's [HowTo](https://core.telegram.org/bots#3-how-do-i-create-a-bot)).

Since you've got a bot, write it a message an check https://api.telegram.org/bot[HTTP-TOKEN]/getUpdates .
You will see your chat-id (`"id":123...`).

### Run Container

```
$ docker-compose up -d
```
The python-files (`icms_craler/`) are mounted as a Docker-volume.
This way you can make changes in scripts without the need of restarting the container.
Your current performance will be placed in folder `icms_crawler/results/` you can easily see.

After the audit period we should not annoy the servers of the HSH.
So turn down the container (from same directory) with:
```
$ docker-compose down
```

## Logs

The Container placing its logs internally in `/var/log/icms_crawler.log`.
To view them, first check your current containers
```
$ docker ps
```
and look for the ID of the `icms_crawler`-contrainer.
Then run 
```
$ docker exec <container-id> cat /var/log/icms_crawler.log
```
If logs getting too long, choose `tail` instead of `cat`.

## Manual Crawling

If there's the need of crawling more often than every 20 minutes 😅:
```
docker exec <container-id> python3 main.py
```

## Without Docker

Sure you can run `ICMSSpider` without Docker.
Therefore you'll need to install the dependencies in `requirements.txt`:
```
pip3 install --no-cache-dir -r requirements.txt
```

Now you can start the Scrapy Spider on demand:
```
python3 icms_crawler/main.py
```

## Background
Im iCMS (integriertes Campus Management System der Hochschule Hannover) "holt man sich seine Noten ab".
Unter der Haube nutzt es (QIS)POS (https://de.wikipedia.org/wiki/Hochschul-Informations-System), welches als Schutz vor CSRF das direkte Abrufen der Leistungsübersicht nicht erlaubt. Man muss einem bestimmten (gefühlt ewig langen) Pfad folgen…

Man startet auf  
http://icms.hs-hannover.de/.  
Aber egal, von wo man kommt, wird man auf  
https://icms.hs-hannover.de/qisserver/rds?state=user&type=0  
weitergeleitet.
Hier gibt man seine Anmeldedaten im POST-Formular an, mit den Parametern (kein Witz !) "`asdf`" für Benutzerkennung und "`fdsa`" für Passwort (und natürlich "`submit=Anmelden`" (ohne geht’s nicht)).
Und kommt auf:  
https://icms.hs-hannover.de/qisserver/rds?state=user&type=1&category=auth.login&startpage=portal.vm 

Hier klickt man nun auf "Prüfungen", den Zugang zum eigentlichen POS.
```
<a href="https://icms.hs-hannover.de/qisserver/rds?state=change&amp;type=1&amp;moduleParameter=studyPOSMenu&amp;nextdir=change&amp;next=menu.vm&amp;subdir=applications&amp;xml=menu&amp;purge=y&amp;navigationPosition=functions%2CstudyPOSMenu&amp;breadcrumb=studyPOSMenu&amp;topitem=functions&amp;subitem=studyPOSMenu" class="visited " target="_self">Prüfungen</a>
```
Ausreichend eindeutig ist hier der XPath: `//*[contains(@href, 'moduleParameter=studyPOSMenu')]`

Vermutlich liegt bei der HsH noch eine WAF davor, die sämtliche Links mit einer Sitzung-ID versieht (in diesem Beispiel "`asi=JJ2xAKmILbgrerCT19KM`").
Also finden wir alle notwendigen Links, unabhängig dieser "asi"-ID mit signifikanten XPathes.

Im folgenden Menü nun auf "Notenspiegel"
```
<a href="https://icms.hs-hannover.de/qisserver/rds?state=notenspiegelStudent&amp;next=tree.vm&amp;nextdir=qispos/notenspiegel/student&amp;menuid=notenspiegelStudent&amp;breadcrumb=notenspiegel&amp;breadCrumbSource=menu&amp;asi=JJ2xAKmILbgrerCT19KM" title="" class="auflistung">Notenspiegel</a>
```
XPath: `//*[contains(@href, 'qispos/notenspiegel/student&menuid=notenspiegelStudent')]`

Und hier dann auf das (i)-Image, um zur Notenübersicht zu gelangen:
```
<a href="https://icms.hs-hannover.de/qisserver/rds?state=notenspiegelStudent&amp;next=list.vm&amp;nextdir=qispos/notenspiegel/student&amp;createInfos=Y&amp;struct=auswahlBaum&amp;nodeID=auswahlBaum%7Cabschluss%3Aabschl%3D90%2Cstgnr%3D1&amp;expand=0&amp;asi=JJ2xAKmILbgrerCT19KM#auswahlBaum%7Cabschluss%3Aabschl%3D90%2Cstgnr%3D1" title="Leistungen für Abschluss 90 Master anzeigen"><img src="/QIS/images//information.svg" alt="Leistungen für Abschluss 90 Master anzeigen" title="Leistungen für Abschluss 90 Master anzeigen"></a>
```
XPath: `//*[contains(@href, 'qispos/notenspiegel/student&createInfos=Y')]`

In der ganzen Seite sind noch abhängig von der ID Kommentare und Links versteckt. 
Ich isoliere zunächst die Tabelle mit den Noten und entferne danach alle Links _dadrin_.
Die entstehende Tabelle lässt sich nun mit vorherigen Versionen vergleichen (unabhängig von der Session).

Es werden nur die Dateien verglichen bisher keine Interpretation der Noten vorgenommen.

## QISPOS CSS

Um die Tabelle etwas aufzuhübschen habe ich das CSS einfach von der HS "geklaut". 
Hier waren noch drei Imports drin, die ich auskommentiert hab, damit `imgkit` keine Fehler wirft.
Außerdem müssten wir bei jedem Crawl weitere 59KB von den HS-Servern herunterladen.
Um die HS-Server hier ein bisschen zu entlasten, habe ich diese CSS als Kopie hier im repo.
Der öffentliche Link, von dem es erreichbar ist:  
https://icms.hs-hannover.de/qisserver/pub/QISDesign_HSH.css  
Es ist also eh public und jeder könnte es sich besorgen ;)

## Links
- One nice overview on how to setup an own telegram-bot:  
	https://www.christian-luetgens.de/homematic/telegram/botfather/Chat-Bot.htm
- Scrapy:  
	https://scrapy.org
- Python-Telegram-Bot:  
	https://github.com/python-telegram-bot/python-telegram-bot
- `imgkit`: Python 2 and 3 wrapper for `wkhtmltoimage`:  
	https://pypi.org/project/imgkit
- Last but not least, the iCMS of the HSH:  
	https://icms.hs-hannover.de
