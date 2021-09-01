#-*- coding: utf-8 -*-
import dpkt
import pcap
import time
import math
import os
import binascii
import re
import requests
import base64
import socket
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256


tag_begining = ["<party-chatrecruit", "<link id='item-name:" , "<link id='damage-meter:", "<guild-member", "<atl", "<link id='achievement:"]
tag_replace = ["", "「無法辯識的物品ID」", "「戰鬥記錄」", "", "", "「無法辯識的成就ID」"]
dungeonID = ["SeaCave", "SuJangKo", "GwiMyeonGeukDan", "DistrotedCastle"]
dungeonNameCHT = ["回聲水中洞", "南天藏寶庫", "鬼面劇團", "扭曲的天舞宮"]
tag_ending = "'/>"
dungeonTag = "<link id='dungeon:Dungeon_"
linkTag = ["<link id='arena-dungeonInvite:", ".0'/>"]
lenOfDungeonTag = len(dungeonTag)
sniff_IP = ["192.168.225.131", "192.168.225.133"]
with open('connection-private.pem', 'r') as f:
    key = f.read()
rsakey = RSA.importKey(key)

def pushdata(playerName, speakingContent, ip_dst):
    #RSA signature
    signer = Signature_pkcs1_v1_5.new(rsakey)
    digest = SHA256.new()
    digest.update(playerName + speakingContent)
    sign = signer.sign(digest)  
    
    #url = "http://104.199.232.117/pushdataWRYYYYYYYYYYYYYYY?msg=" + base64.b32encode(speakingContent) + "&player=" + base64.b32encode(playerName) + "&sign=" + base64.b32encode(sign)
    url = "http://104.199.232.117/pushdataWRYYYYYYYYYYYYYYY"
    #test_url = "http://127.0.0.1/pushdataWRYYYYYYYYYYYYYYY"
    post_data = {
        "msg" : base64.b32encode(speakingContent),
        "player" : base64.b32encode(playerName),
        "src" : account_index.index(ip_dst),
        "sign" : base64.b32encode(sign)
    }
    print(playerName + " : " + speakingContent)

    try:
        #r = s.get(url, timeout=5)
        r = s.post(url, data=post_data, timeout=5)
        #r = s.post(test_url, data=post_data, timeout=5)
    except requests.exceptions.ConnectionError:
        print("Connection Error")
    return 0

def tag_filter(speakingContent):
    for i in range(len(tag_begining)):
        tagBeginPos = speakingContent.find(tag_begining[i])
        while tagBeginPos >= 0:
            tagContent = speakingContent[tagBeginPos:]
            tagEndPos = tagContent.find(tag_ending)
            tagContent = tagContent[:tagEndPos+3]
            print(tagContent)
            speakingContent = speakingContent.replace(tagContent, tag_replace[i])
            tagBeginPos = speakingContent.find(tag_begining[i])

    dungeonTagBeginPos = speakingContent.find(dungeonTag)
    while dungeonTagBeginPos >= 0:
        print("found dungeon tag")
        dungeonTagString = speakingContent[dungeonTagBeginPos:]
        dungeonTagEndPos = dungeonTagString.find(tag_ending)
        dungeonString = dungeonTagString[lenOfDungeonTag : dungeonTagEndPos]
        dungeonTagString = dungeonTagString[:dungeonTagEndPos+3]
        print("dungeonString:  " + dungeonString)
        if dungeonString in dungeonID:
            dungeonString = dungeonNameCHT[dungeonID.index(dungeonString)]
        else:
            dungeonString = "「無法辯識的副本ID：" + dungeonString + "」"
        speakingContent = speakingContent.replace(dungeonTagString, dungeonString)
        dungeonTagBeginPos = speakingContent.find(dungeonTag)

    linkTagBeginPos = speakingContent.find(linkTag[0])
    while linkTagBeginPos >= 0:
        speakingContent = speakingContent.replace(linkTag[0], "")
        linkTagEndPos = speakingContent.find(linkTag[1])+5
        linkTagString = speakingContent[linkTagBeginPos:linkTagEndPos]
        colonPos = linkTagString.find(":")
        speakingContent = speakingContent.replace(linkTagString[colonPos:], "")
        linkTagBeginPos = speakingContent.find(linkTag[0])

    return speakingContent

