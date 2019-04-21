from django.db import models

# Create your models here.
class renter(models.Model):
    renter_id=models.IntegerField(primary_key=True)
    email = models.EmailField(max_length=255, unique= True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, null= True)
    renter_pwd = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)
    carplate = models.CharField(max_length=20, null= True)
    balance = models.FloatField(default=0.0)
    birthday = models.DateField(max_length=50,null=True)
    country = models.CharField(max_length=50,null=True)

class room(models.Model):
    room_number = models.CharField(primary_key=True,max_length=10)
    room_type = models.CharField(max_length=5)
    room_description = models.CharField(null = True, max_length=500)
    room_status = models.IntegerField(default=0)

class lease(models.Model):
    lease_id= models.AutoField(primary_key=True)
    renter = models.ForeignKey(renter, on_delete = models.CASCADE)
    room = models.ForeignKey(room, on_delete = models.CASCADE)
    rent_fee = models.FloatField(default=0.0)
    movein_date = models.DateField(null = True)
    moveout_date = models.DateField(null = True)

class amenity(models.Model):
    #change to charfield
    amenity_id = models.CharField(primary_key=True,max_length=50)
    #amenity_name = models.CharField(max_length=30)
    amenity_type = models.CharField(max_length=30)
    amenity_capacity = models.CharField(null=True, max_length=30)

class maintenance(models.Model):
    maintenance_id= models.AutoField(primary_key=True)
    renter = models.ForeignKey(renter, on_delete = models.CASCADE)
    room = models.ForeignKey(room, on_delete = models.CASCADE)
    apply_date = models.DateField(null = True)
    maintenance_location = models.CharField(max_length=50, null=True)
    maintenance_category = models.CharField(max_length=50,null=True)
    maintenance_describe = models.CharField(max_length=500)
    maintenance_status = models.CharField(max_length=50, default="Submitted")

class reservation(models.Model):
    reservation_id= models.AutoField(primary_key=True)
    Renter = models.ForeignKey(renter, on_delete = models.CASCADE)
    Amenity = models.ForeignKey(amenity, on_delete = models.CASCADE)
    start_date = models.DateField(null=True)
    start_time = models.CharField(max_length=50,null=True)
    reserve_date = models.DateField(null = True)

class admin(models.Model):
    admin_id = models.IntegerField(primary_key=True)
    admin_username = models.CharField(max_length=20)
    admin_pwd = models.CharField(max_length=30)

class payment(models.Model):
    id= models.AutoField(primary_key=True)
    renter = models.ForeignKey(renter, on_delete = models.CASCADE)
    room = models.ForeignKey(room, on_delete = models.CASCADE)
    fee = models.FloatField(default=0.0)
    pay_date = models.DateField(null = True)
    payment_type = models.CharField(max_length=50)
    pay_record = models.BooleanField(default=True)

class post(models.Model):
    post_id=models.AutoField(primary_key=True)
    renter=models.ForeignKey(renter, on_delete=models.CASCADE)
    post_subject=models.CharField(max_length=100)
    post_message=models.CharField(max_length=500)
    post_img=models.ImageField(upload_to='image/')
    post_date=models.DateTimeField(null=True)
    post_tag=models.CharField(max_length=50, null=True)

class reply(models.Model):
    reply_id=models.AutoField(primary_key=True)
    renter = models.ForeignKey(renter, on_delete=models.CASCADE)
    post =models.ForeignKey(post, on_delete=models.CASCADE)
    reply_subject=models.CharField(max_length=100)
    reply_message=models.CharField(max_length=500)
    reply_img=models.ImageField(upload_to='image/')
    reply_date=models.DateTimeField(null=True)
    parent_reply=models.IntegerField(null=True)