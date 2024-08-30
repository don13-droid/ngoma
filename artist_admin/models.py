from django.db import models
from muse.models import Song, User

class Sales(models.Model):
    choices = (('approved','Approved'),('pending','Pending'),('rejected','Rejected'))
    payment_choices = (('Ecocash USD','Ecocash USD'),('Ecocash ZIG','Ecocash ZIG'),('InnBucks','InnBucks'),
                       ('VISA/Mastercard','VISA/Mastercard'))
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_sales')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True ,related_name='user_sales')
    artist = models.ForeignKey(User, on_delete=models.CASCADE,related_name='sales')
    email = models.EmailField(default='sales@ingoma.com')
    phone = models.CharField(max_length=14, null=True)
    poll_url = models.CharField(max_length=100, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=1)
    status = models.CharField(choices=choices, max_length=50, default='approved')
    created = models.DateTimeField(auto_now_add=True)
    cleared = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'sale'
        verbose_name_plural = 'sales'
        ordering = ('created',)

    def __str__(self):
        return f'song bought {self.song} for {self.amount}'

    objects = models.Manager()

class News_and_Updates(models.Model):
    choices = (('draft','draft'),('published','published'))
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='news_and_updates/')
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=11, choices=choices)

    class Meta:
        verbose_name = 'Update'
        verbose_name_plural = 'Updates'

    def __str__(self):
        return self.title
class Song_Payments(models.Model):
    choices = (('success','success'),('failed', 'failed'))
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payments')
    amount = models.DecimalField(decimal_places=2, max_digits=11)
    payment_status = models.CharField(max_length=10, choices=choices)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Song Payment'
        verbose_name_plural = 'Song Payments'

    def __str__(self):
        return 'Song Payment Updated'

class Payouts(models.Model):
    ref_number = models.CharField(max_length=22)
    description = models.CharField(max_length=22)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payouts')
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_payouts')
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    notes = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = 'Payout'
        verbose_name_plural = 'Payouts'

    def __str__(self):
        return F'Payout "{self.ref_number}" created'