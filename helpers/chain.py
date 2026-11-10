"""Helpers for the FIN 4600 smart contract lab.

You do not need to read this file to do the lab, but every line is explained if you are curious.

Everything runs on a private, in-memory Ethereum blockchain provided by two Python libraries:
  * web3.py    : the standard Python library for talking to Ethereum (the real network or a test one)
  * eth-tester : a complete Ethereum blockchain that lives in your computer's memory, with 10 funded accounts
There is no wallet, no real money and no test money, and nothing is published anywhere.

A text in triple quotes right under a "def" line (like this one at the top of the file) is a DOCSTRING:
it documents what the function does. Type help(function_name) in a notebook cell to read it.
"""
# This line lets us write type hints such as "list[dict]" on older Python versions. You can ignore it.
from __future__ import annotations

# Path makes it easy to build file paths (folder/file) that work on Windows, macOS and Linux.
from pathlib import Path

import pandas as pd                               # tables
import solcx                                      # downloads and runs the Solidity compiler (solc)
from web3 import EthereumTesterProvider, Web3     # the Ethereum library and its in-memory test blockchain

# ---------------------------------------------------------------------------------------------
# Settings used throughout the file. CAPITAL names are a convention for "this value does not change".
# ---------------------------------------------------------------------------------------------
SOLC_VERSION = "0.8.28"                                              # the Solidity compiler version we use
CONTRACTS = Path(__file__).resolve().parent.parent / "contracts"     # the contracts/ folder next to helpers/
GAS_LOG: list[dict] = []    # an empty list; every transaction we send adds one row here (see _log below)


# ---------------------------------------------------------------------------------------------
# The compiler: turns human-readable Solidity into bytecode the Ethereum Virtual Machine can run
# ---------------------------------------------------------------------------------------------
def setup_compiler() -> str:
    """Download the Solidity compiler once (about 10 MB) and select it."""
    # Ask solcx which compiler versions are already on this computer, as a list of strings.
    installed = [str(v) for v in solcx.get_installed_solc_versions()]
    if SOLC_VERSION not in installed:                 # only download if we do not have it yet
        print(f"Downloading solc {SOLC_VERSION} (one time only)...")
        solcx.install_solc(SOLC_VERSION)
    solcx.set_solc_version(SOLC_VERSION)              # use this version from now on
    return f"solc {SOLC_VERSION} ready"               # "return" hands a value back to whoever called us


def read_contract(filename: str) -> str:
    """Return the Solidity source code of a file in the contracts/ folder."""
    return (CONTRACTS / filename).read_text()         # "/" joins a folder and a file name into a path


def compile_source(source: str, name: str) -> dict:
    """Compile Solidity source code and return {'name', 'abi', 'bytecode'} for one contract.

    abi      = the "menu" of functions outside programs may call, and what inputs they take
    bytecode = the machine code that gets stored on the blockchain and run by every node
    """
    # The compiler returns a dictionary with one entry per contract in the source code.
    out = solcx.compile_source(source, output_values=["abi", "bin"], solc_version=SOLC_VERSION)
    # Each key looks like "<stdin>:ContractName". Find the one whose name matches.
    for key, value in out.items():
        if key.split(":")[-1] == name:                # split at ":" and take the last piece
            return {"name": name, "abi": value["abi"], "bytecode": value["bin"]}
    # If we get here, no contract had that name: stop with a helpful error message.
    raise ValueError(f"No contract named {name!r} in this source. Found: {[k.split(':')[-1] for k in out]}")


# ---------------------------------------------------------------------------------------------
# The blockchain
# ---------------------------------------------------------------------------------------------
def new_chain() -> Web3:
    """Start a fresh private blockchain with 10 funded test accounts (and clear the gas log)."""
    GAS_LOG.clear()                                   # forget transactions from any earlier chain
    return Web3(EthereumTesterProvider())             # Web3 connected to a brand-new in-memory chain


def balance_eth(w3: Web3, address: str) -> float:
    """Ether balance of an account or contract, as an ordinary decimal number."""
    # The chain stores balances in wei (1 ether = 10**18 wei); from_wei converts to ether.
    return float(w3.from_wei(w3.eth.get_balance(address), "ether"))


