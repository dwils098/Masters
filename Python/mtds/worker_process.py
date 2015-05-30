# This file will contain the logic for the worker nodes.
import rethinkdb as r
import base64

# Parsing imports
import re
import nltk.data
import operator
import heapq
import math
import random
import copy
import numpy as np
import time
import os

from nltk.corpus import stopwords
from bisect import bisect


#--------------------------------Task Functionalities ----------------------------------------

# Given a ip, port; retrieve the data from the database (node).
def retrieveData(task_obj, params):

    ip = params[0]
    port = params[1]
    db_name = params[2]
    table_name = params[3]
    key = params[4]
    auth_key = params[5]
    
    # create a connection object to the database
    conn = r.connect(host = ip,
                     port = port,
                     db = db_name)
                     #auth_key = auth_key)
    
    # create the query
    query = r.db(db_name).table(table_name).get(key)
    
    # execute the query, returns a dict of the fields and values.
    results = query.run(conn)

    # in our case the fields are :
    # uuid
    # type_id
    # filename
    # file (in binary b64)
    file_id = results['uuid']
    filename = results['filename']
    file_data = base64.b64decode(results['file']) 
    
    task_obj.results = "FileID: " + file_id + "\n" +  "Filename:  " + filename + "\n" + "Data: " +file_data
    
    # here we will call the genetic algorithm, and process it 
    title, sentences, numSen = singleReadDoc(filename, file_data)
    token_title, token_sentenceDoc, tokee = sanitize(sentences, title)
    sim_vec, weight_vec = docStats(token_sentenceDoc, token_title)
    
    # summary size
    sum_size = numSen/2
    
    # population size
    pop_size = 100
    
    # coefficients
    coeff = [3,3,3]

    cand_summary = geneticAlgorithm(pop_size, 
                                    sum_size, 
                                    coeff, 
                                    token_sentenceDoc,
                                    sim_vec,
                                    weight_vec)


    summary = ""
    summary.append(title)
    summary.append("\n")
    #build back the summary 
    for i in cand_summary:
        summary.append(sentences[i])
        summary.append(" ")


    # send the results back to the db
    r.db(db_name).table_create('results').run(conn)
    
    response_query = r.db(db_name).table('results').insert({
        "uuid" : key,
        "summary_binary" : cand_summary,
        "summary" : summary
    }).run(conn)
    
    #return file_id, filename, file_dat

def retrieveData_postprocessing(task_obj, params):
    ip = params[0]
    port = params[1]
    db_name = params[2]
    table_name = params[3]
    key = params[4]
    auth_key = params[5]
    
    # create a connection object to the database
    conn = r.connect(host = ip,
                     port = port,
                     db = db_name)
                     #auth_key = auth_key)
    
    # create the query
    query = r.db(db_name).table(table_name).get(key)
    
    # execute the query, returns a dict of the fields and values.
    results = query.run(conn)
    
    print "retrieveDataPostProcessing: " + str(results)

#-------------------------------Text PARSING LOGIC ------------------------------------------
def readFBIS(data):
    titleFound = False
    textFlag = False
    kwFlg = False
    pFlag = False
    pFlagSen = False
    pFlagKW = False
    
    title = ""
    sentence = ""
    word = ""
    keywords = []
    sentences = []
    
    for line in data:
        if "<TI>" in line and not "</TI>" in line:
            #print "HL", line
            titleFound = True
            ine = re.sub(r'<[a-zA-Z0-9]{1,}>', "",line)
            line = re.sub(r'[\n|\r|\t|]{1,}', " ",line)
            line = re.sub(r'[\s]{2,}', "",line)
            title = title + " " + line
        elif "<TI>" in line and "</TI>" in line:
            line = re.sub(r'<[a-zA-Z0-9]{1,}>', "",line)
            line = re.sub(r'</[a-zA-Z0-9]{1,}>', "",line)
            line = re.sub(r'[\n|\r|\t|]{1,}', " ",line)
            line = re.sub(r'[\s]{2,}', "",line)
            title = line
            titleFound = False
        elif "</TI>" in line:
            line = re.sub(r'</[a-zA-Z0-9]{1,}>', "",line)
            line = re.sub(r'[\n|\r|\t|]{1,}', " ",line)
            line = re.sub(r'[\s]{2,}', "",line)
            title = title + " " + line
            titleFound = False
        elif titleFound:
            print "TF",  line
            title += re.sub("\n", " ", line)
        
        if "<TEXT>" in line:
            print "TXT", line
            textFlag = True
        elif textFlag:
            print "TXTFT", line
            if "</TEXT>" in line:
                print "TXTC", line
                textFlag = False
            elif "." in line:
                line = line.split(".")
                print line 
                print "EOS"
                sentence+=line[0]
                sentences.append(sentence)
                sentence = line[1]
            else:
                print "SEN"
                sentence+=line
                
                
        
    #print len(sentences)
    # for each sentences strip and sanitize
    for ix in range (0, len(sentences)):
        sen = sentences[ix]
        #print sen
        sen = re.sub(r'[\n|\r|\t|]{1,}', " ",sen)
        sen = re.sub(r'[\s]{2,}', " ",sen)
        sen = sen.rsplit()
        sentences[ix] = sen

    return sentences,title

