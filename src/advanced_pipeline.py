# -*- coding: utf-8 -*-

# -- Sheet --

# # 1) Datenaufnahme
# Import der zu verwendeten Libraries für die weitere Datenverarbeitung und -bereinigung.


# ## 1.1) Pakete laden


%config IPCompleter.greedy=True

#Einlesen relevanter Pakete

import pandas as pd # Nutzung der Datenstruktur Dataframe und zugehöriger Methodiken
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator # Verwendung zur Erstellung von Wordclouds 
                                                                # zur Visualisierung
import matplotlib.pyplot as plt # Notwendig zur Visualisierung der Wordcloud
import string # Verwendung zur Erstellung von Satzzeichen-Listen

# ## 1.2) Rohdaten in Dataframe einlesen


filepath = "chat_data_tobi_HR_202101_utf16.csv"
filepath2 = "conversations_ gathered.csv" 
chats = pd.read_csv(filepath2,delimiter=";", encoding='utf-16') # CSV einlesen

chats.info() #Datenübersicht

chats.shape #Anzahl Zeilen und Spalten anzeigen

chats.sample(3).T # Top 3 Einträge in sample Ansicht

# ## 1.3) Datenvalidierungen


chats.nunique() #Überprüfung auf Anzahl einzigartiger Werte in den jeweiligen Feldern

# Da der gesamte Datensatz 689 Einträge besitzt, wird deutlich, dass Spalten mit dieser Zahl an unterschiedlichen Einträgen offenbar einzigartige Werte beinhalten, welche der Zeile eindeutig zuordbar sind. 
# 
# Werte mit zwei Einträgen scheinen boolsche Werte zu sein, da diese lediglich 0 und 1 enthalten
# 
# Alle Werte mit lediglich einem Eintrag werden für die spätere Analyse, aufgrund fehlender Unterscheidbarkeit, keinen Mehrwert liefern und können voraussichtlich entfernt werden
# 
# Ausgenommen sind Zeit bzw. Datumsangaben, welche gesondert behandelt werden sollten.


# # 2) Daten bereinigen
# 
# Im Folgenden wird der Datensatz um anonymisierte, oder nicht relevante Werte, wie oben beschrieben, bereinigt.


chats_original = chats # Backup Dataframe erstellen, falls später wieder der Originalzustand benötigt wird

chats.drop(["Domain",
            "Status",
            "User Name",
            "User Email",
            "User External Uid",
            "Custom Metrics"],
            axis = 1,
            inplace= True) # Spalten mit nur einem Wert entfernen

chats.sample(3).T

# ## 2.1) Entfernen von nicht relevanten Spalten im DataFrame
# 
# Info:
# 
# Abandonded
# 
# 0: die Konversation wurde an einen Agenten weitergeleitet.
# 
# 1: der Mitarbeiter hat das Chat Fenster geöffnet, aber nichts geschrieben. Die Anfrage wurde somit an keinen Agenten weitergeleitet.
# 
# 2: Agent konnte den Chat nicht entgegennehmen
# 
# 3: Der Mitarbeiter hat, nachdem sich der Agent gemeldet hat, nicht reagiert. Daher wurde der Chat dann geschlossen.


chats.drop(["Created",
                    "Finished",
                    "Channel",
                    "Primary Agent Handle Time",
                    "Primary Agent Answer Speed",
                    "Pickup SLA Violation",
                    "Escalated",
                    "Escalation Queue",
                    "Abandoned",
                    "Amelia Handled",
                    "Amelia Abandoned",
                    "Agent Handled",
                    "Agent Abandoned",
                    "Escalate Abandoned",
                    "Executed BPNs",
                    "Total Handle Time"], 
                    axis = 1,
                    inplace= True)


chats

chats.head (3)

chats.Transcript[1]

# # 3) Textvorverarbeitung auf Basis der Chat Transkripte (Chats["Transkript"])
# 
# Im Weitere wird nunmehr ausschließlich der Textkorpus der einzelnen Chats betrachtet. Die verbleibenden anderen Spalten "Conversation ID" und "Total Handle Time" dienen der Zuordnung und Qualifizierung der einzelnen Chat-Protokolle, werden jedoch vorerst nicht weiter im Skript betrachtet.


