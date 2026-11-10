# FIN 4600 Lab: Smart Contracts on a Test Chain

**Fintech Foundations · Michigan Technological University**
Companion to study guide **gen-08 (Ethereum)** and the lecture slides on smart contracts.

In this lab you run real **Solidity** smart contracts on a **private Ethereum blockchain that runs inside your Jupyter notebook**. You will see what gas costs, how one line of code controls who may act, the escrow from Nofsinger Figure 5.3, a token the issuer can freeze the way stablecoin issuers do, and the 2016 DAO hack re-created and fixed.

**You do not need to know how to program.** All the code is written for you and every line is explained in comments. Your job is to run it, predict what will happen, try small experiments (change one value and run again), and answer the written questions. Along the way you will pick up how Python and Jupyter notebooks work.

**No wallet, no seed phrase, no real or test money.** The blockchain lives in your computer's memory and disappears when you restart the notebook.

## What you need

* [git](https://git-scm.com/downloads)
* [uv](https://docs.astral.sh/uv/getting-started/installation/) (installs the right Python for you)
* An internet connection the first time (to download packages and the Solidity compiler, about 10 MB)

## Set up and run (command line)

```bash
git clone https://github.com/jnorthey-mtu/mtu-fin4600-lab-smart-contracts.git
cd mtu-fin4600-lab-smart-contracts
uv sync                 # creates .venv with the exact package versions in uv.lock
uv run jupyter lab      # opens JupyterLab in your browser
```

Open `smart_contracts_lab.ipynb` and run the cells in order (Shift+Enter).

## Missions

| # | Mission | Points |
|---|---|---|
| 1 | Accounts, addresses, and why ether is counted in wei | 10 |
| 2 | A free *read* vs. a paid *transaction*, and what gas costs | 15 |
| 3 | Access control: one line decides who may act | 15 |
| 4 | The escrow from Figure 5.3, with no bank in the middle | 15 |
| 5 | A token the issuer can freeze | 10 |
| 6 | The 2016 DAO hack, re-created and fixed | 20 |
| 7 | What it all cost, and what a Layer 2 changes | 15 |

Look for 🔮 (predict before you run), 🧪 (change one value and run again) and ✍️ (written answer, graded).

## What's in this repo

| Path | What it is |
|---|---|
| `smart_contracts_lab.ipynb` | The lab notebook |
| `contracts/` | Solidity source: `SimpleStorage`, `Escrow`, `ClassToken`, `VulnerableBank`, `Attacker` |
| `helpers/chain.py` | Small wrappers around web3.py and the in-memory test chain |
| `pyproject.toml`, `uv.lock` | Python project and pinned dependencies |

## Troubleshooting

* **"Downloading solc" fails:** you need internet access the first time; try again on campus Wi-Fi or another network.
* **Something got stuck:** *Kernel → Restart Kernel and Run All Cells*. The chain starts fresh every time.
* **`ModuleNotFoundError: helpers`:** start JupyterLab from inside the repo folder with `uv run jupyter lab`.

## Want to try more?

* Paste any file from `contracts/` into [Remix IDE](https://remix.ethereum.org) and deploy it to the in-browser **Remix VM**.
* Read the [Solidity documentation](https://docs.soliditylang.org) and the [web3.py documentation](https://web3py.readthedocs.io).

> **Safety:** these contracts are classroom examples and are not audited. Never deploy them to Ethereum mainnet, and never type a seed phrase or private key into a notebook or website.
