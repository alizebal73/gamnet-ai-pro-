$ErrorActionPreference = "Stop"

python -m pip install -r requirements.txt
python -m pytest -q
python -m PyInstaller --noconfirm --clean --name GameNetOperator gamenet/operator_app/main.py
python -m PyInstaller --noconfirm --clean --name GameNetClient gamenet/client_agent/main.py
python -m PyInstaller --noconfirm --clean --name GameNetServer gamenet/server/main.py