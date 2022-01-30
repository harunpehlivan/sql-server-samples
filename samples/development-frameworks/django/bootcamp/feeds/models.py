from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from bootcamp.activities.models import Activity
from django.utils.html import escape
import bleach


class Feed(models.Model):
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    post = models.TextField(max_length=255)
    parent = models.ForeignKey('Feed', null=True, blank=True)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)

    class Meta:
        verbose_name = _('Feed')
        verbose_name_plural = _('Feeds')
        ordering = ('-date',)

    def __unicode__(self):
        return self.post

    @staticmethod
    def get_feeds(from_feed=None):
        return (
            Feed.objects.filter(parent=None, id__lte=from_feed)
            if from_feed is not None
            else Feed.objects.filter(parent=None)
        )

    @staticmethod
    def get_feeds_after(feed):
        return Feed.objects.filter(parent=None, id__gt=feed)

    def get_comments(self):
        return Feed.objects.filter(parent=self).order_by('date')

    def calculate_likes(self):
        likes = Activity.objects.filter(activity_type=Activity.LIKE,
                                        feed=self.pk).count()
        self.likes = likes
        self.save()
        return self.likes

    def get_likes(self):
        return Activity.objects.filter(activity_type=Activity.LIKE,
                                        feed=self.pk)

    def get_likers(self):
        likes = self.get_likes()
        return [like.user for like in likes]

    def calculate_comments(self):
        self.comments = Feed.objects.filter(parent=self).count()
        self.save()
        return self.comments

    def comment(self, user, post):
        feed_comment = Feed(user=user, post=post, parent=self)
        feed_comment.save()
        self.comments = Feed.objects.filter(parent=self).count()
        self.save()
        return feed_comment

    def linkfy_post(self):
        return bleach.linkify(escape(self.post))