# ## Schritt 1) Trennung der Chatpassagen
# 
# Einfügen einer neuen Spalte "transcript_splitted" in den DataFrame, welche eine Liste der durch "||" getrennten Chatpassagen enthält.
# 
# Zudem werden daraufhin, Textpassagen welche vom Chatbot "TOBI" kommen, gelöscht.


#Vergleich der Größe des Dataframe vor und nach Entfernen von Transkripten ohne Userinteraktion

chats.shape # (3669,2)


# Definition einer Methode zum Trennen der Textpassagen
def split_transcript(rowinSeries):
    
   splitted_list = rowinSeries.split("||") # Splitte das Transkript nach jedem "||" auf und erzeuge eine Liste mit den Teilelementen
    
   return splitted_list


chats["transcript_splitted"] = chats["Transcript"].apply(split_transcript)

# ## Schritt 2) Entfernen von Chats ohne Userinteraktion


def remove_tobi_chats(rowinSeries):
    
   rowinSeries = list(filter(lambda item: not item.startswith('TOBi'), rowinSeries))
   if len(rowinSeries) > 1:
       return rowinSeries

chats["transcript_splitted"] = chats["transcript_splitted"].apply(remove_tobi_chats)

chats.dropna('index','any', inplace=True) #Entferne alle Zeilen aus dem DF, welche leere Elemente enthalten

# ## Schritt 3) Zurücksetzen des Index
# 
# Zurücksetzen des Index. Durch die in Schritt 2) durchgeführten Löschungen, muss der Index auf Basis der neuen Größe des DF zurückgesetzt werden.


chats.reset_index(drop=True, inplace=True)

#Vergleich der Größe des Dataframe vor und nach Entfernen von Transkripten ohne Userinteraktion

chats.shape #(2046,3)

# ## [Zwischenschritt] Visualisierung: Zusammenfügung der Daten in einzelne String-Variable
# 
# Für eine erste Analyse der Daten werden alle übrig gebliebenen Chatpassagen in einen großen String geschrieben, um einen ersten Überblick über die enthaltenen Wörter zu erhalten




# #### Visualisierung: Daten zur Ersteinsicht mit Wordcloud darstellen
# 
# Hierzu wird das Modul Wordcloud verwendet, um ein erstes Bild der Daten zu generieren.


# #### 1. Wordcloud generieren


text = ""
for zeile in chats["transcript_splitted"]:
    text += str(zeile)

#Entwicklung des Datenkorpus
zwischenstand1 = len(text)
print(zwischenstand1)

wordcloud = WordCloud(width= 1280, height=800,max_words=100, background_color= "white").generate(text)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
wordcloud.to_file("Wordcloud_zwischenstand1.png")

# #### Visualisierung: Fazit
# 
# Anhand der Wordcloud wird schnell klar, dass diverse weitere Bereinigungen notwendig sind, um einen ersten Blick auf mögliche Kategorien zu erhalten. 
# 
# - Besonders Wörter, welche nur eine syntaktische, aber keine inhaltliche Bedeutung haben, stechen hevor (Stopwords)
# - Zudem gehören die Namen der Support-Agents noch zu den häufigsten Wörtern. Diese bringen ebenfalls keinen Mehrwert in unserer Fragestellung und müssen entfernt werden.


# ## Schritt 4) Trennung der Mitarbeiterchats von den Agentchats in neue Spalte
# 
# Ziel des Skriptes ist die Klassifikation einer Useranfrage bevor ein Agent hinzugeschaltet wird. Um dies zu erreichen, sind für eine weitere Textanalyse lediglich die Textpassagen relevant, welche VOR beitritt des Agents vom Mitarbeiter abgesendet werden. Deshalb wird im nächsten Schritt das Transcript auf die erste Anfrage des Mitarbeiters reduziert.



