import sys
import os
import logging

# Add current directory to path
sys.path.append(os.getcwd())

from src.robust_extractor import RobustExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)

# User provided text (mangled OCR output)
user_text_mangled = """
o Ñ INSTITUTO FEDERAL ELECTORAL
e] REGISTRO FEDERAL DE ELECTORES o
“esoo CREDENCIAL PARA VOTAR
A A A a
RAMIREZ AB IT
ESO AZ e,
=RIVANO:=> == ZA
O | Ñ a 9
—ABERTO- MARTINEZ: ==
—COL.ENDAVISTAS4040: TA a A)
a NE )
Fono 150236756-=-= AÑODEREGISTRO: 7200300 ==: sa,
UE DERIECTOR RMS TSLB5O20 OMS === Ha
A A a a a .
Dal e óAlTO: ===2 ES
múicino- 005 —tecapio=000 - sección O198- == = A >
"""

# Clean text from screenshot (simulated)
user_text_clean = """
INSTITUTO NACIONAL ELECTORAL
CREDENCIAL PARA VOTAR
NOMBRE
RAMIREZ
SOTO
SILVANO
DOMICILIO
COL HECTOR MAYAGOITIA DOMINGUEZ 34010
DURANGO, DGO
CLAVE DE ELECTOR RMSTSL85020410H300
CURP RASS850204HDGMTL06
AÑO DE REGISTRO 2003 02
"""

print("="*50)
print("TEST 1: MANGLED TEXT")
curp = RobustExtractor.find_curp_fuzzy(user_text_mangled)
print(f"Result: {curp}")

print("\n" + "="*50)
print("TEST 2: CLEAN TEXT (FROM SCREENSHOT)")
curp = RobustExtractor.find_curp_fuzzy(user_text_clean)
print(f"Result: {curp}")
if curp == "RASS850204HDGMTL06":
    print("✅ PERFECT MATCH!")
else:
    print("❌ NO MATCH")


print("="*50)
