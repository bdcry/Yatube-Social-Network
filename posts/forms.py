from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        labels = {
            'group': 'Сообщество',
            'text': 'Текст записи',
            'image': 'Изображение для поста',
        }
        help_text = {
            'group': 'Сообщество, в котором вы хотите опубликовать пост',
            'text': 'Содержимое вашего поста',
            'image': 'Только файлы изображений',
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = [
            'text'
        ]
