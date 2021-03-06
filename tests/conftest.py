#!/usr/bin/python3

import pytest
from brownie import Contract, network
from brownie.network.contract import InterfaceContainer
from brownie.network.state import _add_contract, _remove_contract

@pytest.fixture(scope="module")
def Constants():
    return {
        "ZERO_ADDRESS": "0x0000000000000000000000000000000000000000",
        "ONE_ADDRESS": "0x0000000000000000000000000000000000000001",
        "MAX_UINT": "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    }

@pytest.fixture(scope="module")
def DAI(accounts, TestToken):
    return accounts[0].deploy(TestToken, "DAI", "DAI", 18, 1e50)

@pytest.fixture(scope="module")
def LINK(accounts, TestToken):
    return accounts[0].deploy(TestToken, "LINK", "LINK", 18, 1e50)

@pytest.fixture(scope="module")
def priceFeeds(accounts, WETH, DAI, LINK, PriceFeeds, PriceFeedsLocal):
    if network.show_active() == "development":
        feeds = accounts[0].deploy(PriceFeedsLocal)

        feeds.setRates(
            WETH.address,
            LINK.address,
            54.52e18
        )
        feeds.setRates(
            WETH.address,
            DAI.address,
            200e18
        )
        feeds.setRates(
            LINK.address,
            DAI.address,
            3.692e18
        )
    else:
        feeds = accounts[0].deploy(PriceFeeds)
        #feeds.setPriceFeedsBatch(...)

    return feeds

@pytest.fixture(scope="module")
def swapsImpl(accounts, SwapsImplKyber, SwapsImplLocal):
    if network.show_active() == "development":
        feeds = accounts[0].deploy(SwapsImplLocal)
    else:
        feeds = accounts[0].deploy(SwapsImplKyber)
        #feeds.setPriceFeedsBatch(...)

    return feeds

@pytest.fixture(scope="module", autouse=True)
def bzx(accounts, interface, bZxProtocol, ProtocolSettings, LoanSettings, LoanMaintenance):
    bzxproxy = accounts[0].deploy(bZxProtocol)
    bzx = Contract.from_abi("bzx", address=bzxproxy.address, abi=interface.IBZx.abi, owner=accounts[0])
    _add_contract(bzx)
    
    bzx.replaceContract(accounts[0].deploy(ProtocolSettings).address)
    bzx.replaceContract(accounts[0].deploy(LoanSettings).address)
    bzx.replaceContract(accounts[0].deploy(LoanMaintenance).address)
    
    return bzx

@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    pass

@pytest.fixture(scope="module", autouse=True)
def WETH(module_isolation, accounts, TestWeth):
    yield accounts[0].deploy(TestWeth) ## 0x3194cBDC3dbcd3E11a07892e7bA5c3394048Cc87
