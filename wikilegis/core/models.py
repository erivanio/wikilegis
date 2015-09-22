# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _


def model_repr(cls, **kwargs):
    values = ['='.join([k, Truncator(v).chars(60)]) for (k, v) in kwargs.items()]
    return ''.join([cls, '{', values, '}'])


class TimestampedMixin(models.Model):
    created = models.DateTimeField(_('created'), editable=False, blank=True, auto_now_add=True)
    modified = models.DateTimeField(_('modified'), editable=False, blank=True, auto_now=True)

    class Meta:
        abstract = True


class Bill(TimestampedMixin):
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'))

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('bill')
        verbose_name_plural = _('bills')


class BillSegment(TimestampedMixin):
    bill = models.ForeignKey('core.Bill', related_name='segments', verbose_name=_('bill'))
    order = models.PositiveIntegerField(_('order'), default=0)
    content = models.TextField(_('content'))

    TYPE_CHOICES = (
        ('title', _('Title')),
        ('article', _('Article')),
    )
    type = models.CharField(_('type'), max_length=64, choices=TYPE_CHOICES)

    class Meta:
        ordering = ('order',)
        verbose_name = _('segment')
        verbose_name_plural = _('segments')

    def __unicode__(self):
        return '{bill}: {content}'.format(
            bill=self.bill, content=Truncator(self.content).chars(100))

    def is_editable(self):
        # Currently, only articles are editable.
        return self.type == 'article'


class CitizenAmendment(TimestampedMixin):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('author'))
    segment = models.ForeignKey('core.BillSegment', related_name='amendments', verbose_name=_('bill segment'))
    content = models.TextField(_('content'))

    class Meta:
        verbose_name = _('citizen amendment')
        verbose_name_plural = _('citizen amendments')

    def __unicode__(self):
        return model_repr(CitizenAmendment, author=self.author,
                          segment=self.segment, content=self.content)

    def original_content(self):
        return self.segment.content


class UserSegmentChoice(models.Model):
    """
    Each instance of this model indicates a choice of a user for a version of a bill segment.

    Users can choose either a submitted CitizenAmendment or they can choose the original segment text.

    Thus, there should be only one instance of this model for each pair of (user, segment).

    If there is none, the user hasn't voted for that particular segment yet.

    If there is one, but it's amendment if None, it means the user has voted for the original segment text.

    Otherwise, the user has voted for the selected amendment.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))
    segment = models.ForeignKey('core.BillSegment', related_name='choices',
                                verbose_name=_('bill segment'))
    amendment = models.ForeignKey('core.CitizenAmendment', related_name='choosings',
                                  null=True, blank=True, verbose_name=_('amendment'))

    class Meta:
        unique_together = ('user', 'segment')
