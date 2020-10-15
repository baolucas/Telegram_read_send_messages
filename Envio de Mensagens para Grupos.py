# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 19:59:42 2020

@author: lucas.gloria
"""


import configparser
#import json
import asyncio
#import time
from telethon.tl import types
import csv
import os

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import PeerUser, PeerChat, PeerChannel

from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import (
PeerChannel
)

from telethon.tl.types import InputMediaPoll, Poll, PollAnswer
from telethon.tl.patched import MessageService
from datetime import datetime

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

# Remember to use your own values from my.telegram.org!
api_id = api_id
api_hash = api_hash
client = TelegramClient(username, api_id, api_hash)


arquivo_csv_editados = "dict_msgs_editadas.csv"
arquivo_csv_destino = "bd_csv_msgs_destino.csv"

def msg_editada(arquivo,id_msg,horario):
    
    aux = 'editada'
    file_exists = os.path.isfile(arquivo)
    horario = datetime.strptime(horario, '%Y-%m-%d %H:%M:%S')
    
    if file_exists:
        with open(arquivo, mode='r') as infile:
            reader = csv.reader(infile)
            mydict = {rows[0]:rows[1] for rows in reader}
            
        
        if str(id_msg) in mydict.keys(): #verifica se a chave está no dict criado dos editados
            
            date_time_obj = datetime.strptime(mydict[str(id_msg)], '%Y-%m-%d %H:%M:%S')
            #print('horario',type(horario))
            #print('date_time_obj',type(date_time_obj))
            if horario > date_time_obj:
                #print(arquivo,id_msg,horario,date_time_obj)
                aux = 'editar'
        else:
            aux = 'editar'
    else:
        aux = 'editar'
            
    return aux

async def main():

 
        # You can print all the dialogs/conversations that you are part of:
        async for dialog in client.iter_dialogs(limit=20):
            print(dialog.name, 'has ID', dialog.id )
           # print(dialog)
		
        user_input_channel = input("Digite o ID do canal que sera coletado as mensagens:")  #1479578130  Chefe lives
        #user_input_channel = '1479578130' #opateste  #1479578130 Chefe lives

		
        if user_input_channel.isdigit():
            
            entity = PeerChannel(int(user_input_channel))
        else:
            
            entity = user_input_channel
            
       # my_channel = client.get_entity(entity)
        async for message in client.iter_messages(entity,limit= 1):
                print('Ultimo ID enviado desse canal: ', message.id)
                last_id_enviado = message.id
        
        #CANAIS / GRUPOS QUE RECEBERÃO AS MSGSS

        canal_destino = await client.get_entity(1489367949) #tips_iguin - Grupo que receberá as mensagens
        
        #id_minimo = input("Digite o id minimo para encaminhar as msg:")
        last_id = int(last_id_enviado) -1
        
        max_temp = 0
        dict_msg_destino = {}
        dict_msg_destino_temp = {}
        
        while True:
            
            
            ######################################################################################################################################################
            ######################################################################################################################################################
            ######################################################### PERCORRE AS MENSAGENS EDITADAS #############################################################
            ######################################################################################################################################################
            ######################################################################################################################################################
            
            lista_envio = []
            msgs_editadas = []
            async for message in client.iter_messages(entity,limit = 20):
                
                if message.edit_date is not None:
                    
                    #arquivo_csv = "dict_chefe_editadas.csv"
                   # print(message.edit_date)
                    #print(message.edit_date.strftime('%Y-%m-%d %H:%M:%S'))
                    editar = msg_editada(arquivo_csv_editados,message.id, message.edit_date.strftime('%Y-%m-%d %H:%M:%S')) #verifica se essa edição ja foi alterada no destino
                    
                    if editar == 'editar':
                        
                        with open(arquivo_csv_destino, mode='r') as infile:
                            reader = csv.reader(infile)
                            mydict = {rows[0]:rows[1] for rows in reader}
                            

                        if str(message.id) in mydict.keys(): #verifica se a chave está no dict criado do csv
                            id_reply_aux = mydict[str(message.id)]
                            id_reply = id_reply_aux.strip()

                            
                            try:
                                await client.edit_message(canal_destino,int(id_reply),str(message.text))
                            except Exception:
                                pass
                            
                            
                            file_exists = os.path.isfile(arquivo_csv_editados)
                            
                            try:
                                with open(arquivo_csv_editados, "a") as csvfile:
                                    headers = ['de', 'hora']
                                    writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)
                                    if not file_exists:
                                        writer.writeheader()  # file doesn't exist yet, write a header
                                    
                                    writer.writerow({'de': message.id, 'hora': message.edit_date.strftime('%Y-%m-%d %H:%M:%S')})
                                        
                                    #dict_sky_destino_temp = {}
                                    
                            except IOError:
                                print("I/O error")
                                
                        
                    msgs_editadas.insert(0,message)
                    
                if message.id > last_id:
                    if message.id > max_temp:
                        #print(message)
                        max_temp = message.id
                        

                    #print(message)
                    if not isinstance(message, MessageService): #Excluo as MessageServices como mudança de titulo, Pin e etc
                        lista_envio.insert(0,message)  
            ######################################################################################################################################################
            ######################################################################################################################################################
            ######################################################### FINALIZA AS MENSAGENS EDITADAS #############################################################
            ######################################################################################################################################################
            
            ######################################################################################################################################################
           
            ######################################################################################################################################################
            ######################################################### INICIALIZA AS NOVAS MENSAGENS  #############################################################
            ######################################################################################################################################################
            ######################################################################################################################################################
                   
                    
            if len(dict_msg_destino_temp) > 0:
                                
                file_exists = os.path.isfile(arquivo_csv_destino)
                
                try:
                    with open(arquivo_csv_destino, "a") as csvfile:
                        headers = ['de', 'para']
                        writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)
                        if not file_exists:
                            writer.writeheader()  # file doesn't exist yet, write a header
                        for k,v in dict_msg_destino_temp.items():
                            writer.writerow({'de': k, 'para': v})
                    dict_msg_destino_temp = {}
                    
                except IOError:
                    print("I/O error")
                 
            if len(lista_envio) > 0:
                #await client.forward_messages(testesmsg,lista_envio,entity)
                for i in range(len(lista_envio)):
                    id_nova_mensagem = lista_envio[i].id
                    
                    if not isinstance( lista_envio[i].media, types.MessageMediaPoll):
                                                                        
                        if lista_envio[i].is_reply:
                            #print(lista_envio[i])
                            id_reply = 0
                            
                            #print(lista_envio[i].reply_to_msg_id)
                            
                            if lista_envio[i].reply_to_msg_id in dict_msg_destino.keys(): #verifica se está no dicionário em execução
                                id_reply = dict_msg_destino[lista_envio[i].reply_to_msg_id]
                                #print('ta no dict')
                            else:
                                
                                with open(arquivo_csv_destino, mode='r') as infile: #se n tiver no dict , verifica no csv ( bd )
                                    #print('abri csv')
                                    reader = csv.reader(infile)
                                    mydict = {rows[0]:rows[1] for rows in reader}
                                    
                                    #print(mydict)
                                    #print(mydict.keys())
                                        
                                #print(lista_envio[i].reply_to_msg_id, type(lista_envio[i].reply_to_msg_id))
                                if str(lista_envio[i].reply_to_msg_id) in mydict.keys(): #verifica se a chave está no dict criado do csv
                                    id_reply_aux = mydict[str(lista_envio[i].reply_to_msg_id)]
                                    id_reply = id_reply_aux.strip()
                                    print('id reply: ',id_reply)
                            
                            if id_reply != 0 : #se n tiver encontrado chave, envia apenas a msg sem responder alguma outra
                                await client.send_message(canal_destino,lista_envio[i],reply_to = int(id_reply) )
                            else:
                                await client.send_message(canal_destino,lista_envio[i])
                            
                            async for message in client.iter_messages(canal_destino, limit =1):
                                id_enviado_destino = message.id
                            
                            #print('id_enviado_destino: ',id_enviado_destino)
                            #print('id enviado: ',id_nova_mensagem)
                            dict_msg_destino[id_nova_mensagem] = id_enviado_destino
                            dict_msg_destino_temp[id_nova_mensagem] = id_enviado_destino
                            #print('id enviado na origem: ',id_nova_mensagem)
                        else:

                            await client.send_message(canal_destino,lista_envio[i])
                            
                            async for message in client.iter_messages(canal_destino, limit =1):
                                id_enviado_destino = message.id

                            dict_msg_destino[id_nova_mensagem] = id_enviado_destino
                            dict_msg_destino_temp[id_nova_mensagem] = id_enviado_destino
                            #print('id enviado na origem: ',id_nova_mensagem)
                            #print('id enviado: ',id_nova_mensagem)
                            #print('id_enviado_destino: ',id_enviado_destino)
                            
                    else: 
                        await client.send_message(canal_destino,file=InputMediaPoll(
                            poll=Poll(
                                id = lista_envio[i].media.poll.id,
                                question= lista_envio[i].media.poll.question,
                                answers= lista_envio[i].media.poll.answers
                            )
                        ))
                            
                        async for message in client.iter_messages(canal_destino, limit =1):
                                id_enviado_destino = message.id
                                
                        dict_msg_destino[id_nova_mensagem] = id_enviado_destino
                        dict_msg_destino_temp[id_nova_mensagem] = id_enviado_destino
                        #print('id enviado na origem: ',id_nova_mensagem)
                  #  await client.send_message(opateste,lista_envio[i])

            await asyncio.sleep(2)
            if max_temp != 0:
                last_id = max_temp

 
with client:
    client.loop.run_until_complete(main())