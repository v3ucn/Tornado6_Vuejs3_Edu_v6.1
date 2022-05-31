import time

class DelayQueue:

	def __init__(self,redis):

		self.key = "delayqueue"
		self.r = redis


	# 入队
	async def push(self,id,delay=0):

		print("延时队列入队，%s秒后执行查询%s订单的任务" %(delay,id))

		await self.r.zadd(self.key,{id:time.time()+delay})

	# 出队逻辑
	async def out(self):

		# 起始位置
		min_score = 0

		# 区间结束为止
		max_score = time.time()

		# 获取队列
		res = await self.r.zrangebyscore(self.key,min_score,max_score,count=1,offset=0,withscores=False)
        

		if res == None:

			print("暂无延时任务")

			return False

		if len(res) == 1:

			print("延时任务到期，返回执行任务的id%s" % res[0])

			return res[0]

		else:

			print("延时任务没有到时间")

			return False