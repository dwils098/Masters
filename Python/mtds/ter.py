import worker_process as wp 




string_data = """
<DOC>
<DOCNO> AP900103-0077 </DOCNO>
<FILEID>AP-NR-01-03-90 1240EDT</FILEID>
<FIRST>r i AM-Honecker     01-03 0311</FIRST>
<SECOND>AM-Honecker,0322</SECOND>
<HEAD>Report Honecker May be Moved to Monastery For His Safety</HEAD>
<HEAD>With AM-East Germany, Bjt</HEAD>
<DATELINE>HAMBURG, West Germany (AP) </DATELINE>
<TEXT>
   Former East German leader Erich
Honecker may be moved to a monastery to protect him from a possible
lynching by enraged citizens, a newspaper said Wednesday.
   In a front-page story, the mass-circulation Bild newspaper said
``Lynch Danger _ Church Wants to Grant Honecker Asylum.''
   Since Honecker was ousted Oct. 18, the former Communist Party
leader and other party officials have come under investigation for
charges of corruption and living in luxury at the cost of the state.
   In December, seven former Politburo members were arrested, and
Honecker was placed under house arrest in the government housing
area of Wandlitz outside East Berlin.
   The Wandlitz homes, including the one in which Honecker still
lives, are being converted to a medical rehabilitation center for
children. Honecker is expected to be forced out of the compound in
February.
   Bild said it had information that ``Lutheran and Catholic church
sources have offered Honecker _ who is threated by public rage _
protection and refuge.''
   ``This is the only possibility to protect Erich Honecker from
the rage of the East German people,'' Bild quoted the source as
saying.
   It was the churches that became the venues for gathering of
pro-democracy groups that eventually brought the overthrow of his
18-year leadership.
   In recent weeks, East German groups have called for punishing
Honecker and for moving him to smaller quarters ``with an outside
toilet,'' Bild said.
   The current leadership fears that in such a situation, Honecker
``might be attacked and become a victim of lynch justice,'' Bild
said.
   Honecker, 77, underwent gall-bladder surgery in August, and East
German media reported he remains seriously ill.
   ``Sources say the ailing ex-leader may be placed in a
church-operated home for the elderly, or even in a monastery,''
Bild reported.
</TEXT>
</DOC>
"""                                                                                                                                                                                                            

from nltk import sent_tokenize
token_text=sent_tokenize(string_data)
text_sen =[]
for sen in token_text:
    sen = sen.replace('\n',' ')
    text_sen.append(sen)


print text_sen


title_raw = text_sen[0]

import re

result =  re.search('<HEAD>(.*)</HEAD>',title_raw)
title = result.group(1) 

if '<HEAD>' in title:
    title =  re.sub('</HEAD>(.*)<HEAD>',' ',title)

if '<TEXT>' in title_raw:
    result_2 = re.search('<TEXT>(.*)', title_raw)
    remains = result_2.group(1)
else: 
    remains = ""

if remains == "":
    #look at the second sentence
    if '<TEXT>' in text_sen[1]:
        result_2 = re.search('<TEXT>(.*)', text_sen[1])
        remains = result_2.group(1)
        text_sen[1] = remains
        del text_sen[0]
else:
    text_sen[0] = remains
del text_sen[-1]

print "Title = " + title
print "Remains = " + remains


print text_sen
