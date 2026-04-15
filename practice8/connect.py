import psycopg2
from config import load_config


def get_connection():
    return psycopg2.connect(**load_config())