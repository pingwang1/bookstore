from db.base_model import BaseModel
from django.db import models
from hashlib import sha1

def get_hash(str):
	'''取一个字符串的hash值'''
	sh = sha1()
	sh.update(str.encode('utf-8'))
	return sh.hexdigest()


class PassportManager(models.Manager):
	def add_one_passport(self,username,password,email):
		'''添加一个账户信息'''
		passport = self.create(username=username,password=get_hash(password),email=email)
		#返回password
		return passport

	def get_one_passport(self,username,password):
		'''根据用户密码查找账户的信息'''
		try:
			passport = self.get(username=username,password=get_hash(password))
		except self.model.DoesNotExist:
			#账户不存在
			passport = None
		return passport


# Create your models here.
class Passport(BaseModel):
	'''用户模型类'''
	username = models.CharField(max_length=20,verbose_name='用户名称')
	password = models.CharField(max_length=40,verbose_name='用户密码')
	email = models.EmailField(verbose_name='用户邮箱')
	is_active = models.BooleanField(default=False,verbose_name='激活状态')

	#用户表的管管理器
	objects = PassportManager()

	class Meta:
		#指定数据库内的名称
		db_table = 's_user_account'
		verbose_name='用户'
		verbose_name_plural=verbose_name

	def __str__(self):
		return self.username