def readFT(data):
    titleFound = False
    textFlag = False
    kwFlg = False
    pFlag = False
    pFlagSen = False
    pFlagKW = False
    
    title = ""
    sentence = ""
    word = ""
    keywords = []
    sentences = []
    
    for line in data:
        if "<HEADLINE>" in line and not "</HEADLINE>" in line:
            #print "HL", line
            titleFound = True
            line = re.sub(r'<HEADLINE>', "",line)
            line = re.sub(r'[\n|\r|\t|]{1,}', " ",line)
            line = re.sub(r'[\s]{2,}', "",line)
            title = title + " " + line
        elif "<HEADLINE>" in line and "</HEADLINE>" in line:
            line = re.sub(r'<HEADLINE>', "",line)
            line = re.sub(r'</HEADLINE>', "",line)
            line = re.sub(r'[\n|\r|\t|]{1,}', " ",line)
            line = re.sub(r'[\s]{2,}', "",line)
            title = line
            titleFound = False
        elif "</HEADLINE>" in line:
            line = re.sub(r'</HEADLINE>', "",line)
            line = re.sub(r'[\n|\r|\t|]{1,}', " ",line)
            line = re.sub(r'[\s]{2,}', "",line)
            title = title + " " + line
            titleFound = False
        elif titleFound:
            print "TF",  line
            title += re.sub("\n", " ", line)
        
        if "<TEXT>" in line:
            textFlag = True
        elif textFlag:
            if "</TEXT>" in line:
                print "TXTC", line
                textFlag = False
            elif ".\n" in line:
                sentence+=line
                sentences.append(sentence)
                sentence = ""
            else:
                sentence+=line
                
                
        
    #print len(sentences)
    # for each sentences strip and sanitize
    for ix in range (0, len(sentences)):
        sen = sentences[ix]
        #print sen
        sen = re.sub(r'[\n|\r|\t|]{1,}', " ",sen)
        sen = re.sub(r'[\s]{2,}', "",sen)
        sen = sen.rsplit()
        sentences[ix] = sen

    return sentences,title
    
    
def readSJMN(data):
    
    titleFound = False
    textFlag = False
    kwFlg = False
    pFlag = False
    pFlagSen = False
    pFlagKW = False
    
    title = ""
    sentence = ""
    word = ""
    keywords = []
    sentences = []
    
    for line in data:
        if "<HEADLINE>" in line and not "</HEADLINE>" in line:
            #print "HL", line
            titleFound = True
            line = re.sub(r'<HEADLINE>', "",line)
            line = re.sub(r'[\n|\r|\t|]{1,}', " ",line)
            line = re.sub(r'[\s]{2,}', "",line)
            title += line
        elif "<HEADLINE>" in line and "</HEADLINE>" in line:
            line = re.sub(r'<HEADLINE>', "",line)
            line = re.sub(r'</HEADLINE>', "",line)
            line = re.sub(r'[\n|\r|\t|]{1,}', " ",line)
            line = re.sub(r'[\s]{2,}', "",line)
            title = line
            titleFound = False
        elif "</HEADLINE>" in line:
            line = re.sub(r'</HEADLINE>', "",line)
            line = re.sub(r'[\n|\r|\t|]{1,}', " ",line)
            line = re.sub(r'[\s]{2,}', "",line)
            title += line
            titleFound = False
        elif titleFound:
            print "TF",  line
            title += re.sub("\n", "", line)
            
        
        if "<TEXT>" in line:
            textFlag = True
            line = re.sub(r'<TEXT>', "",line)
            line = re.sub(r'[\n|\r|\t|]{1,}', " ",line)
            line = re.sub(r'[\s]{2,}', "",line)
            sentence += line
        elif "</TEXT>" in line:
            textFlag = False
            line = re.sub(r'</TEXT>', "",line)
            line = re.sub(r'[\n|\r|\t|]{1,}', " ",line)
            line = re.sub(r'[\s]{2,}', "",line)
            sentence += line
            sentences = sentence.split(";")
            print sentences
            sentence = ""
        elif textFlag:
            line = re.sub(r'[\n|\r|\t|]{1,}', " ",line)
            line = re.sub(r'[\s]{2,}', "",line)
            sentence+=line
            
    #print len(sentences)
    # for each sentences strip and sanitize
    for ix in range (0, len(sentences)):
        sen = sentences[ix]
        #print sen
        sen = re.sub(r'[\n|\r|\t|]{1,}', " ",sen)
        sen = re.sub(r'[\s]{2,}', "",sen)
        sen = sen.rsplit()
        sentences[ix] = sen

    return sentences,title
    
    
    
