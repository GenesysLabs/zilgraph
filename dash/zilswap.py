# -*- coding: utf-8 -*-

from pprint import pprint

from pyzil.zilliqa import chain
from pyzil.zilliqa.units import Zil
from pyzil.zilliqa.api import ZilliqaAPI
from pyzil.account import Account

from pyzil.contract import Contract

import time
import json

class pyzilly:

  def get_contract(self, contract_addr):
      contract = Contract.load_from_address(contract_addr)
      contract.get_state()
      pprint(contract.state)    
      return contract
    
class zilswap:
    def __init__(self, account):
        # Set mainnet
        chain.set_active_chain(chain.MainNet)  
        
        # Set contract
        _addr = "zil1hgg7k77vpgpwj3av7q7vv5dl4uvunmqqjzpv2w"
        self.contract = Contract.load_from_address(_addr, load_state=True)
        
        # Set account
        self.contract.account = account
        
        # Set Zilliqa API
        self.api = ZilliqaAPI("https://api.zilliqa.com/")
        
        
        # Load Zilgraph JSON 
        fp_json = open("zilgraph.json")
        self.tokens = json.load(fp_json)["tokens"]
        
        # Setup dictionaries
        self.token = {}
        self.decimals = {"zil" : 12}
        for tok in self.tokens:
            self.token[tok]      = Account(address=self.tokens[tok]["addr"])
            self.decimals[tok]   = self.tokens[tok]["decimals"]

    
    def get_contract(self):
        self.contract.get_state()
        pprint(self.contract.state)
      
    def zil_balance(self):
        balance = self.contract.account.get_balance()
        return balance
    
    def gzil_balance(self):
        gzil_contract = Contract.load_from_address(self.token["gzil"].bech32_address, load_state=True)
        balance = float(gzil_contract.state['balances'][self.contract.account.address0x])*1e-15
        return balance
    
    def buy_gzil(self, amount, max_price=2000):
        # Buy gZIL
        _min_token_amount = str(int(amount*1e15))
        _deadline_block = str(int(self.api.GetCurrentMiniEpoch())+15)
        
        _params = [Contract.value_dict("token_address", "ByStr20", self.token["gzil"].address0x),
                   Contract.value_dict("min_token_amount", "Uint128", _min_token_amount),
                   Contract.value_dict("deadline_block", "BNum", _deadline_block),
                   Contract.value_dict("recipient_address", "ByStr20", self.contract.account.address0x)]
        
        pprint(_params)
        
        _zils = Zil(max_price*amount)
        
        resp = self.contract.call(method="SwapExactZILForTokens", params=_params, amount=_zils, gas_limit=30000)
        pprint(resp)
        pprint(self.contract.last_receipt)
        
    def sell_gzil(self, amount, min_price=4000):
        # Sell gZIL
        _token_amount = str(int(amount*1e15))
        _deadline_block = str(int(self.api.GetCurrentMiniEpoch())+15)
        
        _min_zil_amount = str(int(min_price*amount*1e12))
        
        _params = [Contract.value_dict("token_address", "ByStr20", self.token["gzil"].address0x),
                   Contract.value_dict("token_amount", "Uint128", _token_amount),
                   Contract.value_dict("min_zil_amount", "Uint128", _min_zil_amount),
                   Contract.value_dict("deadline_block", "BNum", _deadline_block),
                   Contract.value_dict("recipient_address", "ByStr20", self.contract.account.address0x)]
        
        pprint(_params)
        
        resp = self.contract.call(method="SwapExactTokensForZIL", params=_params, gas_limit=30000)
        pprint(resp)
        pprint(self.contract.last_receipt)

    def get_gzil_rate(self):
        self.contract.get_state()
        _poolsize = self.contract.state['pools'][self.token["gzil"].address0x]['arguments']
        _rate = (int(_poolsize[0])*1e-12) / (int(_poolsize[1])*1e-15)
        return _rate


    def get_gzil_market(self):
        self.contract.get_state()
        _poolsize = self.contract.state['pools'][self.token["gzil"].address0x]['arguments']
        
        _liq_zil = (int(_poolsize[0])*1e-12)
        _liq_gzil = (int(_poolsize[1])*1e-15)
        _rate = _liq_zil / _liq_gzil
        
        _market_data_point = {"_id": int(time.time()),
                              "rate": _rate,
                              "liq_zil": _liq_zil,
                              "liq_gzil": _liq_gzil}
        
        return _market_data_point
    
        
    def get_market(self, tokenstr):        
        _time = int(time.time())
        self.contract.get_state()
        _poolsize = self.contract.state['pools'][self.token[tokenstr].address0x]['arguments']
        
        _liq_zil = int(_poolsize[0])*1e-12
        _liq_token = int(_poolsize[1])*pow(10,-self.decimals[tokenstr])
        _rate = _liq_zil / _liq_token
        
        _market_data_point = {"_id": _time,
                              "rate": _rate,
                              "liq_zil": _liq_zil,
                              "liq_"+tokenstr: _liq_token}
        
        return _market_data_point


