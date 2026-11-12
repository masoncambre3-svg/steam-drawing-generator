"""Where the TI source PDFs are for this session.

The PDFs are not kept in the repo. Attach them to the chat, then point these at the uploaded files
(or set the environment variables). Only needed when tracing; existing packs do not need them.
"""
import os

UP = "/mnt/user-data/uploads/"
V1 = os.environ.get("SDG_PHB_V1", UP + "11_-_NOVEMBER_-_US_PHB_2026_-_VOLUME_1.pdf")   # US Product Handbook, volume 1
V2 = os.environ.get("SDG_PHB_V2", UP + "11_-_NOVEMBER_-_US_PHB_2026_-_VOLUME_2.pdf")   # US Product Handbook, volume 2
A3S_PDF = os.environ.get("SDG_A3S", UP + "A3S_A3SS-TI-P132-09-EN.pdf")                  # TI-P132-09