def readLA(data):
    
    titleFound = False
    textFlag = False
    kwFlg = False
    pFlag = False
    pFlagSen = False
    pFlagKW = False
    
    title = ""
    sentence = ""
    word = ""
    keywords = []
    sentences = []

    for line in data:
        if "<HEADLINE>" in line:
            #print "HL", line
            titleFound = True
        elif titleFound:
            if "<P>" in line:
                #print "TFP", line
                titleFound = False
                pFlag = True
        elif "</P>" in line:
            #print "PC", line
            pFlag = False
        elif "</HEADLINE>" in line:
            #print "HLC", line
            titleFound = False
        elif pFlag:
            #print "PF", line
            title += re.sub("\n", "", line)
        
        if "<TEXT>" in line:
            textFlag = True
        elif textFlag:
            if "<P>" in line:
                print "PF", line
                pFlagSen = True
            elif "</P>" in line:
                print "PC", line
                pFlagSen = False
                sentences.append(sentence)
                sentence = ""
            elif "</TEXT>" in line:
                print "TXTC", line
                textFlag = False
            elif pFlagSen:
                print "PFO", line
                sentence+=line
                
        if "<SUBJECT>" in line:
            print "KWF"
            kwFlg = True
        elif kwFlg:
            if "<P>" in line:
                pFlagKW = True
            elif "</P>" in line:
                pFlagKW = False
                keywords = word.split("; ")
                word = ""
            elif "</SUBJECT>" in line:
                kwFlg = False
            elif pFlagKW:
                line = re.sub(r'[\n|\r|\t|]{1,}', " ",line)
                line = re.sub(r'[\s]{2,}', "",line)
                word+=line
        
    #print len(sentences)
    # for each sentences strip and sanitize
    for ix in range (0, len(sentences)):
        sen = sentences[ix]
        #print sen
        sen = re.sub(r'[\n|\r|\t|]{1,}', " ",sen)
        sen = re.sub(r'[\s]{2,}', "",sen)
        sen = sen.rsplit()
        sentences[ix] = sen
    #print keywords
    return sentences,title,keywords
            

def readAP_WSJ(filename,data):
    #AP
    APHLTag = "HEAD"
    
    #WSJ
    WSJHLTag = "HL"
    
    index = 0 
    
    titleFound = False
    textFlag = False
    sentence = ""
    prevSen = ""
    sentences = []
    
    #AP type of file
    if "AP" in filename:
        tag = APHLTag
    elif "WSJ" in filename:
        tag = WSJHLTag
            
    for line in data:
        #print "( "+ line +" )"
        # Only the first <HEAD> tag represent the title
        if "<" + tag + ">" in line and "</" + tag + ">" in line and titleFound == False:
            line = re.sub("<" + tag + ">","", line)
            line = re.sub("</" + tag + ">","", line)
            line = re.sub("\n", "", line)
            title = line
            titleFound = True
        elif "<" + tag + ">" in line and titleFound == False:
            line = re.sub("<" + tag + ">","", line)
            line = re.sub("\n", " ", line)
            title = line
        elif "</" + tag + ">" in line and titleFound == False:
            line = re.sub("</" + tag + ">","", line)
            line = re.sub("\n", "", line)
            title+= line
            titleFound = True
        
        # Text processing
        if "<TEXT>" in line:
            line = re.sub("<TEXT>", "", line)
            line = re.sub("\n|\t", "", line)
            textFlag = True
            
        elif "</TEXT>" in line:
            #add the last line 
            sentences.append(sentence)
            line = re.sub("</TEXT>", "", line)
            line = re.sub("\n|\t|\r", "", line)
            textFlag = False

        elif textFlag == True:
            if line.startswith("   ") and prevSen != "":
                sentences.append(sentence)
                prevSen = sentence
                sentence = ""
            sentence += line
            prevSen = sentence
    #print len(sentences)
    # for each sentences strip and sanitize
    for ix in range (0, len(sentences)):
        sen = sentences[ix]
        sen = re.sub(r'[\n|\r|\t|]{1,}', " ",sen)
        sen = re.sub(r'[\s]{2,}', "",sen)
        sen = sen.rsplit()
        sentences[ix] = sen
    return sentences,title
#-------------------------------End of PARSING LOGIC ----------------------------------------



# Process Single Document (sentences)
# returns the title (string)
#         the sentences (list of list of words)
#         the number of sentences (int)
def singleDocRead(filename,file_data=None):
    
    sentences = []
    # open file
    #print filename
    #fh = open (filename, 'r')
        
    # read the file
    data = file_data
        
    if "AP" in filename or "WSJ" in filename:
        print "AP"
        sentences,title = readAP_WSJ(filename,data)
    elif "LA" in filename:
        print "LA"
        sentences,title,kws = readLA(data)
    elif "SJMN" in filename:
        print "SJMN"
        sentences,title = readSJMN(data)
    elif "FT" in filename:
        print "FT"
        sentences, title = readFT(data)
    elif "FBIS" in filename:
        print "FBIS"
        sentences, title = readFBIS(data)

    #print sentences[index]
    numberOfSen = len(sentences)
    #print numberOfSen

    print "The following document has been parsed: \n"
    print "Title: ", title
    print "Total number of sentences: ", numberOfSen
    print "DATA: ", file_data
    #close the file handler
    fh.close()
    
    return title,sentences,numberOfSen


# Sanitize: tokenize, and remove stopwords.
# returns: array of sentences (without stopwords)
#          array of arrays corresponding to sentences once tokenized
#          title (tokenized)
 
