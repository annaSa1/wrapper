#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import requests
import json
import time
import io
import logging

#logging.basicConfig(filename="Parse.log",level=logging.DEBUG)
logging.basicConfig(filename="Parse.log",level=logging.INFO)

fileUrl='/home/blockchainuser2/bin/Tokens.txt'

class Parse(object):
    def __init__(self,
                 last_block=0,
                 load=False):
        """Initialize with a geth client and an optional last block."""
        self.last_block = last_block
        self.url = "http://127.0.0.1:8545"
        self.headers = {"content-type": "application/json"}
        if load:
            self.checkGeth(last_block)

    def checkGeth(self, block_id=0):
        """Make sure geth is running in RPC on port 8545."""
        try:
            return self._rpcRequest("eth_getBlockByNumber", [hex(block_id), True], block_id)
        except Exception as err:
            assert not err, "Geth cannot be reached: {}".format(err)


    def getTransactionReceipt(self, tXhash=0):
        """Make sure geth is running in RPC on port 8545."""
        try:
            return self._rpcRequest("eth_getTransactionReceipt", [tXhash], tXhash)
        except Exception as err:
            assert not err, "Geth cannot be reached: {}".format(err)

    def _rpcRequest(self, method, params, block_id):
        """Make an RPC request to geth on port 8545."""
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": block_id
        }
        res = requests.post(self.url,
                            data=json.dumps(payload),
                            headers=self.headers).json()
        # Geth will sometimes crash if overloaded with requests
        time.sleep(0.05)
        return res

