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
