from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


# Create your models here.
class Post(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created = models.DateTimeField('Created Date', default=timezone.now)
    title = models.CharField('Title', max_length=200)
    content = models.TextField('Content')
    #  A slug is a short label for something, containing only letters, numbers, underscores
    slug = models.SlugField('Slug')

    def __str__(self):
        return '"%s" by %s' % (self.title, self.author)