if __name__ == '__main__':
    word_filter = ['<', '>', '\\', '/', ',', '.']
    replace_list = ['＜','＞','＼','／', '，', '‧']
    pc = pcap.pcap('ens33')
    #filter = "(src host 203.70.17.33 or src host 203.70.17.34) and (dst host " + sniff_IP[0] + " or dst host " + sniff_IP[1] + ")"
    filter = "src host 210.242.123.1"
    pc.setfilter(filter)
    pattern = re.compile(".+:[0-9]:[0-9]:(.*?):[0-9]:.+")
    lastcontent = ""
    s = requests.Session()
    account_monitor = {}
    global account_index
    account_index = []

    for ptime,pdata in pc:
        _skip = False
        eth = dpkt.ethernet.Ethernet(pdata)
        if not isinstance(eth.data, dpkt.ip.IP):
            print 'Non IP Packet type %s\n' % eth.data.__class__.__name__
            continue
        packet = eth.data
        df = bool(packet.off & dpkt.ip.IP_DF)
        mf = bool(packet.off & dpkt.ip.IP_MF)
        offset = packet.off & dpkt.ip.IP_OFFMASK
        output1 = {'time':time.strftime("%Y-%m-%d %H:%M:%S", (time.localtime(ptime)))}
        ip_dst = socket.inet_ntoa(packet.dst)
        tcp = packet.data
        data = tcp.data

        #print(ip_dst)
        if ip_dst in account_monitor:
            account_monitor[ip_dst]+=1
            #print(account_monitor[ip_dst])
        else:
            account_monitor.update({ip_dst:1})
            account_index = account_monitor.keys() #python2
            #account_index = list(account_monitor.keys()) #python3
            print(account_index)


        if len(data) == 0:
            #print "heartbeat"
            lastcontent = ""
            if account_monitor[ip_dst] == 20:
                pushdata("@KONODIODA", "", ip_dst)
                account_monitor[ip_dst] = 0
            continue

        print output1

        stageAData = ''
        #print "data lenth: " + str(len(data))
        startpos = 27

        for i in range(startpos, len(data), 2):
            try:
                currnetData = '\u' + binascii.hexlify(data[i+1]) + binascii.hexlify(data[i])

            except IndexError:
                print "Unknown package, Skip"
                _skip = True
                break

            stageAData = stageAData + currnetData

        if _skip:
            continue
            
        try:
            stageBData = stageAData.decode('unicode-escape', errors='ignore').encode('utf-8')
            print stageBData
        except UnicodeDecodeError:
            print "UnicodeDecodeError"
            continue

        if "<party-chatrecruit" in stageBData:
            #F7 message
            continue

        matchobj = pattern.match(stageBData)
        try:
            playerName = stageBData[matchobj.start(1):matchobj.end(1)]
            #Get position of player name
            #Player Name START matchobj.start(1)
            #Player Name END   matchobj.end(1)

            stageBData = stageBData[matchobj.end(1):]
            #delete useless data
        except AttributeError:
            print "Player name not found"
            continue

        speakingContentPos =  stageBData.find('/')
        speakingContent = tag_filter(stageBData[speakingContentPos+1:])

        for i in range(0, len(word_filter)):
            speakingContent = speakingContent.replace(word_filter[i], replace_list[i])

        print speakingContent
        
        #VMWare NAT sometime gives duplicate packets with different timestamp, and I don't know why.
        #There's no those duplicate packets when I using bridged mode.
        if speakingContent == lastcontent:
            continue
        else:
            lastcontent = speakingContent

        pushdata(playerName, speakingContent, ip_dst)
        account_monitor[ip_dst] = 0
