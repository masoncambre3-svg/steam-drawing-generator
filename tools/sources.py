"""Where the TI source PDFs are for this session.

The PDFs are not kept in the repo. Attach them to the chat, then point these at the uploaded files
(or set the environment variables). Only needed when tracing; existing packs do not need them.
"""
import os

UP = "/mnt/user-data/uploads/"
V1 = os.environ.get("SDG_PHB_V1", UP + "11_-_NOVEMBER_-_US_PHB_2026_-_VOLUME_1.pdf")   # US Product Handbook, volume 1
V2 = os.environ.get("SDG_PHB_V2", UP + "11_-_NOVEMBER_-_US_PHB_2026_-_VOLUME_2.pdf")   # US Product Handbook, volume 2
A3S_PDF = os.environ.get("SDG_A3S", UP + "A3S_A3SS-TI-P132-09-EN.pdf")                  # TI-P132-09
S5_PDF = os.environ.get("SDG_S5", UP + "S5-TI-P023-11-EN.pdf")                      # TI-P023-11, S5 separator
S6_PDF = os.environ.get("SDG_S6", UP + "S6-TI-P023-12-EN.pdf")                      # TI-P023-12, S6 separator
S4A_PDF = os.environ.get("SDG_S4A", UP + "S4A-TI-P139-02-US.pdf")                   # TI-P139-02-US, S4A 1/2"-6" (raster drawing)
S4A818_PDF = os.environ.get("SDG_S4A818", UP + "S4A_8_18-TI-P139-03-US.pdf")        # TI-P139-03-US, S4A 8"-18" (filled shapes)
UFT32_PDF = os.environ.get("SDG_UFT32", UP + "UFT32-TI-P146-05-EN.pdf")             # TI-P146-05, UFT32 trap unit
MANIFOLD_PDF = os.environ.get("SDG_MSCMSD", UP + "MSD-MSC-MANIFOLDS-TI-P115-03-US.pdf")  # TI-P115-03-US, MSC / MSD manifolds
SIGHT_PDF = os.environ.get("SDG_SIGHT", UP + "83f1414c-Sight_Check-TI-P022-01-EN.pdf")   # TI-P022-01, Sight Check
SDCV44_PDF = os.environ.get("SDG_SDCV44", UP + "b835a6dc-SDCV44-TI-P154_10-US.pdf")       # TI-P154-10-US, SDCV44 split disc
LCV_PDF = os.environ.get("SDG_LCV", UP + "e2caf807-LCV3-TI-P029-16-EN.pdf")               # TI-P029-16, LCV3/4/6/7 lift check
DCV41_PDF = os.environ.get("SDG_DCV41", UP + "651cdc45-DCV41-TI-P601-18-EN.pdf")          # TI-P601-18, DCV41 disc check
DCV10_PDF = os.environ.get("SDG_DCV10", UP + "fe86f086-DCV10-TI-P601-32-US.pdf")          # TI-P601-32-US, DCV10 wafer check
CVS10_PDF = os.environ.get("SDG_CVS10", UP + "10cb141f-CVS10-TI-P029-21-EN.pdf")          # TI-P029-21, CVS10 sanitary check
UFT14HC_PDF = os.environ.get("SDG_UFT14HC", UP + "3c9f233e-UFT14HC-TI-P712-01-EN.pdf")   # TI-P712-01, UFT14HC trap unit
UBP32_PDF = os.environ.get("SDG_UBP32", UP + "fd091e27-UBP32-TI-P127-01-EN.pdf")         # TI-P127-01, UBP32 trap unit
UTDS46M_PDF = os.environ.get("SDG_UTDS46M", UP + "9183f1c8-UTDS46M-TI-P187-03-EN.pdf")   # TI-P187-03, UTDS46M trap unit
UIB45_PDF = os.environ.get("SDG_UIB45", UP + "24064473-UIB45-TI-P113-03-EN.pdf")         # TI-P113-03, UIB45 + PC10HP
UIB30_PDF = os.environ.get("SDG_UIB30", UP + "737bf9bd-UIB30_30H-TI-P113-01-EN.pdf")     # TI-P113-01, UIB30 / UIB30H + PC10HP
UTD52L_PDF = os.environ.get("SDG_UTD52L", UP + "3ccb69c5-UTD52L-TI-P614-04-US.pdf")      # TI-P614-04-US, UTD52L (raster drawing)
STS17_PDF = os.environ.get("SDG_STS17", UP + "d21332df-STS172-TI-P128-22-EN.pdf")        # TI-P128-22, STS17.2 trapping station
PC4000_PDF = os.environ.get("SDG_PC4000", UP + "1b5397a0-PC4001-TI-P128-33-EN.pdf")      # TI-P128-33, PC4001 / PC4000 / PC40