def sanitize(document, title):
    
    documentSentences = []
    sentence = ""
    
    token_title = []
    sSentence =[]
    token_sentenceDoc = []
    
    for token in nltk.word_tokenize(title):
        token_title.append(token)
    
    for sen in document:
        for token in sen:
            if "." not in token:
                sentence+= token
                sentence+= " "
            if len(token.split("."))<3 and "." in token:
                token = token.split(".")
                if sentence != "":
                    sentence += " "
                    sentence += token[0]
                    sentence += "."
                    documentSentences.append(sentence)
                    sentence = ""
                    sentence += token[1]
                    sentence += " "
                else:
                    sentence += " "
                    sentence += token[0]
                    sentence += ". "
                    sentence += token[1]
                    sentence += " "
            elif len(token.split("."))>2:
                token = token.split(".")
                newT = ""
                for i in range(0,len(token)):
                    if i<len(token)-1:
                        newT += token[i]
                        newT += "."
                    else:
                        newT += " "
                        newT += token[i]
                sentence += newT
        
        
    
    stre = ""
    for entry in documentSentences:
        stre+=entry
        stre+= " "
    
    # USE THE NLTK TOKENIZER (do not reinvent the wheel...)
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    tokee = tokenizer.tokenize(stre)
    
    stop = stopwords.words("english")
    
    for entry in tokee:
        for token in nltk.word_tokenize(entry):
            # remove stop words 
            if token not in stop:
                sSentence.append(token)        
        token_sentenceDoc.append(sSentence)
        sSentence = []
    
    return token_title, token_sentenceDoc, tokee



# ------------------------------- Start of STATS Functions -----------------------------------    
    
def termFrequency(term, senStats, flag):
    
    # This function takes in a term and a sentence and 
    # compute its frequency according to this formula:
    # tf(t,s) = freq(t,s)/MAXarg(freq(x,s))
    
    # The Flag indicates if it is the title, if so compute frequency
    # using this formula:
    # tf(t,s) = 0.5 + (0.5 * freq(t,s)/MAXarg(freq(x,s)))
    
    if flag:
        freqTS = 0.5 * float(senStats[term])

        # find the term that has the greatest frequency
        maxARG = float(max(senStats.iteritems(), key=operator.itemgetter(1))[1])
    
        tf = 0.5 + (freqTS/maxARG)
        #print "termFrequency( ", term, " ) = ",freqTS, " / ", maxARG, " = ", tf
    else:
        freqTS = float(senStats[term])

        # find the term that has the greatest frequency
        maxARG = float(max(senStats.iteritems(), key=operator.itemgetter(1))[1])
    
        tf = (freqTS/maxARG)
        #print "termFrequency( ", term, " ) = ",freqTS, " / ", maxARG, " = ", tf
    
    
    #print "termFrequency( ", term, " ) = ",freqTS, " / ", maxARG, " = ", tf
    return tf
    
def inverseSenFreq(term, NumberOfSentences, numOfSenContainingT):
    
    # This function computes the inverse sentence frequency
    # according to this formula:
    # isf(i) = log(Number of Sentences/ # of Sentences containing i)
    
    isf = math.log(float(NumberOfSentences) / float(numOfSenContainingT))
    
    #print "inverseSenFrequency ( ", term, " ) = ", NumberOfSentences, " / ", numOfSenContainingT, " = ", isf 
    
    return isf

def weightPerSen(sentence, senStats, textStats, numSen,flag):
    
    # This function returns a weight vector containing
    # each weight per term in a given sentence according
    # to the following formula:
    # weight(term, sentence) = termFrequency(term,sentence) * inverseSenFreq(term)
    
    # The Flag indicates if it is the title, if so compute weight
    # using this formula:
    # weight(term, sentence) = (0.5 + termFrequency(0.5 * term,sentence)) * inverseSenFreq(term)
    
    # weight[] = {weight(term#1,sentence), weight(term#2, sentence), ..., weight(term#len(sentence), sentence)}
    weight = []
    i = 0
    for term in sentence:
        #print term
        tf = termFrequency(term, senStats, flag)
        
        # default value for number of sentence containing the term is
        # 1 because if it is read there must be at least one sentence
        # containing the term.
        isf = inverseSenFreq(term, numSen, textStats.get(term,1))
        res = tf * isf
        #print "weight[", i , "] = ",tf, " * ", isf, " = ", res
        weight.append(res)
        i = i + 1
            
    return weight

# Compute cosine similarity between 2 vectors
# returns a float.    
def similarity (weightVec1, weightVec2):
    numerator = 0
    
    # compute the dot product of the two vectors.
    for x in range(max(len(weightVec1),len(weightVec2))):
        #print "[",x,"] = ",weightVec1[x] if len(weightVec1) > x else 0, " * " ,weightVec2[x] if len(weightVec2) > x else 0
        numerator+= (weightVec1[x] if len(weightVec1) > x else 0) * (weightVec2[x] if len(weightVec2) > x else 0)
        
    sum1 = sum([weightVec1[x]**2 for x in range(0,len(weightVec1))])
    sum2 = sum([weightVec2[x]**2 for x in range(0,len(weightVec2))])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    
    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator
    #print "Sim = ", numerator, " / ", denominator,  " = ", numerator*denominator
    
# ------------ End of STATS Functions -----------------


