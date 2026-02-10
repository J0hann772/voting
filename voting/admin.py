from django.contrib import admin

from voting.models import Voting, Choice, Vote, Report


admin.site.register(Voting)
admin.site.register(Choice)
admin.site.register(Vote)
admin.site.register(Report)