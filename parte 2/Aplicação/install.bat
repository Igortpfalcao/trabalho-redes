@echo off

py -m venv venv


call venv\Scripts\activate


py -m pip install -r requirements.txt


echo Ambiente virtual configurado e dependências instaladas com sucesso.
pause