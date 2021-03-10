from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы',
                             help_text='Выберите группу')
    slug = models.SlugField(unique=True, verbose_name='Адрес группы')
    description = models.TextField(verbose_name='Описание группы')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст', blank=False,
                            help_text='Поле для текста записи')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts', verbose_name='Автор')
    group = models.ForeignKey(Group, blank=True, null=True,
                              on_delete=models.CASCADE, related_name='posts',
                              verbose_name='Группа',
                              help_text='Группа, в которую можно добавить '
                                        'запись')
    image = models.ImageField(upload_to='posts/', blank=True, null=True,
                              verbose_name='Изображение')

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField(verbose_name='Комментарий', blank=False)
    created = models.DateTimeField('Дата и время комментария',
                                   auto_now_add=True, db_index=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments', verbose_name='Пост')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments', verbose_name='Автор')

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')
