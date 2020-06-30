# iCMS Personal Grades Crawler HsH

Using [Scrapy](https://scrapy.org) this script logs into iCMS with your credentials and crawls current performance list as an HTML table.
Compared to the last crawl this script will let you know, if there are differences in grading.

## Installation / Usage
```
#install scrapy https://scrapy.org
$pip3 install scrapy

#set your login credentials
$nano login_credentials.py
```
   Ja, der Login der Hochschule. Lasst das Script also nur laufen (und die Dateien liegen) auf Maschinen, denen Ihr vertraut ;)

```
#run in same dir
$scrapy runspider icms_crawler.py
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
Ich isoliere zunächst die Tabelle mit den Noten und entferne danach alle Links darin.
Die entstehende (weniger schöne) Tabelle lässt sich nun mit vorherigen Versionen vergleichen (unabhängig von der Session).

Es werden nur die Dateien verglichen bisher keine Interpretation der Noten vorgenommen.