#Als relevante Chatanfrage des Mitarbeiters kann in den vorliegenden Daten die zweite Anfrage des Mitarbeiters verwendet werden.
# Die erste Antwort des Mitarbeiters ist stets "Ja" und ist als Antwort auf die Frage nach weiteter Unterstützung des Bots.

chats["user_transcript"] = chats.transcript_splitted.apply(lambda listinrow: listinrow[1])

#Testprint
print(chats.user_transcript)

wordcloud = WordCloud(width= 1280, height=800,max_words=100, background_color= "white").generate(" ".join(chats.user_transcript))
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
wordcloud.to_file("Wordcloud_zwischenstand2.png")

#entwicklung des datenkorpus
zwischenstand2 = len(" ".join(chats.user_transcript))
print(zwischenstand2)

y = [zwischenstand1,zwischenstand2] # y-Werte
x = ["zws1","zws2"] # x-Werte
xy = {'Zwischenstand':x,'Anzahl Zeichen':y}
df_xy = pd.DataFrame(xy)
print(df_xy)


plt.title("Zwischenstand")
plt.yscale("linear")
plt.plot(x,y,'o-',color='black')
plt.bar(x,y,width= 0.2 )  
plt.savefig("Barplot_zws1-2.png")             
plt.show()

chats[["Conversation Id","user_transcript"]].sample(5)

# ## Schritt 5) Cleaning: Entfernen von kontextbasierten Phrasen (vor Tokenization)
# 
# Im folgenden werden spezielle Phrasen entfernt, welche für die weitere Schlagwortanalyse keinen Mehrwert bieten.
# 
# - Entfernen von "Firstname", "Lastname", anonymisierten Telefonnummern "+XX (X) XXX XXX XXXX", Zeitstempel


#Entfernen von Kombinationen von "Firstname Lastname"
chats.user_transcript = chats.user_transcript.str.replace(r"(?i)Firstname\sLastname|Firstname|Lastname"," ", regex = True)

#Entfernen der Zeitstempel
chats.user_transcript = chats.user_transcript.str.replace(r"\[.*\]", "", regex = True)

#Entfernen von anonymer Telefonnummer
chats.user_transcript = chats.user_transcript.str.replace(r"(?i)\+*XX\s\(*X\)*\sXXX\sXXX\sXXXX"," ", regex = True)

#Entfernen von weiteren anonymisierten Daten
chats.user_transcript = chats.user_transcript.str.replace(r"(?i)xx+"," ", regex = True)

#Entfernen von weiteren anonymisierten Daten
chats.user_transcript = chats.user_transcript.str.replace(r"(?i)\sx\s"," ", regex = True)

# rex_FirstnameLastname = re.compile(r"Firstname Lastname")  #Isoliere den Zeitstempel mit der Regular Expression 
# chats.transcript_merged.apply(lambda stringtext: re.sub(rex_FirstnameLastname,"",stringtext)) # klappt nicht

wordcloud = WordCloud(width= 1280, height=800,max_words=100, background_color= "white").generate(" ".join(chats.user_transcript))
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
wordcloud.to_file("Wordcloud_zwischenstand3.png")

#entwicklung des datenkorpus
zwischenstand3 = len(" ".join(chats.user_transcript))
print(zwischenstand3)

y = [zwischenstand1,zwischenstand2, zwischenstand3] # y-Werte
x = ["zws1","zws2","zws3"] # x-Werte
xy = {'Zwischenstand':x,'Anzahl Zeichen':y}
df_xy = pd.DataFrame(xy)
print(df_xy)



plt.title("Zwischenstand")
plt.yscale("linear")
plt.plot(x,y,'o-',color='black')
plt.bar(x,y,width= 0.4 ) 
plt.savefig("Barplot_zws1-3.png")             
plt.show()

# ## Schritt 6) Normalisierung: lowercase
# 
# Für eine weitere Harmonisierung, werden alle Chatpassagen in Kleinschreibung konvertiert. Da unsere Analyse primär auf Schlagworterkennung abzielt, ist die Groß- und Kleinschreibung weniger relevant.