# Compute Document Statistics: 
# returns similarity_vector
#         weight_vector
def docStats (document, title):
    # Computes the statistics of the inputFile to do the edge
    # weighting. Also, various other NLP statistics.

    # Declarations
    wordStatsSen = dict()
    titleStatsSen = dict()
    collectedWSS = [dict() for x in range(len(document))]
    occurenceInCWSS = dict()
    weightVector = []
    similarityVector = []
    
    numberOfSen = len(document)
    
    sentenceNum = 0
    occPerSen = 0
    
    # count the occurences of the tokens inside the title
    # and include it into a dict: titleStatsSen
    for token in title:
        occured = titleStatsSen.get(token)
        if( occured == None ):
            titleStatsSen[token] = 1
        else:    
            titleStatsSen[token] = occured + 1
            

    # count the occurences of the tokens in a given sentence.
    # and include it into a dict: wordStatsSen
    # then collect all these stats in a dict (of dict [1 per sentence]): collectedWSS
    for sentence in document:
        for token in sentence:
            
            # occurences counted inside the sentence yet
            occurences = wordStatsSen.get(token)
            
            if( occurences == None ):
                wordStatsSen[token] = 1
            else:    
                wordStatsSen[token] = occurences + 1
        
        collectedWSS[sentenceNum] = wordStatsSen
        wordStatsSen = {}
        sentenceNum += 1
    
    # count the occurence of a term in the total text, by assinging +1 if it is present at least
    # once in the sentence
    # and include it into a dict: occurrenceInCWSS
    for senStats in collectedWSS:
        for token in senStats:
            # occurences counted in terms of token/sentence (if seen once already : do not increment)
            occPerSen = occurenceInCWSS.get(token)
            if ( occPerSen == None ):
                occurenceInCWSS[token]  = 1
            else:
                occurenceInCWSS[token] = occPerSen + 1
    
    
    # compute the weight vector for the title
    weightVector.append(weightPerSen(title, titleStatsSen, occurenceInCWSS, numberOfSen,True))
    
    # compute the weight vector for each sentence 
    for i in range (0, numberOfSen):
        weightVector.append(weightPerSen(document[i], collectedWSS[i], occurenceInCWSS, numberOfSen,False))
    
    
    
    senBSV = []
    
    # compute similarity for each sentence
    for i in range(0, numberOfSen):
        for x in range(i, numberOfSen):
            if(x > i):
                senBSV.append(similarity(weightVector[i],weightVector[x]))
        similarityVector.append(senBSV)
        senBSV = []
    
    return similarityVector, weightVector

    numerator = 0
    
    # compute the dot product of the two vectors.
    for x in range(max(len(weightVec1),len(weightVec2))):
        #print "[",x,"] = ",weightVec1[x] if len(weightVec1) > x else 0, " * " ,weightVec2[x] if len(weightVec2) > x else 0
        numerator+= (weightVec1[x] if len(weightVec1) > x else 0) * (weightVec2[x] if len(weightVec2) > x else 0)
        
    sum1 = sum([weightVec1[x]**2 for x in range(0,len(weightVec1))])
    sum2 = sum([weightVec2[x]**2 for x in range(0,len(weightVec2))])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    
    
    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator
    #print "Sim = ", numerator, " / ", denominator,  " = ", numerator*denominator
    
# ------------ End of STATS Functions -----------------

# ------------ Start of FITNESS Function Factors -----------------
def topicRelationFactor(summary, document, similarityVector, weightVector):
    
    
    
    # compute TR: the AVG of the similarities of the summary against the title
    indices = []
    for i in range(0,len(summary)):
        if (summary[i] == 1):
            indices.append(i)
    
    summarySize = len(indices)
    
            
    TR = float(sum([similarity(weightVector[i], weightVector[0]) for i in indices]))/float(summarySize)
    
    # compute TRF:
    
    # to find max simply AVG the top (S = summary length) similarities of all
    # the sentences with the topic.
  
    simListTopic = []
    topList = []

    for i in range(0,len(document)-1):
        simListTopic.append(similarityVector[i][0])
        
    simListTopic.sort(reverse= True)
    
    topList = simListTopic [:summarySize]
    
    avg = float(sum(topList))/float(summarySize)
    
    TRF = TR / avg
    
    return TRF

def cohesionFactor(summary, similarityVector):
    # We need to compute a similarity matrix (containing the similarity b/w every pair of sentences)
    # in this case just access the 2D similarityVector...
    
    # C = SUM(weights of all edges in the summary)/ Ns
    
    # where: Ns = ((S = size of the summary) * S-1) / 2
    
    indices = []
    for i in range(0,len(summary)):
        if (summary[i] == 1):
            indices.append(i)
    
    summarySize = len(indices)
    
    
    Ns =  (summarySize * (summarySize-1))/2
    
    total = 0
    for i in indices:
        for x in indices:
            if (x>i):
                total += similarityVector[i][x-i-1]
    
    C = float(total) / float(Ns)
    currentMax=0
    # find the max val in the sV
    for i in similarityVector:
        for x in i:
            if (x > currentMax):
                currentMax = x
    
    M = currentMax            
    
    # now compute the actual CF
    CF = math.log(C*9+1)/math.log(M*9+1)
    
    return CF

