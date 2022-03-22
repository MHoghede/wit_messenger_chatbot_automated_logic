#!/usr/bin/env python
# coding:utf-8
from __future__ import print_function
from __future__ import unicode_literals
import os, sys
import json
import csv                             

path_to_json = 'wit_ai_chatbot_unzipped_dirs'

def first_entity_resolved_value(entities, entity):
    # if entity in entities:
    Q=len(entities)
    for q in range(Q):
        if entities[q]['entity'] == entity:
            return True
    return False

def binaryToEntities(binary,all_entities):
    binary1 = binary
    acc_value,i, n = 0, 0, 0
    selected_entities=[]
    while(binary != 0):
        acc_value = binary % 0b10
        if(acc_value):
            selected_entities.append(all_entities[i])
        binary = binary//0b10
        i += 1
    return selected_entities
                       

my_successfull_return_status=False

if os.path.exists('wit_ai_chatbot_db.old.csv'):
  os.remove('wit_ai_chatbot_db.old.csv')
  
if os.path.exists('wit_ai_chatbot_db.csv'):
    os.replace('wit_ai_chatbot_db.csv','wit_ai_chatbot_db.old.csv')

with open('wit_ai_chatbot_db.csv','w', encoding='UTF8') as my_chatbot_db_file:
    writer = csv.writer(my_chatbot_db_file)
    max_number_of_entities=5
    header = ['intent', '#entities', 'entity 0','entity 1','entity 2','entity 3','entity 4', 'utterance','answer']
    # write the header
    writer.writerow(header)

    for file_name in [file for file in os.listdir(path_to_json+'/intents/') if file.endswith('.json')]:
        with open(path_to_json+'/intents/'+file_name,"r") as my_intent_file:

            my_intents_data = json.load(my_intent_file)
            my_intent=my_intents_data['name']
            my_entities=my_intents_data['entities']

            N = len(my_entities)
            if N > max_number_of_entities:
                my_successfull_return_status=False
                break

            all_entities=[]
            for j in range(N):
                all_entities.append(str(my_entities[j]))
            N_hot = pow(2, N)
                      
            for l_hot in reversed(range(N_hot)):
                if l_hot==0:
                    continue
                
                selected_entities=binaryToEntities(l_hot,all_entities)
                number_of_selected_entities=len(selected_entities)

                if number_of_selected_entities:
                    with open(path_to_json+'/utterances/'+'utterances-1.json',"r") as my_utterances_file:                    
                        my_utterances_data = json.load(my_utterances_file)
                        my_utterances=my_utterances_data['utterances']
                        M=len(my_utterances)


                        
                        for m in range(M):
                            if my_utterances[m]['intent'] == my_intent:
                                #Make list of entities for utterance
                                entities_for_utterance=my_utterances[m]['entities']
                          
                                selected_entities_found=True
                                
                                for entity_index in range(number_of_selected_entities):
                                    if not first_entity_resolved_value(entities_for_utterance,selected_entities[entity_index]):
                                        selected_entities_found=False
                                    
                                if selected_entities_found:
                                    my_successfull_return_status=True
                                    my_answer="***To be filled in by you***"
                                    data=[]                                    
                                    data.append(my_intent)                                    
                                    data.append(str(number_of_selected_entities))

                                    z=0
                                    while z < number_of_selected_entities:
                                        data.append(selected_entities[z])
                                        z+=1
                                        
                                    while z < max_number_of_entities:
                                        data.append('')
                                        z+=1
                                        
                                    data.append(str(my_utterances[m]['text']))                                                                        
                                    data.append(my_answer)                                                                                                            

                                    # write the data
                                    writer.writerow(data)

if my_successfull_return_status:
    sys.exit("Successfully created new valid wit_ai_chatbot_db.csv")
else:
    if os.path.exists('wit_ai_chatbot_db.csv'):
        os.remove('wit_ai_chatbot_db.csv')
    sys.exit("Error: Unsuccesful conversion to a new wit_ai_chatbot_db.csv")
    
