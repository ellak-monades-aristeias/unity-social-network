from django.db import models


class Role(models.Model):
	id = models.AutoField(primary_key=True)
	type = models.CharField(max_length=50L, null=True)
	desc = models.CharField(max_length=100L, null=True)

	#function which declare what is shown in admin panel
	def __unicode__(self):
		return self.type

