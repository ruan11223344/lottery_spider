#!/usr/bin/env python
# coding:utf-8
"""
@Auth ： Just
@File : lottery.py
@Date : 2018/8/29
"""
from sqlalchemy import Column, Integer, BigInteger, VARCHAR, DateTime
from config import Base
from sqlalchemy import func
from config import CurrentConfig as Config


class Lottery(Base):
	__tablename__ = Config.lottery_table_name
	id = Column(Integer, autoincrement=True, primary_key=True, comment=u'ID')
	room_id = Column(BigInteger, nullable=False, comment=u'房间号')
	lottery_prize = Column(VARCHAR(100), nullable=False, comment=u'奖品')
	platform = Column(VARCHAR(20), nullable=False, comment=u'直播平台')
	lottery_time = Column(Integer(), nullable=False, comment=u'开奖时间')
	condition = Column(VARCHAR(200), nullable=False, comment=u'参与条件')
	location = Column(VARCHAR(255), nullable=True, comment=u'url地址')
	avatar = Column(VARCHAR(255), nullable=True, comment=u'头像地址')
	anchor_name = Column(VARCHAR(255), nullable=True, comment=u'主播名称')
	members = Column(Integer(), default=0, comment=u'参与人数')
	create_time = Column(DateTime(timezone=True), server_default=func.now(), comment=u'创建时间')