def _log(label: str, receipt) -> None:
    """Record one transaction in GAS_LOG. (A leading _ means "internal: used only inside this file".)"""
    GAS_LOG.append({"operation": label, "gas_used": receipt.gasUsed, "block": receipt.blockNumber})


def deploy(w3: Web3, compiled: dict, *args, sender: str, value_eth: float = 0, label: str | None = None):
    """Deploy (publish) a compiled contract and return a contract object you can call.

    *args      : any inputs the contract's constructor needs, in order (the * collects them all)
    sender     : the account that pays for and signs the deployment
    value_eth  : ether to send along with the deployment (for example a deposit)
    """
    # A "factory" knows the contract's ABI and bytecode and can build the deployment transaction.
    factory = w3.eth.contract(abi=compiled["abi"], bytecode=compiled["bytecode"])
    # Build and send the transaction. It returns a transaction hash: the transaction's unique ID.
    tx_hash = factory.constructor(*args).transact({"from": sender, "value": w3.to_wei(value_eth, "ether")})
    # Wait until the transaction is in a block, then get its receipt (the official record).
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    label = label or f"deploy {compiled['name']}"     # "or": use our label if given, otherwise a default
    _log(label, receipt)
    print(f"✅ {label}: address {receipt.contractAddress[:10]}..., gas used {receipt.gasUsed:,}")
    # Return an object pointing at the new contract's address, so we can call its functions.
    return w3.eth.contract(address=receipt.contractAddress, abi=compiled["abi"])


def transact(w3: Web3, fn, sender: str, value_eth: float = 0, label: str | None = None):
    """Send a transaction that runs a contract function on every node. Returns the receipt."""
    tx_hash = fn.transact({"from": sender, "value": w3.to_wei(value_eth, "ether")})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    label = label or fn.fn_name                       # default label: the function's name
    _log(label, receipt)
    print(f"✅ {label}: gas used {receipt.gasUsed:,}")
    return receipt


def try_transact(w3: Web3, fn, sender: str, value_eth: float = 0, label: str | None = None):
    """Like transact(), but if the contract refuses (a "revert") it prints the reason instead of stopping.

    Returns two values: (True, receipt) if it worked, or (False, reason) if the contract refused.
    """
    label = label or fn.fn_name
    # try / except: "try this; if an error happens, run the except block instead of crashing".
    try:
        return True, transact(w3, fn, sender, value_eth, label)
    except Exception as exc:    # web3 raises a ContractLogicError when a require(...) fails
        # Get the error text and strip the standard prefix so only the contract's own reason is left.
        reason = getattr(exc, "message", None) or str(exc)
        reason = reason.replace("execution reverted: ", "").strip()
        print(f"⛔ {label}: refused (reverted), reason: {reason!r} (nothing changed on chain)")
        return False, reason


def time_travel(w3: Web3, days: float) -> None:
    """Move the test chain's clock forward by some days and add a block. (Impossible on the real network!)"""
    tester = w3.provider.ethereum_tester              # reach the in-memory chain underneath web3
    now = w3.eth.get_block("latest").timestamp        # time of the newest block, in seconds since 1970
    tester.time_travel(int(now + days * 86_400))      # 86,400 seconds in a day
    tester.mine_blocks(1)                             # make a new block with the new time
    print(f"⏩ clock moved forward {days} days")


def events(contract, event_name: str) -> pd.DataFrame:
    """All events (log messages) of one type that a contract has emitted, as a table."""
    logs = getattr(contract.events, event_name).get_logs(from_block=0)   # search from the first block
    # Each log's "args" are the values the contract wrote; add the block number and make a table.
    return pd.DataFrame([{**dict(log["args"]), "block": log["blockNumber"]} for log in logs])


def gas_table() -> pd.DataFrame:
    """Every transaction sent through deploy() and transact() since new_chain(), as a table."""
    return pd.DataFrame(GAS_LOG)


# ---------------------------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------------------------
def check(condition, ok: str, fail: str) -> bool:
    """Print ✅ and the ok message if condition is true, otherwise ❌ and the fail message.

    It never crashes: if working out the condition causes an error, it just counts as ❌.
    (condition may also be a function with no inputs; it is then run here, inside the safety net.)
    """
    try:
        passed = bool(condition() if callable(condition) else condition)
    except Exception:
        passed = False
    print(("✅ " + ok) if passed else ("❌ " + fail))
    return passed
