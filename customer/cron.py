from django_cron import CronJobBase, Schedule
from customer.models import PasswordResetToken
from django.utils.timezone import now
from datetime import timedelta

class CleanExpiredTokensCronJob(CronJobBase):
    RUN_EVERY_MINS = 60  # Toutes les heures

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'customer.clean_expired_tokens' 

    def do(self):
        expiration_time = timedelta(hours=1)
        expired_tokens = PasswordResetToken.objects.filter(created_at__lt=now() - expiration_time)
        count = expired_tokens.count()
        expired_tokens.delete()
        print(f"{count} tokens expirés supprimés.")
