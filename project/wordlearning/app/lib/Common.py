# coding: utf-8
from app.models import StatusHistory


class Common:
    @staticmethod
    def changeStatus(**kwargs):
        status_history = StatusHistory()
        t = None
        if 'word' in kwargs:
            t = kwargs['word']
            status_history.word = t
            status_history.type = 'word'
        else:
            t = kwargs['phrase']
            status_history.phrase = t
            status_history.type = 'phrase'
        if 'status' in kwargs:
            old_status = t.status
            t.status = kwargs['status']
            status_history.status = kwargs['status']
        else:
            old_status = 'None'
            status_history.status = t.status
        t.save()
        status_history.old_status = old_status
        status_history.save()