chats.user_transcript = chats.user_transcript.apply(str.lower)

# ## Schritt 7) Satzzeichen entfernen
# 
# Für eine Tokenisierung mit dem Ziel der Extraktion von Stichwörtern, sind die Satzzeichen irrelevant. Deshalb werden diese im folgenden Schritt entfernt.


exclist = string.punctuation + string.digits # Erstellt eine List von Satzzeichen und Zahlen welche 
                                             #im weiteren entfernt werden sollen

translation_table = str.maketrans('', '', exclist)  # Erstellt ein Dictionary Object, welches als Mapping Tabelle verwendet wird (a wird zu b, x wird zu y)

chats.user_transcript = chats.user_transcript.str.translate(translation_table) # Führt die Übersetzung anhand 
                                                                                #des Dictionaries durch

chats.user_transcript[1:5]

chats[["Conversation Id","user_transcript"]].head(5)

wordcloud = WordCloud(width= 1280, height=800,max_words=100, background_color= "white").generate(" ".join(chats.user_transcript))
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
wordcloud.to_file("Wordcloud_zwischenstand4.png")

#entwicklung des datenkorpus
zwischenstand4 = len(" ".join(chats.user_transcript))
print(zwischenstand4)

y = [zwischenstand1,zwischenstand2, zwischenstand3, zwischenstand4] # y-Werte
x = ["zws1","zws2","zws3","zws4"] # x-Werte
xy = {'Zwischenstand':x,'Anzahl Zeichen':y}
df_xy = pd.DataFrame(xy)
print(df_xy)



plt.title("Zwischenstand")
plt.yscale("linear")
plt.plot(x,y,'o-',color='black')
plt.bar(x,y,width= 0.4 )  
plt.savefig("Barplot_zws1-4.png")             
plt.show()

# # 4) Advanced NLP mit spaCy 3.0


# ## Schritt 1) Initialisierung und Konfiguration SPACY


# Import Package spaCy
import spacy
# Import Package Subprocess, zum Laden von spaCy trained pipelines
import subprocess

trained_pipeline_trf = "de_dep_news_trf"

# Laden der spaCy pretrained pipeline
print(subprocess.getoutput("python -m spacy download " + trained_pipeline_trf))

#Referenzvariable für spaCy einführen
nlp=spacy.load(trained_pipeline_trf)

# ## Schritt 2) Erstellen von kontextbasierten Stopword Listen


# ### Schritt 2.1) Liste für Höflichkeitsformen


import pandas as pd
#Einlesen der Liste der Höflichkeitsformen in Dataframe
thankyou_raw=pd.read_csv("hoeflichkeitsformen.csv",encoding="utf-8")

#Einführen von Referenzvariable für finale Liste
thankyou = []

#Vorverarbeitung der greetings-Liste: Kleinschreibung aller texte
for line in thankyou_raw["höflichkeitsform"]:
   thankyou.append(line.lower())

#Testprint
print(thankyou)

# ### Schritt 2.2) Liste für Begrüßungsformen


#Einlesen der Begrüßungsliste in Dataframe
greetings_raw=pd.read_csv("Greetings.csv", delimiter=";", encoding= 'latin-1')

#Einführen von Referenzvariable für finale Liste
greetings=[]

#Vorverarbeitung der greetings-Liste: Kleinschreibung aller texte
for line in greetings_raw["Greetings"]:
      greetings.append(line.lower())

#Testprint
print(greetings)

# ### Schritt 2.3) Liste von kontextspezifischen Begriffen der Vodafone GmbH


#Einlesen der Liste in Dataframe
vodafone_words_raw=pd.read_csv("Vodafone_words.csv", delimiter=";", encoding= 'latin-1')

#Einführen von Referenzvariable für finale Liste
vodafone_words=[]

#Vorverarbeitung der greetings-Liste: Kleinschreibung aller texte
for line in vodafone_words_raw["Words"]:
      vodafone_words.append(line.lower())

#Testprint
print(vodafone_words)