class Saver(object):
    def __init__(self, parse,
                 last_block=0,
                 load=False):
        """Initialize with a GremlinServer."""
        self.parse = parse
        self.last_block = last_block
        self.url = "http://127.0.0.1:8182"
        self.headers = {"content-type": "application/json"}
        if load:
            self.checkGremlin(last_block)

    def checkGremlin(self, block_id=0):
        """Make sure GremlinServer is running in RPC on port 8182."""
        try:
            return self._rpcRequest("g.V().count()")
        except Exception as err:
            assert not err, "GremlinServer cannot be reached: {}".format(err)

    def __addTransaction(self, parsed_transaction=""):
        """add Transaction to GremlinServer."""
        #print("receiver=" + str(parsed_transaction['to']))
        #print("Is transaction")
        if "0x" == str(parsed_transaction['input']):
            transaction_input='empty'
        else:
            transaction_input=str(parsed_transaction['input'])

        if str(parsed_transaction['from']) == str(parsed_transaction['to']):
            rpcRequestVar="addLoopbackTransaction(graph, '" + str(parsed_transaction['from']) + "', '" + str(parsed_transaction['hash']) + "', " + str(int(parsed_transaction['blockNumber'], 0)) + ", '" + transaction_input + "', '" + str(int(parsed_transaction['value'], 0)) + "')"
        else:
            rpcRequestVar="addTransaction(graph, '" + str(parsed_transaction['from']) + "', '" + str(parsed_transaction['hash']) + "', " + str(int(parsed_transaction['blockNumber'], 0)) + ", '" + transaction_input + "', '" + str(int(parsed_transaction['value'], 0)) + "', '" + str(parsed_transaction['to']) + "')"
        try:
            logging.debug(rpcRequestVar)
            self._rpcRequest(rpcRequestVar)
        except Exception as err:
            assert not err, "GremlinServer cannot be reached: {}".format(err)

    def __addContract(self, parsed_transaction=""):
        """add Contract to GremlinServer."""
        #        print("Contract Creation")
        #        print("action=contractCreation")
        #        print("from=" + str(parsed_transaction['from']))
        #        print("to=" + str(parsed_transaction['to']))
        #        print("input=" + str(parsed_transaction['input']))
        jsonString = self.parse.getTransactionReceipt(str(parsed_transaction['hash']))
        parsedTransactionReceipt = json.loads(json.dumps(jsonString))
        #        print("contractAddress=" + str(parsedTransactionReceipt['result']['contractAddress']))
        contractName='empty'
        #        print("contractBidy=" + str(parsed_transaction['input']))
        #        print("contractId=" + str(parsedTransactionReceipt['result']))
        #        print("contractAddress=" + str(parsedTransactionReceipt['result']))
        #        print("Is contract")
        with io.open(fileUrl, encoding='utf-8') as file:
            for line in file:
                if str(parsedTransactionReceipt['result']['contractAddress']) in line:
                    contractName=line.split('|')[0]
        try:
            rpcRequestVar="addContract(graph, '" + str(parsed_transaction['from']) + "', '" + str(parsed_transaction['hash']) + "', " + str(int(parsed_transaction['blockNumber'], 0)) + ", '" + str(parsed_transaction['input']) + "', '" + str(parsed_transaction['to']) + "', '" + contractName + "')"
            logging.debug(rpcRequestVar)
            self._rpcRequest(rpcRequestVar)
        except Exception as err:
            assert not err, "GremlinServer cannot be reached: {}".format(err)

    def __token_transfer(self, parsed_transaction="", parsedTransactionReceipt="", contractName="empty", typeEnd=0):
        """token transfer to GremlinServer."""
        #        print("toToken=0x" + str(parsed_transaction['input'][typeEnd+24:typeEnd+64]))
        #        print("valueToken=" + str(long(parsed_transaction['input'][typeEnd+64:], 16)))
        try:
            rpcRequestVar="addTokenTransfer(graph, '" + str(parsed_transaction['from']) + "', '" + str(parsed_transaction['hash']) + "', " + str(int(parsed_transaction['blockNumber'], 0)) + ", '" + str(parsed_transaction['input']) + "', '" + str(parsed_transaction['to']) + "', '" + contractName + "', '" + str(parsed_transaction['input'][typeEnd+24:typeEnd+64]) + "', '" + str(long(parsed_transaction['input'][typeEnd+64:], 16)) + "')"
            logging.debug(rpcRequestVar)
            self._rpcRequest(rpcRequestVar)
        except Exception as err:
            assert not err, "GremlinServer cannot be reached: {}".format(err)

    def __makeWallet(self, parsed_transaction=""):
        """make Wallet to GremlinServer."""
        jsonString = self.parse.getTransactionReceipt(str(parsed_transaction['hash']))
        parsedTransactionReceipt = json.loads(json.dumps(jsonString))
        for logs in parsedTransactionReceipt['result']['logs']:
            parsed_logs = json.loads(json.dumps(logs))
            #            print("contractAddress=" + parsed_logs['address'])
            logging.info("walletAddress=" + str(parsed_logs['data']).replace('000000000000000000000000','',1)  + " transactionID=" + str(parsed_transaction['hash']))
        #print("makeWallet=" + str(parsedTransactionReceipt['result']['logs']['address']))
    #        print("contractBody=" + str(parsedTransactionReceipt['result']))
    #        print("action=makeWallet")
    #        print("Is contract")
    #        print("============")

    def __addToken(self, parsed_transaction=""):
        """add Token to GremlinServer."""
        #        print("receiver=" + str(parsed_transaction['to']))
        typeEnd=parsed_transaction['input'].find("000000000000000000000000")
        token_type=str(parsed_transaction['input'][2:typeEnd])

        jsonString = self.parse.getTransactionReceipt(str(parsed_transaction['hash']))
        parsedTransactionReceipt = json.loads(json.dumps(jsonString))
        #        print("contractAddress=" + str(parsedTransactionReceipt['result']['contractAddress']))
        contractName='empty'
        with io.open(fileUrl, encoding='utf-8') as file:
            for line in file:
                if str(parsedTransactionReceipt['result']['contractAddress']) in line:
                    contractName=line.split('|')[0]

        if "18160ddd" == token_type:
            # TODO
            logging.info("block_n=" + str(int(parsed_transaction['blockNumber'], 0)) + " token_type=totalSupply" + " transactionID=" + str(parsed_transaction['hash']))
        elif "70a08231" == token_type:
            # TODO
            logging.info("block_n=" + str(int(parsed_transaction['blockNumber'], 0)) + " token_type=balanceOf" + " transactionID=" + str(parsed_transaction['hash']))
        elif "dd62ed3e" == token_type:
            # TODO
            logging.info("block_n=" + str(int(parsed_transaction['blockNumber'], 0)) + " token_type=allowance" + " transactionID=" + str(parsed_transaction['hash']))
        elif "a9059cbb" == token_type:
            self.__token_transfer(parsed_transaction, parsedTransactionReceipt, contractName, typeEnd)
        elif "095ea7b3" == token_type:
            # TODO
            logging.info("block_n=" + str(int(parsed_transaction['blockNumber'], 0)) + " token_type=approve" + " transactionID=" + str(parsed_transaction['hash']))
        #            print("toToken=0x" + str(parsed_transaction['input'][typeEnd+24:typeEnd+64]))
        #            print("valueToken=" + str(long(parsed_transaction['input'][typeEnd+64:], 16)))
        elif "23b872dd" == token_type:
            # TODO
            logging.info("block_n=" + str(int(parsed_transaction['blockNumber'], 0)) + " token_type=transferFrom" + " transactionID=" + str(parsed_transaction['hash']))
        else :
            # TODO
            logging.info("block_n=" + str(int(parsed_transaction['blockNumber'], 0)) + " token_type=" + token_type + " transactionID=" + str(parsed_transaction['hash']))
    #            print("token_body=" + parsed_transaction['input'])
    #        print("test input =" + str(parsed_transaction['input']))
    #        print("Is token")

    def __addBlock(self, parsed_block=""):
        """add Block to GremlinServer."""
        logging.info("result=" + str(parsed_block['result']))
    #        print(parsed_block['result']['transactions'])
    #        print("id=" + str(parsed_block['id']))
    #        print("nonce=" + str(parsed_block['nonce']))
    #        print("gasUsed=" + str(parsed_block['gasUsed']))
    #        print("extraData=" + str(parsed_block['extraData']))
    #        print("hash=" + str(parsed_block['hash']))
    #        print("sha3Uncles=" + str(parsed_block['sha3Uncles']))
    #        print("logsBloom=" + str(parsed_block['logsBloom']))
    #        print("timestamp=" + str(parsed_block['timestamp']))
    #        uncles': [], u'
    #        parentHash': u'0x49578f9c6520d31b6e2106a6e428a6ff54199ca1652ef91b381854d0be4ea601
    #        receiptsRoot': u'0x51500876bc5d29f980bcd5c0b598096f73fda1f7f374ea16ef12edd79bfeb74c
    #        miner': u'0xa42af2c70d316684e57aefcc6e393fecb1c7e84e
    #        print("number=" + str(int(parsed_block['result']['number'], 0)))
    #        stateRoot': u'0x5c7fdfff96ca8d7968648a894d046bfd5738b706b00cc82ffdad77f6c23c1d9d
    #        difficulty': u'0x2d565eb36b7b
    #        transactionsRoot': u'0x61655ae7f6a08b0580218c30e2a0acf43978b3fc452c8afdb3e3db1e148713ff',
    #        mixHash': u'0xd4d7a1686fc1d47f369dda886c2321a89856a4b5f7ac7eca9393d349ed46b3d2
    #        totalDifficulty': u'0x262c56aaf6a18b3c4
    #        print("size=" + str(parsed_block['size']))
    #        print("gasLimit=" + str(int(parsed_block['result']['gasLimit'], 0)))
    #print(parsed_block['result'])

    def saveToGremlinServer(self, jsonString=""):
        """Make sure geth is running on port 8182."""
        parsed_block = json.loads(json.dumps(jsonString))
        #self.__addBlock(parsed_block)
        if len(parsed_block['result']['transactions']) == 0:
            return ""
        else:
            logging.debug( "block_n=" + str(int(parsed_block['result']['number'], 0)) + " transactionsCount=" + str(len(parsed_block['result']['transactions'])))

        for tr in parsed_block['result']['transactions']:
            #            print(tr)
            parsed_transaction = json.loads(json.dumps(tr))
            #            print("nonce=" + str(int(parsed_transaction['nonce'], 0)))
            #            print("transactionID=" + str(parsed_transaction['hash']))
            #            print("blockHash=" + str(parsed_transaction['blockHash']))
            #            print("sender=" + str(parsed_transaction['from']))
            #            print("gas=" + str(int(parsed_transaction['gas'], 0)))
            #            print("value=" + str(int(parsed_transaction['value'], 0)))
            #            print("blockNumber=" + str(int(parsed_transaction['blockNumber'], 0)))
            #            print("s=" + str(parsed_transaction['s']))
            #            print("r=" + str(parsed_transaction['r']))
            #            print("v=" + str(parsed_transaction['v']))
            #            print("input=" + str(parsed_transaction['input']))
            #            print("transactionIndex=" + str(int(parsed_transaction['transactionIndex'], 0)))
            #            print("gasPrice=" + str(int(parsed_transaction['gasPrice'], 0)))

            if "None" == str(parsed_transaction['to']):
                self.__addContract(parsed_transaction)
            elif parsed_transaction['input'].find("000000000000000000000000") == 10:
                self.__addToken(parsed_transaction)
            elif parsed_transaction['input'].find("000000000000000000000000") == 42:
                self.__addToken(parsed_transaction)
            elif str(parsed_transaction['input']) == "0xa9b1d507":
                self.__makeWallet(parsed_transaction)
            else:
                self.__addTransaction(parsed_transaction)

    #            print("====V count=====" + str(self._rpcRequest("g.V().count()")))
    #            print("====E count=====" + str(self._rpcRequest("g.E().count()")))


    def _rpcRequest(self, method):
        """Make an request to gremlin server on port 8182."""
        payload = { "gremlin": method, }
        res = requests.post(self.url,
                            data=json.dumps(payload),
                            headers=self.headers).json()
        time.sleep(0.05)
        return res

if __name__ == '__main__':
    parse = Parse()
    save = Saver(parse)

    # TODO get last block from DB
    # save.last_block 209707

    for number in range(1, 5447258):
        logging.debug("block_n=" + str(number) + "")
        outputFromEth=parse.checkGeth(number)
        logging.debug("outputFromEth=" + str(number) + "")
        save.saveToGremlinServer(outputFromEth)

