# Licenta-Necsoiu-Iasmina
Proiect de diploma. 
Sistem automat de monitorizare si control al debitului unei perfuzii intravenoase utilizand Arduino

Autor: Necsoiu Iasmina-Teodora
Coordonator: Sl.dr.ing. Alexandra-Iulia Szedlak-Stinean
Facultatea de Automatica si Calculatoare, UPT, Sesiunea Iunie 2026




Repository: https://github.com/iasmina7/Licenta-Necsoiu-Iasmina






DESCRIEREA PROIECTULUI

Proiectul implementeaza un sistem automat de monitorizare si control al debitului unei perfuzii intravenoase, bazat pe platforma Arduino Uno. Sistemul detecteaza picturile din camera de perfuzie prin intrerupere hardware, calculeaza debitul la fiecare 10 secunde, il compara cu un setpoint setat de utilizator si actioneaza o pompa peristaltica pentru corectarea automata a debitului. O aplicatie web separata, bazata pe Flask si SQLite, colecteaza datele transmise prin portul serial si le afiseaza intr-un dashboard accesibil din browser.


FISIERELE DIN REPOSITORY

In repository se gasesc urmatoarele fisiere:

app.py este serverul Flask, care se ocupa de citirea portului serial, interactiunea cu baza de date si expunerea datelor catre browser.

index.html este interfata web, adica dashboardul pe care il deschizi in browser.

cod_setup_arduino.ino este codul sursa incarcat pe placa Arduino Uno.

iv_database.db este baza de date SQLite. Se genereaza automat la prima rulare, dar am inclus-o si in repository ca referinta.


ATENTIE, PAS OBLIGATORIU INAINTE DE RULARE

Flask cauta fisierele HTML intr-un director numit templates. Din cauza limitarilor platformei de upload, fisierele au fost incarcate direct in radacina repository-ului, fara structura de directoare. Inainte de a rula aplicatia, trebuie creat manual acest director si mutat index.html in el.

Dupa descarcarea fisierelor, structura trebuie sa arate asa:

app.py
cod_setup_arduino.ino
iv_database.db
templates/
    index.html

Pasii sunt urmatorii: descarcati toate fisierele din repository, creati un folder nou numit exact templates in acelasi director cu app.py, mutati index.html in interiorul folderului templates, apoi rulati aplicatia din directorul care contine app.py.


COMPONENTE HARDWARE NECESARE

Arduino Uno R3, senzor optic IR FC-51, modul releu 5V un canal, pompa peristaltica 12V INTLLAB DP-DIY, LCD 16x2 cu modul I2C la adresa 0x27, buzzer activ, potentiometru 10kΩ, sursa externa 12V 2A, breadboard si fire jumper.


CODUL ARDUINO

Biblioteci necesare: LiquidCrystal_I2C de Frank de Brabander, instalabila din Arduino IDE Library Manager. Wire este inclusa implicit in Arduino IDE.

Pasi de compilare si incarcare:
Deschideti Arduino IDE 2 si fisierul cod_setup_arduino.ino. Selectati placa din Tools, Board, Arduino Uno. Selectati portul din Tools, Port, COMx, verificati in Device Manager pe Windows care este portul corect. Apasati Upload.

Pentru verificare, deschideti Serial Monitor si setati baud rate la 115200. La fiecare 10 secunde ar trebui sa apara o linie de forma:
Setpoint: 50 pm | Flux: 8/10s | Debit: 48 pm | Stare: OK | Pompa: OFF | Buzzer: OFF


APLICATIA WEB

Cerinte: Python 3.8 sau mai nou si Arduino conectat prin USB.

Instalare dependente:
pip install flask pyserial

Configurare port serial: deschideti app.py si verificati linia SERIAL_PORT. Valoarea implicita este COM5. Modificati daca Arduino-ul este detectat pe alt port. Portul exact poate fi verificat in Device Manager, sectiunea Ports.

Important: Arduino IDE trebuie sa fie complet inchis inainte de a lansa aplicatia. Portul serial poate fi folosit de un singur program la un moment dat.

Lansare:
python app.py

Daca totul este configurat corect, in consola apare mesajul OK Conectat la COM5 si serverul porneste la adresa http://127.0.0.1:5000.

Deschideti browserul la aceasta adresa. Dashboardul afiseaza parametrii curentii ai sistemului, datele pacientului, statistici pe stari si istoricul ultimelor 20 de evenimente inregistrate.

Pentru a opri aplicatia apasati Ctrl+C in fereastra de terminal.


NOTE

Sistemul fizic functioneaza independent de aplicatia web. Daca aplicatia nu ruleaza, Arduino continua sa monitorizeze si sa controleze debitul in mod normal.
