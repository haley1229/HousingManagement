from django.db import models

# Create your models here.
class renter(models.Model):
    renter_id=models.IntegerField(primary_key=True)
    email = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, null= True)
    renter_pwd = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)
    carplate = models.CharField(max_length=20, null= True)
    blance = models.FloatField(default=0.0)

class room(models.Model):
    room_number = models.CharField(primary_key=True,max_length=10)
    room_type = models.CharField(max_length=5)
    room_description = models.CharField(null = True, max_length=500)
    room_status = models.IntegerField(default=0)

class rent(models.Model):
    renter = models.ForeignKey(renter, on_delete = models.CASCADE)
    room = models.ForeignKey(room, on_delete = models.CASCADE)
    rent_fee = models.FloatField(default=0.0)
    utility_fee = models.FloatField(default=0.0)
    movein_date = models.DateField(null = True)
    moveout_date = models.DateField(null = True)

class amenity(models.Model):
    amenity_id = models.IntegerField(primary_key=True)
    amenity_type = models.CharField(max_length=30)
    amenity_capacity = models.CharField(null=True, max_length=30)
    amenity_status = models.IntegerField(default=0)

class reservation(models.Model):
    Renter = models.ForeignKey(renter, on_delete = models.CASCADE)
    Amenity = models.ForeignKey(amenity, on_delete = models.CASCADE)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

class admin(models.Model):
    admin_id = models.IntegerField(primary_key=True)
    admin_username = models.CharField(max_length=20)
    admin_pwd = models.CharField(max_length=30)

