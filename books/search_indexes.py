from haystack import indexes
from books.models import Books

#指定对于某个类的某些数据建立索引，一般类名：模型类名＋Indnex
class BooksIndex(indexes.SearchIndex,indexes.Indexable):
	#指定根据表中的哪些字段建立索引：比如：商品名字，商品描述
	text = indexes.CharField(document=True,use_template=True)

	def get_model(self):
		print(Books)
		return Books

	def index_queryset(self, using=None):
		print(self.get_model().objects.all())
		return self.get_model().objects.all()