def rfComputeMaxVal(summaryLength, numberOfSen, similarityVector):
    
    m = numberOfSen-1
    n = summaryLength
    maxVal = 0
    
    tempI = 0
    tempK = 0
    mVI = 0
    mVK = 0
    mVJ = 0
    
    A = [[0 for _ in xrange(n)] for __ in xrange(m)]
    B = [[0 for _ in xrange(n)] for __ in xrange(m)]
    
    for j in range(1,n):
        for i in range(0,m):

                # check wether using the previous number sentences + the similarity of the current
                # similaritVector[k][i]  = sim(sentenceK, sentenceI)
                
                # if length is j and # of sentence i = A[i][j]
                # if using ith sentence on a path of length j --> A[i][j] is smaller than: (using any other of the sen# up to I on a path of smaller length) + (that sim(sen#,senI))
                # using the kth sentence on a path of length j-1 --> A[k][j-1] (plus) the sim(senK, senI)
                # then: (take the value of the ith sentence, of the previous length) and add (sim(senK, senI))) [include sentence I]
                # A[i][j] = A[i][j-1] + sim(senK, senI) : using the ith sentence on a path of lenght j-1 + sim(senK, senI)
            #print i, j
            
            #print similarityVector[8][3]
            for k in range (0, i+1):
                #print i, k, j
                #print "Normalized indices: ", k
                #print "Comparison = ", A[i][j], " < ", A[k][j-1], " + " , similarityVector[k][i-k-1], " = ", (A[k][j-1] + similarityVector[k][i-k-1])
                if(A[i][j] < (A[k][j-1] + similarityVector[k][i-k-1])) & (i>=j):
                    #print "Comparison = True"
                    #print "(A[",i,"][",j,"] < (A[",k,"][",j-1,"] + similarityVector[",k,"][",i-k-1,"])"
                    #print "-----------------------------------------"
                    #print i,k,j,A[i]
                    #print "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv"
                    A[i][j] = A[k][j-1] + similarityVector[k][i-k-1]
                    #B[i][j] = k,i
                    #print i,k,j,A[i]
                    #print "-----------------------------------------"
                #else:
                    #print "unused: i = ", i," k = ", k, " j = ", j
                if(maxVal < A[i][j]):
                    #print maxVal, " < ", A[i][j]
                    maxVal = A[i][j]
                    #print k, i, j
                    mVI = i
                    mVJ = j 
                    mVK = k
                            
    #print "Maximum Weight = ", maxVal, " A[",mVI,"][",mVJ,"] = ", A[mVI][mVJ]
    
    #maxVal=0
    #for x in range(0,687):
    #    if maxVal < A[x][49] :
    #        maxVal = A[x][49]
    #        mVI = x
    #        mVJ = 49
    #    print x, 49     

    #print "Maximum Weight = ", maxVal, " A[",mVI,"][",mVJ,"] = ", A[mVI][mVJ]
    #print "at length: ", n, " sen" ,mVK,mVI, "was added"
        
    # to find path walk back the matrix A
    # last added edge is : mVK,mVI 
    # path doesnt work for some unknown reason, but works in normalized version (see longestPath_norm.py)
    #path =[]
    #path.append(("sim",mVK,mVI))
    #print "at length: ", n-1, " sen" ,mVK,mVI, "was added"
    #for j in range(2,n): 
    #    for k in range (0, mVI+1):
    #        if (A[mVK][mVJ-1] == A[k][mVJ-2] + similarityVector[k][mVK-k-1]):
    #            mVI=mVK
    #            mVK=k
    #            mVJ=mVJ-1
    #            break
    #    path.append(("sim",mVK,mVI))
    #    print "at length: ", n-j, " sen" ,mVK,mVI, "was added"
    #print path
    
    return maxVal
    
def readabilityFactor(summary, document, similarityVector, maxValRF):
    

    # now compute actual Readability Factor
    R = 0
    indices = []
    for i in range(0,len(summary)):
        if (summary[i] == 1):
            indices.append(i)
    
    #print indices
    for i in range(0,len(indices)-1):
        sen1 = indices[i]
        sen2 = indices[i+1]
        #print sen1, sen2, len(similarityVector[sen1]), sen2-sen1-1
        R = R + similarityVector[sen1][sen2-sen1-1]
        #print sen1, sen2
                #print "R = ", R, " + ", "sV[",summary[i],"][",(summary[x]-summary[i]-1),"] = ", similarityVector[summary[i]][summary[i+1]-summary[i]-1]  
        
    
    ReadabilityFactor = R / maxValRF
    #print "R = ", R, " / maxVal = ", maxValRF
    #print "RF = ", ReadabilityFactor
    return ReadabilityFactor

def fitnessFunction(trfMul, cfMul, rfMul,summary, document, similarityVector, weightVector,maxVRF):
    
    RF = readabilityFactor(summary, document, similarityVector, maxVRF)
    TRF = topicRelationFactor(summary, document, similarityVector, weightVector)
    CF = cohesionFactor(summary, similarityVector)
    
    #print "RF: ", RF, " TRF: ", TRF, " CF : ", CF
    #print (trfMul*TRF)+(cfMul*CF)+(rfMul*RF) , " / ", trfMul+cfMul+rfMul
    result = float((trfMul*TRF)+(cfMul*CF)+(rfMul*RF))/ float(trfMul+cfMul+rfMul)
    
    return result

# ------------ End of FITNESS Function Factors -----------------

 # ------------ Start of Genetic Algorithm ----------------------
def generateChromosome (length, boundary):
    # Simple function to generate a random chromosome
    # Boundary represent the high boundary for possible values
    # Length is the lenght of the chromosome
    # 
    # Each succeding gene HAS to be a value GREATER than the previous
    # gene, due to the nature of the work (path in a DAG).
    #
    # Chromosome ex: (length = 10, boundary = 505)
    #
    # ([1][32][45][67][92][103][104][293][493][504])
    chromosome = np.array([0] * (boundary-length) + [1] * (length))
    np.random.shuffle(chromosome)
    #print "Chromosome: ",chromosome
    
    return chromosome  

