import os
from os.path import join

from dotenv import load_dotenv

dotenv_path = join(os.getcwd(), ".env.test")
load_dotenv(dotenv_path)