# ### Schritt 2.4) Liste von Datums und Zeitangaben 


#Einlesen der Liste in Dataframe
date_and_time_raw=pd.read_csv("date_and_time.csv", delimiter=";", encoding= 'latin-1')

#Einführen von Referenzvariable für finale Liste
date_and_time=[]

#Vorverarbeitung der greetings-Liste: Kleinschreibung aller texte
for line in date_and_time_raw["Words"]:
      date_and_time.append(line.lower())

doc_date_time = nlp(" ".join(date_and_time))

for token in doc_date_time:
    date_and_time.append(token.lemma_)
      

#Testprint
print(date_and_time)

# ## Schritt 3) Erstellung Pipeline Methode



merged_stopwords = thankyou + date_and_time + greetings + vodafone_words


def apply_pipeline(textinput):
    doc = nlp(textinput)
    
    nomen = []

    for token in doc:
        if token.pos_ == "NOUN":
            if token.text not in merged_stopwords:
                if token.lemma_ not in merged_stopwords:
                    nomen.append(token.lemma_)
    
    return nomen


   

# ## Schritt 4) Anwenden der Pipeline auf Datensatz


chats["Nomen"] = chats.user_transcript.apply(apply_pipeline)

AlleNomen = []

for liste in chats["Nomen"]:
    for item in liste:
        AlleNomen.append(item)

#Entwicklung des datenkorpus
zwischenstand5 = len(" ".join(AlleNomen))
print(zwischenstand5)

y = [zwischenstand1,zwischenstand2, zwischenstand3, zwischenstand4,zwischenstand5] # y-Werte
x = ["zws1","zws2","zws3","zws4","zws5"] # x-Werte
xy = {'Zwischenstand':x,'Anzahl Zeichen':y}
df_xy = pd.DataFrame(xy)
print(df_xy)



plt.title("Zwischenstand")
plt.yscale("linear")
plt.plot(x,y,'o-',color='black')
plt.bar(x,y,width= 0.4 ) 
plt.savefig("Barplot_zws1-5.png")             
plt.show()

# # 5) Counter erstellen


from collections import Counter
counter = Counter(AlleNomen)
print(counter)

print(type(counter))

# nice about the counter is that it can be incrementally updated with a list of tokens of a second document:

#more_tokens = tokenize("Hallo, kannst du mir bitte Informationen zum Thema: katastrophenhilfe hochwasser geben")
#counter.update(more_tokens)
#print(counter)

df = pd.DataFrame.from_dict(counter, orient='index', columns=['freq'])
df = df.sort_values(['freq'], ascending=False)
df.index.name = 'token'
df

print("Fertig")

# # 6) Bereinigte Textdaten visualisieren
# 
# Nachdem die Tokenisierung und Vorverarbeitung abgeschlossen ist, können erste Visualisierungen der berenigten Chatpassagen durchgeführt werden


wordcloud = WordCloud(width= 1280, height=800,max_words=100, background_color= "white").generate(" ".join(AlleNomen))
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
wordcloud.to_file("wordcloud_zwischenstand5.png")

import nltk

print(len(AlleNomen))
fdist_spacy = nltk.FreqDist(AlleNomen)


top100 = fdist_spacy.most_common(100)

fdistplot = fdist_spacy.plot(30)

top100a = df.head(100)
top100a.to_csv("top100a.csv")

chats.to_csv("data_after_spacy_step6.csv", encoding= 'utf-16')

# 


# # **Deskriptive** Analyse: Visualiserung nach Konvention


# Barplot für Kategoriale Daten
# 
# Linecharts für Zeitreihen und Seqeunzen


ax = df.head(20).plot(kind='barh', width=0.85)
ax.invert_yaxis()
ax.set(xlabel='Frequency', ylabel='Token', title='Top Words')

ax.get_figure().savefig("topwords.png")

chats.head(3)

chats_result = chats.drop("transcript_splitted", axis=1)

chats_result.Nomen = chats_result.Nomen.apply(lambda liste: ", ".join(liste))

chats_result.head(3)