def centerOfMass(population, degOfDeviation):
    # This function is used to determine if the initial population is biased towards a
    # certain area of the search space, either on a gene level or a chromosomchromosomee level.
    # in this case population is a list of vectors (each representing an individual in the population)
    #print population
    # compute the x coordinate according to 1's
    total = 0
    count = 0
    
    for j in range(0, len(population)):      
        for i in range(0,len(population[0])):
            if(population[j][i] == 1):
                count = count + i+1
                total = total + 1
                
    x1 = float(count)/float(total)
    
    # compute the y coordinate according to 1's
    total = 0
    count = 0
    for j in range(0, len(population[0])):
        for i in range(0,len(population)):
            if(population[i][j] == 1):
                count = count + i+1
                total = total + 1
                
    y1 = float(count)/float(total)
    
    # compute the x coordinate according to 0's
    total = 0
    count = 0
    for j in range(0, len(population)):
        for i in range(0,len(population[0])):
            if(population[j][i] == 0):      
                count = count + i+1
                total = total + 1
                
    x0 = float(count)/float(total)
    
    # compute the y coordinate according to 0's
    total = 0
    count = 0
    for j in range(0, len(population[0])):
        for i in range(0,len(population)):
            if(population[i][j] == 1):
                count = count + i+1
                total = total + 1
                
    y0 = float(count)/float(total)

    #print "x0 = ",x0, " y0 = ",y0
    #print "x1 = ",x1, " y1 = ",y1
    
    # Center of mass should tend to:
    
    boolX0 = float(len(population)-degOfDeviation)/float(1.05) <= x0 <= float(len(population)+degOfDeviation)/float(1.05)
    boolY0 = float(len(population)-degOfDeviation)/float(1.05) <= y0 <= float(len(population)+degOfDeviation)/float(1.05)
    boolX1 = float(len(population)-degOfDeviation)/float(1.05) <= x1 <= float(len(population)+degOfDeviation)/float(1.05)
    boolY1 = float(len(population)-degOfDeviation)/float(1.05) <= y1 <= float(len(population)+degOfDeviation)/float(1.05)
    
    #print "According to 0s : ",(bool(boolX0) == bool(boolY0))
    #print "According to 1s : ",(bool(boolX1) == bool(boolY1))
    
    # XOR the two components
    #print (bool(boolX0) == bool(boolX1))

    return (bool(boolX0) == bool(boolX1))

def createPopulation (popSize, geneBoundary, document):
    # flag to verify proper diversity
    isPopBiased = False
    #print "GB --> ",geneBoundary
    while isPopBiased != True:
        population  = []
        for i in range (0, popSize):
            population.append(generateChromosome(geneBoundary, len(document)))
    
        #print population
        #isPopBiased = centerOfMass(population, 1.005)
        isPopBiased = True
    return population

def evaluatePopulation(population, FFCoefficients, document,similarityVector, weightVector, maxVRF):
    results = []
    maxFF = 0
    sumID = 0
    
    #print "Pop LEN: ",len(population)

    for i in range(0,len(population)):
        results.append((fitnessFunction(FFCoefficients[0],FFCoefficients[1],FFCoefficients[2],population[i], document, similarityVector,weightVector,maxVRF), i))
        if maxFF < results[0]:
            maxFF = results[0]
            sumID = i
    #print len(results)
    return results, sumID, maxFF
    
def hamming_distance(s1, s2):
    "Return the Hamming distance between equal-length sequences."
    if len(s1) != len(s2):
        raise ValueError("Undefined for sequences of unequal length")
    return float(sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2)))/float(len(s1))
    
def naturalSelection(population, results):
    # assuming that the half of the population is selected
    # sort array of results

    
    results.sort(key=operator.itemgetter(0), reverse=True)
    resSUM =0.0 
    numRES = 0
    
    for res in results:
        resSUM = resSUM + res[0]
        numRES = numRES + 1
    
    # compute the probability of a chromosome to survive to the next generation
    probVector = []
    
    for res in results:
        probVector.append(float(res[0])/float(resSUM))
            
    # use the Cumulative Distributed Probability
    cdf = [probVector[0]]
    for i in xrange(1, len(probVector)):
        cdf.append(cdf[-1] + probVector[i])
    
    indices = []
    #select half the population
    for i in range(0,(len(population)/2)):
        indices.append(results[i][1])
    
    newPopulation = []
    
    #elitism = 10
  
    for i in range(0,10):
        newPopulation.append(population[indices[i]])
        #discard the second half
    for i in range(0,len(indices)-10):
        random_ind = bisect(cdf,random.random())
        newPopulation.append(population[random_ind])
            
    #print "NEWPOP: ",len(newPopulation)
    return newPopulation

