@echo off
:loop
python C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\PHYSICS\percolation_3d\CODE\run_exp0011.py
if %errorlevel% neq 0 (echo ERROR %date% %time% >> C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\PHYSICS\percolation_3d\CODE\LOG\errors.log & timeout /t 60 >nul)goto loop
