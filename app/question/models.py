# coding: utf-8
from sqlalchemy import BigInteger, Column, DECIMAL, Date, DateTime, Enum, Float, ForeignKey, Index, Integer, JSON, String, TIMESTAMP, Table, Text, text, Boolean
from sqlalchemy.dialects.mysql import LONGTEXT, TINYINT, VARCHAR, YEAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()
metadata = Base.metadata
class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    pair_id = Column(String)
    answer_json = Column(JSON)
    sort_order = Column(Integer)