def crossover(chromosome1, chromosome2, numOfRegions, noc):
    # split the chromosomes in n sub-regions and pick randomly a region to crossover
    regionLength = len(chromosome1)/numOfRegions
    crossoverRegion = random.randrange(0,numOfRegions)
    startOfCOR = crossoverRegion * regionLength
    endOfCOR = startOfCOR + regionLength 
    
    chromo1COR = copy.copy(chromosome1[startOfCOR:endOfCOR])
    chromo2COR = copy.copy(chromosome2[startOfCOR:endOfCOR])
    
    # verify that the number of 1's is consistent with our length
    countC1 = 0
    for gene in chromo1COR:
        if (gene == 1):
            countC1 = countC1 + 1
            
    countC2 = 0
    for gene in chromo2COR:
        if (gene == 1):
            countC2 = countC2 + 1
    
    #started with lenC1 genes now has lenC2 genes
    child1Delta = countC1 - countC2
    child2Delta = countC2 - countC1
    
    childCOR1 = list(chromo2COR)
    childCOR2 = list(chromo1COR)
    
    while child1Delta != 0: 
        #it means that we need to adjust the count of genes to respect the limit
        if child1Delta < 0:
            #it means that we need to remove exactly child1Delta genes to restore equilibrium
            for x in range(0,regionLength):
                if(chromo1COR[x] == 0 and childCOR1[x] == 1):
                    childCOR1[x] = 0
                    child1Delta = child1Delta + 1
                    break
            
        elif child1Delta > 0:
            #it means that we need to add exactly child1Delta genes to restore equilibrium
            for x in range(0,regionLength):
                if(chromo1COR[x] == 1 and childCOR1[x] == 0):
                    childCOR1[x] = 1
                    child1Delta = child1Delta - 1
                    break

    while child2Delta != 0: 
        #it means that we need to adjust the count of genes to respect the limit
        if child2Delta < 0:
            #it means that we need to remove exactly child1Delta genes to restore equilibrium
            for x in range(0,regionLength):
                if(chromo2COR[x] == 0 and childCOR2[x] == 1):
                    childCOR2[x] = 0
                    child2Delta = child2Delta + 1
                    break
            
        elif child2Delta > 0:
            #it means that we need to add exactly child1Delta genes to restore equilibrium
            for x in range(0,regionLength):
                if(chromo2COR[x] == 1 and childCOR2[x] == 0):
                    childCOR2[x] = 1
                    child2Delta = child2Delta - 1
                    break
    
    child1 = list(chromosome2)
    child1[startOfCOR:endOfCOR] = list(childCOR2)
    
    child2 = list(chromosome1)
    child2[startOfCOR:endOfCOR] = list(childCOR1)
    
    # verify that the number of 1's is consistent with our length
    countChr1 = 0
    for gene in child1:
        if (gene == 1):
            countChr1 = countChr1 + 1
            
    countChr2 = 0
    for gene in child2:
        if (gene == 1):
            countChr2 = countChr2 + 1
            
    # verify that the number of 1's is consistent with our length
    count1 = 0
    for gene in chromosome1:
        if (gene == 1):
            count1 = count1 + 1
            
    count2 = 0
    for gene in chromosome2:
        if (gene == 1):
            count2 = count2 + 1  
            
    return child1, child2
    
def mutation(chromosome):
    # select a random 1 and swap it with one of its neighbor...
    mutationDone = False
    
    while mutationDone != True:
        
        index = random.randrange(0, len(chromosome)-1)
        if chromosome[index] == 1:
            if index>0:
                if chromosome[index-1]== 0:
                    chromosome[index]=0
                    chromosome[index-1]=1
                    mutationDone = True
                elif chromosome[index+1] == 0:
                    chromosome[index] = 0
                    chromosome[index+1] = 1
                    mutationDone = True
    return chromosome
            
    
def geneticAlgorithm(popSize, geneBoundary, FFCoefficients, sentences, similarityVector, weightVector):
    numberOfSen = len(sentences)
    isPopBiased = False

    maxFFCount = 0
    lastMFF = 0
    # create initial population
    print "Doc length: ",len(sentences)
    #print sentences
    population = createPopulation(popSize, geneBoundary, sentences)
    for x in range (0,15):
        
        nextGen = []
        nextGenChilds = []
        
    
        maxValRF = rfComputeMaxVal(len(population[x]), len(sentences), similarityVector)
        # evaluate initial population
        #print population
        popEval,sumID, maxFF = evaluatePopulation(population, FFCoefficients, sentences, similarityVector, weightVector, maxValRF)
        
        # select the offspring that makes it to the next generation
        nextGen = naturalSelection(population, popEval)

        for i in range (0, (len(nextGen)/2)):
            
            child1, child2 = crossover(nextGen[i],nextGen[i+1],10,3)            
            #print "---------------------------------------------------------------------------------------------"
            #print "P1FF = ", parent1FF, " P2FF = ", parent2FF, " child1FF = ", child1FF, " child2FF = ", child2FF
            #time.sleep(1)

            child1 = mutation(child1)
            child2 = mutation(child2)

            

            #child1FF = fitnessFunction(FFCoefficients[0],FFCoefficients[1],FFCoefficients[2],child1)
            #child2FF =fitnessFunction(FFCoefficients[0],FFCoefficients[1],FFCoefficients[2],child2)
            
            #print "P1FF = ", parent1FF, " P2FF = ", parent2FF, " child1FF = ", child1FF, " child2FF = ", child2FF
            #print "---------------------------------------------------------------------------------------------"

            #time.sleep(1)
            nextGenChilds.append(child1)
            nextGenChilds.append(child2)
            
        print "Generation: ", x
        print "MAX FF for this Pop.: ", maxFF
          
        nextGen = nextGen + nextGenChilds
        
        if x != 0:
            population = []
        #print len(population)    
        population = nextGen
        
        #print len(population)
    
    #print summary
    
    indices = []
    summary = population[sumID]
    for i in range(0,len(summary)):
        if (summary[i] == 1):
            indices.append(i)
    
    #for x in indices:
        #print sentences[x]
    
    return indices
    
# ------------ End of Genetic Algorithm ------------------------

