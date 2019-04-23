#!/usr/bin/env python
# coding:utf-8
"""
@Auth ： Just
@File : douyu_lottery.py
@Date : 2018/8/29
"""
import sys
import json
import re
import time
import gevent
from gevent import monkey
monkey.patch_all()
from douyu_config import DYConfig as Config
from douyu_logger import DOUYU_LOTTERY_LOG as LOG
from base_lottery import BaseLottery
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class DouyuLottery(BaseLottery):
	def __init__(self):
		BaseLottery.__init__(self,Config,LOG)
		self.start_time = time.time()

	def get_all_rooms(self):
		jobs = [gevent.spawn(self.scrapy, Config.lottery_list.format(page=i+1)) for i in range(0,25)]
		gevent.joinall(jobs)
		for job in jobs:
			if job.value:
				yield job.value.json()
			else:
				self.fail_page += 1

	def get_lottery_rooms(self):
		lottery_rooms = []
		for content in self.get_all_rooms():
			try:
				if content['msg'] == '操作成功':
					for room in content['data']:
							lottery_rooms.append(room)
				else:
					self.fail_page += 1
			except Exception, e:
				self.fail_page += 1
				LOG.error('page_url 的内容有误 value:{content},msg:{msg}'.format(content=content,msg=e.message))
		self.total_lottery_room = len(lottery_rooms)
		return lottery_rooms

	def scapy_lottery_room(self):
		lottery_rooms = self.get_lottery_rooms()
		unique_list = lambda x, y: x if y in x else x + [y]
		lottery_rooms = reduce(unique_list, [[], ] + lottery_rooms)
		jobs = [gevent.spawn(self.scrapy, Config.lottery_url.format(roomid=roomItem['roomId'])) for roomItem in lottery_rooms]
		gevent.joinall(jobs)
		for job in jobs:
			if job.value:
				if not job.value.content:
					self.fail_lottery_room+=1
				else:
					yield job.value
			else:
				self.fail_lottery_room+=1

	def get_lotteryInfo(self):
		prize_num = 0
		try:
			for content in self.scapy_lottery_room():
				if content is not None:
					content = content.json()
					if content["data"] is not None:
						content = content["data"]
						self.lottery_prize = content["prize_name"]
						self.roomid = content['room_id']
						self.platform = Config.platform
						if content.has_key("prize_num"):
							prize_num = content["prize_num"]
						if content["join_condition"].has_key("command_content"):
							self.lottery_condition = json.dumps({"command": content["join_condition"]["command_content"], "prize_num": prize_num,"lottery_range":content["join_condition"]["lottery_range"]})
						elif content["join_condition"].has_key("gift_id"):
							self.lottery_condition = json.dumps({"giftid": content["join_condition"]["gift_id"],"num": content["join_condition"]["gift_num"],"prize_num": prize_num,"lottery_range":content["join_condition"]["lottery_range"]})
						if int(content["stop_at"]) == 0:
							self.lottery_time = int(content["start_at"]) + content["join_condition"]["expire_time"]
						else:
							self.lottery_time = int(content["stop_at"])
					self.format_lottery_datas()
		except Exception as e:
			print e
			LOG.error("update platform info failed {msg}".format(msg=e.message))

	def get_roomInfo(self):
		roomInfoDict = {}
		roomInfoList = []
		for content in self.scapy_room_info():
			if content:
				roomInfo = content.json()
				roomInfoList.append(roomInfo[u'data'])
				roomInfoDict[str(roomInfo[u'data'][u'room_id'])] = len(roomInfoList) - 1

		for lottery_data in self.lottery_datas:
			try:
				data_key = roomInfoDict[str(lottery_data['room_id'])]
				itemData = roomInfoList[data_key]
				lottery_data['avatar'] = itemData[u'owner_avatar']
				lottery_data['anchor_name'] = itemData[u'nickname']
				lottery_data['location'] = "https://www.douyu.com/"+str(itemData[u'room_id'])
			except Exception as e:
				print(e)

	def scapy_room_info(self):
		jobs = [gevent.spawn(self.scrapy, Config.room_info.format(roomid=roomItem['room_id'])) for roomItem in
				self.lottery_datas]
		gevent.joinall(jobs)
		for job in jobs:
			if job.value:
				if not job.value.content:
					pass
				else:
					yield job.value
			else:
				pass

	def run(self):
		self.get_lotteryInfo()
		self.get_roomInfo()
		self.update_lottery()
		LOG.info('总共{total_page}页，失败{fail_page}页，总共{total_lottery_room}间直播抽奖，失败{fail_lottery_room}间,耗时{times}'.format(total_page=self.total_page,fail_page=self.fail_page,total_lottery_room=self.total_lottery_room,fail_lottery_room=self.fail_lottery_room,times=str(time.time()-self.start_time)))


if __name__ == '__main__':
	while True:
		t = DouyuLottery()
		start_time = time.time()
		t.get_lotteryInfo()
		t.update_lottery()
		time.sleep(60)







