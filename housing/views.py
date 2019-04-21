from django.shortcuts import render
from django.shortcuts import redirect
from django import forms
from django.db import models
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import HttpResponse
from housing.models import renter, lease, maintenance, payment,reservation, amenity, admin, room, post, reply
from housing.forms import renterForm
import datetime
from django.db import connection
import numpy as np

from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Create your views here.

# locate request to index.html
def user_index(request):
    #str = '922'
    #str1 = lease.objects.get(room=str).rent_fee
    pass
    return render(request, 'user_index.html')
    #return  render(request, 'index.html')

def login(request):
    # if request.session.get('is_login', None):
    #     return redirect("/user_index/")
    if request.method == "POST":
        login_form = renterForm(request.POST)
        message = "Please check the entered information！"
        if login_form.is_valid():
            r_email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            try:
                renter_info = renter.objects.get(email=r_email)
                if renter_info.renter_pwd == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = renter_info.renter_id
                    request.session['user_name'] = renter_info.lastname
                    return redirect('/profile/')
                else:
                    message = "Incorrect password！"
            except:
                message = "User does not exist！"
        return render(request, 'login.html', locals())

    login_form = renterForm()
    return render(request, 'login.html', locals())

def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/user_index/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/user_index/")




# def admin_index(request):
#     #str = '922'
#     #str1 = lease.objects.get(room=str).rent_fee
#     pass
#     return render(request, 'index.html')
#     #return  render(request, 'index.html')

def login_admin(request):
    if request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == "POST":
        login_form = renterForm(request.POST)
        message = "Please check the entered information！"
        if login_form.is_valid():
            a_email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            try:
                admin_info = admin.objects.get(admin_username = a_email)
                if admin_info.admin_pwd == password:
                    request.session['is_login'] = True
                    request.session['admin_id'] = admin_info.admin_id
                    request.session['admin_username'] = admin_info.admin_username
                    return redirect('/index/')
                else:
                    message = "Incorrect password！"
            except:
                message = "User does not exist！"
        return render(request, 'login_admin.html', locals())

    login_form = renterForm()
    return render(request, 'login_admin.html', locals())

def logout_admin(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/index/")

def profile(request):
    if request.session.get('is_login', None):
        renter_id = request.session['user_id']
        renter_info = renter.objects.raw("SELECT * FROM housing_renter WHERE renter_id = %s", [renter_id])
        for r in renter_info:
            firstname = r.firstname
            lastname = r.lastname
            email = r.email
            phone = r.phone
            gender = r.gender
            pwd = r.renter_pwd

    #modify info part
    if request.POST:
        first = request.POST['firstname']
        last = request.POST['lastname']
        mail = request.POST['email']
        mobile = request.POST['phone']
        sex = request.POST['gender']
        cursor = connection.cursor()
        cursor.execute("UPDATE housing_renter SET `firstname` = %s, `lastname` = %s,`email` = %s,  `phone` = %s, `gender` = %s WHERE `renter_id` = %s",
                [first,last, mail, mobile, sex, renter_id])
        return redirect("/profile/")
    #reset password part
    if request.GET:
        pwd = request.GET['newpwd1']
        r_info = renter.objects.get(renter_id=renter_id)
        r_info.renter_pwd = pwd
        r_info.save()

    #lease info part
    leases = lease.objects.filter(renter=renter_id)
    return render(request, "profile.html", {'lease':leases, 'email':email,'password':pwd,'firstname':firstname, 'lastname':lastname, 'phone':phone, 'gender': gender})




def maintain(request):
    if request.session.get('is_login', None):
        renter_id = request.session['user_id']
    # maintenance history part
    maintain_info = maintenance.objects.filter(renter=renter_id)
    return render(request, 'maintenance.html', {"maintain_info": maintain_info})


def maintenance_add(request):
    if request.session.get('is_login', None):
        renter_id = request.session['user_id']
        renter_info = renter.objects.raw("SELECT * FROM housing_renter WHERE renter_id = %s", [renter_id])
        for r in renter_info:
            email = r.email
            phone = r.phone
        roomno = lease.objects.get(renter=renter_id).room_id
        roominfo = room.objects.get(room_number=roomno)
    # add maintenance part
    if request.POST:
        id = renter.objects.get(renter_id=renter_id)
        date = timezone.now()
        location = request.POST['location']
        category = request.POST['category']
        description = request.POST['description']
        new_maintenance = maintenance(renter=id,room = roominfo, apply_date = date, maintenance_location = location, maintenance_category = category, maintenance_describe = description)
        new_maintenance.save()
        return redirect('/maintenance/')
    return render(request, 'maintenance_add.html',{ 'email':email,'phone':phone, 'roomno': roomno})

def maintenance_edit(request):
    if request.session.get('is_login', None):
        renter_id = request.session['user_id']
        renter_info = renter.objects.raw("SELECT * FROM housing_renter WHERE renter_id = %s", [renter_id])
        for r in renter_info:
            email = r.email
            phone = r.phone
        room = lease.objects.get(renter=renter_id).room
    m_id = request.GET.get("id")
    maintain = maintenance.objects.raw("SELECT * FROM housing_maintenance WHERE maintenance_id = %s", [m_id])
    for m in maintain:
        description = m.maintenance_describe

    # update maintenance part

    if request.POST:
        mid = request.GET.get("mid")
        date = timezone.now()
        loc = request.POST['location']
        cat = request.POST['category']
        des = request.POST['description']
        #m_info=maintenance.objects.get(maintenance_id = m_id)
        #maintenance.objects.filter(maintenance_id="1").update(apply_date = date, maintenance_location=loc, maintenance_category=cat, maintenance_describe = des )
        #m_info.apply_date = date
        #m_info.maintenance_location = loc
        #m_info.maintenance_category = cat
        #m_info.maintenance_describe = des
        #m_info.save()

        cursor = connection.cursor()
        cursor.execute("UPDATE housing_maintenance SET `apply_date` = %s, `maintenance_location` = %s,`maintenance_category` = %s,  `maintenance_describe` = %s WHERE `maintenance_id` = %s", [date,loc,cat,des,mid])
        #if(result):
        return redirect('/maintenance/')
       # else:
            #return redirect('/maintenance_edit/')

    return render(request, 'maintenance_update.html',{ 'email':email,'phone':phone, 'roomno': room, "description":description, "mid":m_id})

def maintenance_delete(request):
    m_id = request.GET.get("id")
    cursor = connection.cursor()
    cursor.execute("delete from housing_maintenance where `maintenance_id`=%s",[m_id])
    return redirect("/maintenance/")


def payments(request):
    if request.session.get('is_login', None):
        renter_id = request.session['user_id']
    #UT=utility.objects.all()
    pay_info=payment.objects.raw("SELECT * FROM housing_payment WHERE housing_payment.renter_id=%s AND housing_payment.pay_record=1 "
                                 "ORDER BY housing_payment.id DESC ",[renter_id])
    balance_info=payment.objects.raw("SELECT * FROM housing_payment WHERE housing_payment.renter_id=%s ORDER BY housing_payment.id DESC ",[renter_id])
    balance={}
    for i in balance_info:
        balance[i.id]=0.0
        for j in balance_info:
            if i.id>=j.id and j.pay_record == 0:
                balance[i.id] = round(balance[i.id]-j.fee, 2)
            elif i.id>=j.id and j.pay_record == 1:
                balance[i.id] = round(balance[i.id] + j.fee,2)
            else:
                continue
    cursor = connection.cursor()
    cursor.execute('select balance from housing_renter where housing_renter.renter_id=%s',[renter_id])
    current_balance = cursor.fetchone()[0]

    return render(request,'payment.html' ,{'pi':pay_info,'bi':balance_info,'balance':balance,'current_balance':current_balance})
"""


def make_pay(request):
  #  if request.method=='POST':
    if request.session.get('is_login', None):
      renter_id = request.session['user_id']

    amount=request.POST['amount']
    pay_type=request.POST['type']
    rent_info=renter.objects.raw("SELECT * FROM housing_lease WHERE housing_lease.renter_id=%s",[renter_id])
    for i in rent_info:
        room_id=i.room_id
    time_now = timezone.now()
    pay_info=payment(renter_id=renter_id, room_id=room_id, pay_record=1,payment_type=pay_type,pay_date=time_now,fee=amount)
    pay_info.save()



    balance_info = payment.objects.raw("SELECT * FROM housing_payment WHERE housing_payment.renter_id=%s ", [renter_id])
    balance=0
    for j in balance_info:
        if j.pay_record == 0:
            balance = balance - j.fee
        elif j.pay_record == 1:
            balance = balance + j.fee
    cursor = connection.cursor()
    cursor.execute('update housing_renter set balance= %s where housing_renter.renter_id=%s',[balance,renter_id])

    return redirect("/payment/")
"""

def make_pay(request):
  #  if request.method=='POST':
    if request.session.get('is_login', None):
      renter_id = request.session['user_id']

    amount=request.POST['amount']
    pay_type=request.POST['type']
    rent_info=renter.objects.raw("SELECT * FROM housing_lease WHERE housing_lease.renter_id=%s",[renter_id])
    room_id=0
    for i in rent_info:
        room_id=i.room_id
    time_now = timezone.now()
    pay_record=1
    cursor=connection.cursor()
    cursor.execute("INSERT INTO housing_payment "
                   "(renter_id, room_id, pay_record, payment_type, pay_date, fee)"
                   "VALUES ( %s, %s, %s, %s, %s, %s)",[renter_id, room_id, pay_record, pay_type, time_now, amount])

    #pay_info=payment(renter_id=48, room_id=room_id, pay_record=pay_record,payment_type=pay_type,pay_date=time_now,fee=amount)
    #pay_info.save()



    balance_info = payment.objects.raw("SELECT * FROM housing_payment WHERE housing_payment.renter_id=%s ", [renter_id])
    balance=0
    for j in balance_info:
        if j.pay_record == 0:
            balance = balance - j.fee
        elif j.pay_record == 1:
            balance = balance + j.fee
    balance = float(balance)

    cursor.execute('update housing_renter set balance= %s where housing_renter.renter_id=%s',[balance,renter_id])

    return redirect("/payment/")

def reservations(request):
    if request.session.get('is_login', None):
        renter_id = request.session['user_id']
    reserve_info = reservation.objects.raw("SELECT * FROM housing_reservation JOIN housing_amenity"
                                           " ON housing_amenity.amenity_id=housing_reservation.Amenity_id WHERE housing_reservation.Renter_id= %s ",[renter_id])
    return render(request,'reservation.html' ,{'amenity_info':reserve_info})


def reservation_add(request):
    if request.session.get('is_login', None):
        renter_id = request.session['user_id']
        renter_info = renter.objects.raw("SELECT * FROM housing_renter WHERE renter_id = %s", [renter_id])
        for r in renter_info:
            email = r.email
            phone = r.phone
        amenity_info = amenity.objects.raw("SELECT * FROM housing_amenity")

    time_list=["00:00","01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]
    booked_time=[]

    # add reservation part
    if request.POST:
        id = renter.objects.get(renter_id=renter_id)
        room = request.POST['room']
        start_date = request.POST['date']
        reserve_info = reservation.objects.raw("SELECT * FROM housing_reservation WHERE Amenity_id=%s and start_date=%s", [room, start_date])
        for r in reserve_info:
            booked_time.append(r.start_time)
        t_list = np.setdiff1d(time_list, booked_time)
        return render(request,"reservation_add.html", {'start_d':start_date,'email':email,'phone':phone, "amenity_info":amenity_info,"time_list":t_list, "room":room, "start_date":start_date})

    if request.GET:
        id = renter.objects.get(renter_id=renter_id)
        start_time = request.GET['time']
        a_room=request.GET['a_room']
        amenity_room =  amenity.objects.get(amenity_id=a_room)
        start_day = request.GET['date']
        reserve_date = timezone.now()
        new_reservation = reservation( Renter=id, Amenity=amenity_room, start_date=start_day,start_time=start_time, reserve_date=reserve_date)
        new_reservation.save()
        return redirect('/reservation/')
    return render(request,'reservation_add.html',{'email':email,'phone':phone, "amenity_info":amenity_info })

def check_date(request):
    if request.POST:
        startd = request.POST['date']
    reserve_info = reservation.objects.raw("SELECT * FROM housing_reservation WHERE start_date=%s",[])
    return render(request,'reservation_add.html')


def reservation_edit(request):
    if request.session.get('is_login', None):
        renter_id = request.session['user_id']
        renter_info = renter.objects.raw("SELECT * FROM housing_renter WHERE renter_id = %s", [renter_id])
        for r in renter_info:
            email = r.email
            phone = r.phone
        amenity_info = amenity.objects.raw("SELECT * FROM housing_amenity")

    time_list=["00:00","01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]
    reserve_info = reservation.objects.raw("SELECT * FROM housing_reservation")
    for r in reserve_info:
        re = r.email
        phone = r.phone

    if request.POST:
        mid = request.GET.get("mid")
        date = timezone.now()
        loc = request.POST['location']
        cat = request.POST['category']
        des = request.POST['description']

        cursor = connection.cursor()
        cursor.execute("UPDATE housing_maintenance SET `apply_date` = %s, `maintenance_location` = %s,`maintenance_category` = %s,  `maintenance_describe` = %s WHERE `maintenance_id` = %s", [date,loc,cat,des,mid])
    return render(request,'reservation_edit.html',{'email':email,'phone':phone,"time_list":time_list, "amenity_info":amenity_info })

def reservation_delete(request):
    r_id = request.GET.get("id")
    cursor = connection.cursor()
    cursor.execute("delete from housing_reservation where `reservation_id`=%s",[r_id])
    return redirect("/reservation/")

def login_admin(request):

    #if request.session.get('is_login', None):
     #   return redirect("/index/")
    if request.method == "POST":
        message = "Please check the entered information！"
        r_admin_username = request.POST['username']
        password = request.POST['pwd_admin']
        try:
                admin_info = admin.objects.get(admin_username=r_admin_username)
                if admin_info.admin_pwd == password:
                    request.session['is_login'] = True
                    request.session['admin_id'] = admin_info.admin_id
                    #request.session['user_name'] = renter_info.lastname
                    return redirect('/index/')
                else:
                    message = "Incorrect password！"
        except:
                message = "User does not exist！"
        return render(request, 'login_admin.html', locals())
    return render(request, 'login_admin.html', locals())



def maintenance_admin(request):
    maintenance_info =maintenance.objects.raw("SELECT * FROM housing_maintenance")
    return render(request, 'maintenance_admin.html', {'maintenance_info':maintenance_info})

def reservation_admin(request):
    reservation_info =reservation.objects.raw("SELECT * FROM housing_reservation")
    return render(request, 'reservation_admin.html', {'reservation_info': reservation_info})

def amenity_admin(request):
    amenity_info =amenity.objects.raw("SELECT * FROM housing_amenity")
    return render(request, 'amenity_admin.html', {'amenity_info': amenity_info})

def amenity_admin_delete(request):
    amenity_id=request.GET.get("am_id")
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM `housing`.`housing_amenity` WHERE (`amenity_id` = %s)",
        [amenity_id])
    amenity_info =amenity.objects.raw("SELECT * FROM housing_amenity")
    return render(request, 'amenity_admin.html', {'amenity_info': amenity_info})

def amenity_admin_update(request):
    amenity_id = request.GET.get("am_id")
    amenity_list=amenity.objects.get(amenity_id=amenity_id)
    return render(request, 'amenity_admin_update.html', {'amenity_info': amenity_list })

def amenity_admin_update2(request):
    amenity_id = request.GET.get("amenity_id")
    amenity_type = request.GET.get("amenity_type")
    amenity_capacity = request.GET.get("amenity_capacity")
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE housing_amenity SET amenity_type = %s,amenity_capacity = %s WHERE amenity_id= %s",
        [amenity_type, amenity_capacity,amenity_id])
    amenity_info = amenity.objects.raw("SELECT * FROM housing_amenity")
    return render(request, 'amenity_admin.html', {'amenity_info': amenity_info})


def payment_admin(request):
    payment_info =payment.objects.raw("SELECT * FROM housing_payment")
    for obj in payment_info:
        if(obj.pay_record==True):
            obj.pay_record="+"
        else:
            obj.pay_record = "-"
    return render(request, 'payment_admin.html', {'payment_info': payment_info})

def payment_admin_add(request):
    fee = request.GET.get("fee")
    pay_date = request.GET.get("pay_date")
    payment_type = request.GET.get("payment_type")
    pay_record = request.GET.get("pay_record")
    renter_id = request.GET.get("renter_id")
    room_id = request.GET.get("room_id")
    balance = renter.objects.get(renter_id=renter_id).balance
    if (pay_record=="Charge"):
        sum = float(balance) - float(fee)
        pay_record=0
    else:
        sum = float(balance) + float(fee)
        pay_record = 1
    cursor = connection.cursor()
    cursor.execute('INSERT INTO `housing`.`housing_payment` ( `fee`, `pay_date`, `payment_type`, `pay_record`, `renter_id`, `room_id`) VALUES ( %s, %s, %s, %s, %s, %s)',[fee, pay_date, payment_type, pay_record,renter_id,room_id])
    cursor.execute("UPDATE housing_renter SET balance = %s WHERE renter_id= %s",
        [sum, renter_id])
    return HttpResponse("<script type='text/javascript'> alert('Success');location.href='/payment_admin/'</script>")

def maintenance_changestatus(request):
    mid = request.GET.get("mid")
    operation = request.GET.get("operation")
    if(operation=="Confirm"):
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE housing_maintenance SET maintenance_status = %s WHERE maintenance_id= %s",
            ["Confirm",mid])
    if (operation == "Complete"):
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE housing_maintenance SET maintenance_status = %s WHERE maintenance_id= %s",
            ["Complete", mid])
    maintenance_info = maintenance.objects.raw("SELECT * FROM housing_maintenance")
    return render(request, 'maintenance_admin.html', {'maintenance_info': maintenance_info})


def housing_room(request):
    room_info = room.objects.raw("SELECT * FROM housing_room")
    return render(request, 'housing_room.html', {'room_info' :room_info})

def housing_renter(request):
    renter_info = renter.objects.raw("SELECT * FROM housing_renter")
    return render(request, 'housing_renter.html', {'renter_info' :renter_info})

def housing_renter_delete(request):
    renter_id=request.GET.get("renter_id")
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM `housing`.`housing_renter` WHERE (`renter_id` = %s)",
        [renter_id])
    renter_info =renter.objects.raw("SELECT * FROM housing_renter")
    return render(request, 'housing_renter.html', {'renter_info': renter_info})

def forgot_password(request):
    pass
    return render(request, 'forgot-password.html')
# def update_room(request):
#     room_status = request.GET['room']
#
# def update_renter(request):
#     renter_phone = request.GET['renter_phone']
#     print(renter_phone)

def renter_admin_update(request):
    renter_id = request.GET.get("renter_id")
    renter_list=renter.objects.filter(renter_id = renter_id)
    for i in renter_list:
        renter_idi = i.renter_id
        renter_em = i.email
        renter_fn = i.firstname
        renter_ln = i.lastname
        renter_g = i.gender
        renter_ph = i.phone
        renter_cp = i.carplate
        renter_bl = i.balance

    return render(request, 'renter_admin_update.html', {'renter_id': renter_idi, 'renter_email': renter_em, 'renter_firstname':renter_fn,'renter_lastname':renter_ln,'renter_gender': renter_g, 'renter_phone': renter_ph, 'renter_carplate':renter_cp,'renter_balance': renter_bl})

def renter_admin_update2(request):
    renter_id = request.GET["renter_id"]
    renter_email = request.GET["renter_email"]
    renter_firstname = request.GET["renter_firstname"]
    renter_lastname = request.GET["renter_lastname"]
    renter_phone = request.GET["renter_phone"]
    renter_carplate = request.GET["renter_carplate"]
    renter_balance = request.GET["renter_balance"]

    cursor = connection.cursor()
    cursor.execute(
        "UPDATE housing_renter SET email = %s, firstname = %s, lastname = %s, phone = %s, carplate = %s, balance = %s WHERE renter_id= %s",
        [renter_email, renter_firstname, renter_lastname, renter_phone, renter_carplate, renter_balance, renter_id])
    renter_info = renter.objects.raw("SELECT * FROM housing_renter")
    return render(request, 'housing_renter.html', {'renter_info': renter_info})

def room_admin_update(request):
    room_number = request.GET.get("room_number")
    room_list=room.objects.filter(room_number = room_number)
    for r in room_list:
        room_no = r.room_number
        room_type = r.room_type
        room_description = r.room_description
        room_status = r.room_status
    return render(request, 'room_admin_update.html', {'room_number': room_no, 'room_type':room_type, 'room_description':room_description,'room_status':room_status})

def room_admin_update2(request):
    room_number = request.GET["room_number"]
    room_type = request.GET["room_type"]
    room_description = request.GET["room_description"]
    room_status = request.GET["room_status"]

    cursor = connection.cursor()
    cursor.execute(
        "UPDATE housing_room SET room_type = %s, room_description = %s, room_status = %s WHERE room_number= %s",
        [room_type, room_description, room_status, room_number])
    room_info = room.objects.raw("SELECT * FROM housing_room")
    return render(request, 'housing_room.html', {'room_info': room_info})

def housing_renter_addform(request):
    return render(request, 'housing_addrenter.html')
def housing_renter_add(request):
    renter_id = request.GET.get("renter_id")
    renter_email = request.GET.get("renter_email")
    renter_firstname = request.GET.get("renter_firstname")
    renter_lastname = request.GET.get("renter_lastname")
    renter_phone = request.GET.get("renter_phone")
    renter_pwd = request.GET.get("renter_pwd")
    renter_carplate = request.GET.get("renter_carplate")
    renter_balance = request.GET.get("renter_balance")
    renter_birthday = request.GET.get("renter_birthday")
    renter_gender = request.GET.get("renter_gender")
    renter_country = request.GET.get("renter_country")

    # lease_id = request.GET.get("lease_id")
    room_number = request.GET.get("room_number")
    rent_fee = request.GET.get("rent_fee")
    movein_date = request.GET.get("movein_date")
    moveout_date = request.GET.get("moveout_date")


    cursor = connection.cursor()
    cursor.execute('INSERT INTO `housing`.`housing_renter` ( `renter_id`, `email`, `firstname`, `lastname`, `gender`, `renter_pwd`, `phone`, `carplate`, `balance`, `birthday`,  `country`) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',[renter_id, renter_email, renter_firstname, renter_lastname, renter_gender, renter_pwd, renter_phone, renter_carplate,renter_balance, renter_birthday, renter_country])
    cursor.execute('INSERT INTO `housing`.`housing_lease` ( `rent_fee`, `movein_date`, `moveout_date`, `renter_id`,`room_id`) VALUES ( %s, %s, %s, %s, %s)',[rent_fee, movein_date, moveout_date, renter_id, room_number])
    cursor.execute(
        "UPDATE housing_room SET `room_status` = %s WHERE `room_number` = %s",
        ["1", room_number])

    return HttpResponse("<script type='text/javascript'> alert('Success');location.href='/housing_renter/'</script>")



def forum(request):
    #post_list = post.objects.raw("SELECT * FROM housing_post JOIN housing_renter"
    #                                       " ON housing_post.renter_id=housing_renter.renter_id ORDER BY housing_post.post_date DESC")
    if request.POST:
        search=request.POST["search"]
        search='%'+search+'%'
        cursor = connection.cursor()
        cursor.execute("SELECT p.post_id, p.post_subject, p.post_date,p.post_tag,r.firstname, r.lastname, temp.num"
                       " FROM housing_post as p, housing_renter as r,"
                       "(SELECT R1.post_id , count(R2.reply_id) as num FROM "
                       "housing_post AS R1 "
                       "LEFT JOIN housing_reply as R2 "
                       "on R1.post_id=R2.post_id"
                       " group by R1.post_id ) AS temp"
                       " WHERE p.renter_id= r.renter_id"
                       " AND p.post_id = temp.post_id"
                       " AND ((p.post_subject like %s) "
                       "OR (r.firstname like %s)"
                        "OR (r.lastname like %s)"
                        "OR (p.post_tag like %s))"
                       " order by p.post_date desc",[search,search,search,search])
        posts_list = cursor.fetchall()
        connection.close()
        return render(request, 'forum.html', {'post_list': posts_list})

    order=request.GET.get("order")
    if order =='popular':
        cursor = connection.cursor()
        cursor.execute("SELECT p.post_id, p.post_subject, p.post_date,p.post_tag,r.firstname, r.lastname, temp.num"
                       " FROM housing_post as p, housing_renter as r,"
                       "(SELECT R1.post_id , count(R2.reply_id) as num FROM "
                       "housing_post AS R1 "
                       "LEFT JOIN housing_reply as R2 "
                       "on R1.post_id=R2.post_id"
                       " group by R1.post_id ) AS temp"
                       " WHERE p.renter_id= r.renter_id"
                       " AND p.post_id = temp.post_id"
                       " order by temp.num desc")
        posts_list = cursor.fetchall()
        connection.close()
        return render(request, 'forum.html', {'post_list': posts_list})
    else:
        cursor = connection.cursor()
        cursor.execute("SELECT p.post_id, p.post_subject, p.post_date,p.post_tag,r.firstname, r.lastname, temp.num"
                       " FROM housing_post as p, housing_renter as r,"
                       "(SELECT R1.post_id , count(R2.reply_id) as num FROM "
                       "housing_post AS R1 "
                       "LEFT JOIN housing_reply as R2 "
                       "on R1.post_id=R2.post_id"
                       " group by R1.post_id ) AS temp"
                       " WHERE p.renter_id= r.renter_id"
                       " AND p.post_id = temp.post_id"
                       " order by p.post_date desc")
        posts_list = cursor.fetchall()
        connection.close()
        return render(request, 'forum.html', {'post_list': posts_list})

def post_add(request):
    if request.method =='POST':
        renter_id = request.session['user_id']
        id = renter.objects.get(renter_id=renter_id)

        image = request.FILES.get('img')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        tag = request.POST.get('tag')

        date = timezone.now()
        new_post = post(renter=id,post_subject=subject, post_message=message, post_img=image, post_date= date, post_tag=tag )
        new_post.save()
        return redirect("/forum/")
    return render(request, 'post_add.html')

def post_view(request):

    p_id = request.GET.get("id")
    post_detail = post.objects.raw("SELECT * FROM housing_post JOIN housing_renter"
                                     " ON housing_post.renter_id=housing_renter.renter_id WHERE post_id = %s", [p_id])

    reply_detail = reply.objects.raw("SELECT * FROM housing_reply JOIN housing_renter"
                                     " ON housing_reply.renter_id=housing_renter.renter_id WHERE post_id = %s", [p_id])
    cursor = connection.cursor()
    cursor.execute("SELECT count(R2.reply_id) as num FROM "
                   "housing_post AS R1 "
                   "LEFT JOIN housing_reply as R2 "
                   "on R1.post_id=R2.post_id"
                   " WHERE R1.post_id= %s " , [p_id])

    count = cursor.fetchall()
    connection.close()
    return render(request, 'post_view.html', {"post_detail": post_detail,"reply_detail": reply_detail, "count":count})

def post_reply(request):
    p_id = request.GET.get("p_id")
    post_detail = post.objects.raw("SELECT * FROM housing_post JOIN housing_renter"
                                   " ON housing_post.renter_id=housing_renter.renter_id WHERE post_id = %s", [p_id])

    return render(request, 'post_reply.html', {"detail": post_detail})

def reply_add(request):
    if request.method =='POST':
        renter_id = request.session['user_id']
        id = renter.objects.get(renter_id=renter_id)

        image = request.FILES.get('img')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        p_id = request.POST.get('postid')

        date = timezone.now()
        new_reply = reply(renter=id,reply_subject=subject, reply_message=message, reply_img=image, reply_date= date, post_id=p_id )
        new_reply.save()
        return redirect("/post_view/?id="+p_id)
    return render(request, 'post_reply.html')

def reply_reply(request):
    r_id = request.GET.get("r_id")
    reply_detail = reply.objects.raw("SELECT * FROM housing_reply, housing_renter, housing_post"
                                   " WHERE housing_reply.renter_id=housing_renter.renter_id "
                                     "AND housing_post.post_id=housing_reply.post_id"
                                     " AND reply_id = %s", [r_id])

    return render(request, 'reply_reply.html', {"detail": reply_detail})

def reply_reply_add(request):
    if request.method =='POST':
        renter_id = request.session['user_id']
        id = renter.objects.get(renter_id=renter_id)

        image = request.FILES.get('img')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        p_id = request.POST.get('postid')
        parent_reply=request.POST.get('parentid')
        date = timezone.now()
        new_reply = reply(renter=id,reply_subject=subject, reply_message=message, parent_reply=parent_reply,reply_img=image, reply_date= date, post_id=p_id )
        new_reply.save()
        return redirect("/post_view/?id="+p_id)
    return render(request, 'post_reply.html')

def mypost(request):
    renter_id = request.session['user_id']
    if request.POST:
        search = request.POST["search"]
        search = '%' + search + '%'
        cursor = connection.cursor()
        cursor.execute("SELECT p.post_id, p.post_subject, p.post_date,p.post_tag,r.firstname, r.lastname, temp.num"
                       " FROM housing_post as p, housing_renter as r,"
                       "(SELECT R1.post_id , count(R2.reply_id) as num FROM "
                       "housing_post AS R1 "
                       "LEFT JOIN housing_reply as R2 "
                       "on R1.post_id=R2.post_id"
                       " group by R1.post_id ) AS temp"
                       " WHERE p.renter_id= r.renter_id"
                       " AND r.renter_id = %s "
                       " AND p.post_id = temp.post_id"
                       " AND ((p.post_subject like %s) "
                       "OR (p.post_tag like %s))"
                       " order by p.post_date desc", [renter_id,search,  search])
        posts_list = cursor.fetchall()
        connection.close()
        return render(request, 'mypost.html', {'post_list': posts_list})

    order = request.GET.get("order")
    if order == 'popular':
        cursor = connection.cursor()
        cursor.execute("SELECT p.post_id, p.post_subject, p.post_date,p.post_tag,r.firstname, r.lastname, temp.num"
                       " FROM housing_post as p, housing_renter as r,"
                       "(SELECT R1.post_id , count(R2.reply_id) as num FROM "
                       "housing_post AS R1 "
                       "LEFT JOIN housing_reply as R2 "
                       "on R1.post_id=R2.post_id"
                       " group by R1.post_id ) AS temp"
                       " WHERE p.renter_id= r.renter_id"
                        " AND r.renter_id = %s "
                       " AND p.post_id = temp.post_id"
                       " order by temp.num desc",[renter_id])
        posts_list = cursor.fetchall()
        connection.close()
        return render(request, 'mypost.html', {'post_list': posts_list})
    else:
        cursor = connection.cursor()
        cursor.execute("SELECT p.post_id, p.post_subject, p.post_date,p.post_tag,r.firstname, r.lastname, temp.num"
                       " FROM housing_post as p, housing_renter as r,"
                       "(SELECT R1.post_id , count(R2.reply_id) as num FROM "
                       "housing_post AS R1 "
                       "LEFT JOIN housing_reply as R2 "
                       "on R1.post_id=R2.post_id"
                       " group by R1.post_id ) AS temp"
                       " WHERE p.renter_id= r.renter_id"
                       " AND r.renter_id = %s "
                       " AND p.post_id = temp.post_id"
                       " order by p.post_date desc",[renter_id])
        posts_list = cursor.fetchall()
        connection.close()
        return render(request, 'mypost.html', {'post_list': posts_list})
    return render(request,'mypost.html')

def post_delete(request):
    p_id = request.GET.get("id")
    cursor = connection.cursor()
    cursor.execute("delete from housing_post where `post_id`=%s",[p_id])
    return redirect("/mypost/")

def myreply(request):
    renter_id = request.session['user_id']
    if request.POST:
        search = request.POST["search"]
        search = '%' + search + '%'
        cursor = connection.cursor()
        cursor.execute("SELECT re.post_id, re.reply_id,re.reply_subject, p.post_tag, re.reply_date, r.firstname, r.lastname FROM housing_post as p, housing_renter as r, housing_reply as re"
                       " WHERE re.renter_id= r.renter_id"
                        " AND re.post_id = p.post_id "
                       " AND re.renter_id = %s "
                       " AND ((re.reply_subject like %s) "
                       "OR (p.post_tag like %s))"
                       " order by re.reply_date desc", [renter_id,search,  search])
        reply_list = cursor.fetchall()
        connection.close()
        return render(request, 'myreply.html', {'reply_list': reply_list})


    cursor = connection.cursor()
    cursor.execute("SELECT re.post_id, re.reply_id,re.reply_subject, p.post_tag, re.reply_date, r.firstname, r.lastname"
                   " FROM housing_post as p, housing_renter as r, housing_reply as re"
                       " WHERE re.renter_id= r.renter_id"
                        " AND re.post_id = p.post_id "
                       " AND r.renter_id = %s "
                       " order by re.reply_date desc", [renter_id])
    reply_list = cursor.fetchall()
    connection.close()
    return render(request, 'myreply.html', {'reply_list': reply_list})

def reply_delete(request):
    r_id = request.GET.get("id")
    cursor = connection.cursor()
    cursor.execute("delete from housing_reply where `reply_id`=%s",[r_id])
    connection.close()
    return redirect("/myreply/")

def index(request):
    cursor = connection.cursor()
    cursor.execute("SELECT country, COUNT(*) AS num FROM housing_renter GROUP BY country")
    country_list = cursor.fetchall()
    connection.close()
    cursor = connection.cursor()
    cursor.execute("SELECT gender, COUNT(*) AS num FROM housing_renter GROUP BY gender")
    gender = cursor.fetchall()
    connection.close()
    cursor = connection.cursor()
    cursor.execute(" SELECT CASE WHEN(age >= 10 AND age <= 20) THEN '10-20' "
                                "WHEN(age >= 21 AND age <= 30) THEN '21-30' "
                                "ELSE '30+' END 'eag_layer', count(*) num FROM "
                                "(SELECT timestampdiff(YEAR, birthday, CURDATE()) as age FROM housing_renter ) AS temp "
                                "GROUP BY CASE "
                                "WHEN(age >= 10 AND age <= 20) THEN '10-20' "
                                "WHEN(age >= 21 AND age <= 30) THEN '21-30' "
                                "ELSE '30+' END ORDER BY 1;")
    age_group = cursor.fetchall()
    connection.close()
    cursor = connection.cursor()
    cursor.execute(" SELECT room_type, count(*) as num from housing_room "
                   " GROUP BY room_type")
    room = cursor.fetchall()
    connection.close()
    cursor = connection.cursor()
    cursor.execute("SELECT r.room_type, temp1.age_group, count(*) as num FROM housing_lease as l, housing_room as r,"
                   "(SELECT temp.renter_id, CASE WHEN(age >= 10 AND age <= 20) THEN '10-20' WHEN(age >= 21 AND age <= 30) THEN '21-30' "
                   "ELSE '30+' END 'age_group' FROM (SELECT renter_id, timestampdiff(YEAR, birthday, CURDATE()) as age FROM housing_renter ) AS temp ) as temp1"
                   " WHERE l.renter_id = temp1.renter_id "
                   "AND l.room_id= r.room_number"
                   " GROUP BY temp1.age_group, r.room_type")
    lease=cursor.fetchall()
    connection.close()

    list_20=[0,0,0]
    list_21_30=[0,0,0]
    list_30=[0,0,0]
    for l in lease:
        if(l[1])=="10-20":
            if(l[0])=='2b2b':
                list_20[0]=l[2]
            if (l[0]) == '3b3b':
                list_20[1] = l[2]
            if (l[0]) == '4b4b':
                list_20[2] = l[2]
        if (l[1]) == "21-30":
            if (l[0]) == '2b2b':
                list_21_30[0] = l[2]
            if (l[0]) == '3b3b':
                list_21_30[1] = l[2]
            if (l[0]) == '4b4b':
                list_21_30[2] = l[2]
        if (l[1]) == "30+":
            if (l[0]) == '2b2b':
                list_30[0] = l[2]
            if (l[0]) == '3b3b':
                list_30[1] = l[2]
            if (l[0]) == '4b4b':
                list_30[3] = l[2]
    cursor = connection.cursor()
    cursor.execute(
        "SELECT maintenance_category,count(*) as coun FROM housing_maintenance GROUP BY maintenance_category")
    category_chart = cursor.fetchall()
    connection.close()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT maintenance_location,count(*) as coun FROM housing_maintenance GROUP BY maintenance_location")
    location_chart = cursor.fetchall()
    connection.close()
    cursor = connection.cursor()
    cursor.execute(
        "select r.room_type,month(pay_date) as mon,avg(fee) as avgfee from housing_payment as p join housing_room as r on p.room_id=r.room_number where payment_type='Utility' and pay_record = 0 group by month(pay_date),r.room_number")
    payment_chart = cursor.fetchall()
    connection.close()
    list2b = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    list3b = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    list4b = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for pa in payment_chart:
        if (pa[0] == '2b2b'):
            list2b[pa[1] - 1] = pa[2]
        if (pa[0] == '3b3b'):
            list3b[pa[1] - 1] = pa[2]
        if (pa[0] == '4b4b'):
            list4b[pa[1] - 1] = pa[2]

    cursor = connection.cursor()
    cursor.execute("select amenity_type, count(*) as num from housing_amenity group by amenity_type")
    amenity_count = cursor.fetchall()
    connection.close()
    a_id = amenity.objects.raw("SELECT * FROM housing_amenity ")

    cursor = connection.cursor()
    cursor.execute("select a.amenity_type, count(*) from housing_reservation as r "
                   "left join housing_amenity as a "
                   "on a.amenity_id = r.Amenity_id "
                   "group by a.amenity_type;")
    amenity_reserve=cursor.fetchall()
    connection.close()

    cursor = connection.cursor()
    cursor.execute(
        "select dayname(start_date) as we,start_time,count(*) as coun from housing_reservation as r group by dayname(start_date),start_time;")
    reservation_chart = cursor.fetchall()
    connection.close()
    hours = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00',
             '07:00', '08:00', '09:00', '10:00', '11:00',
             '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
             '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']
    days = ['Saturday', 'Friday', 'Thursday',
            'Wednesday', 'Tuesday', 'Monday', 'Sunday']
    listall = []
    list = [0, 0, 0]

    for d in range(len(days)):
        for h in range(len(hours)):
            for reser in reservation_chart:
                if (reser[1] == hours[h]):
                    if (reser[0] == days[d]):
                        list[0] = d
                        list[1] = h
                        list[2] = reser[2]
            listall.append(list)
            list = [0, 0, 0]
    if request.POST:
        a_name = request.POST["amenityid"]
        if a_name == "total":
            return render(request, "index.html", {"country_list": country_list, "gender":gender,"age_group":age_group, "room":room, "list_20":list_20, "list_21_30":list_21_30, "list_30":list_30,'category_chart': category_chart, 'location_chart': location_chart, 'list2b': list2b,
                   'list3b': list3b, 'list4b': list4b, 'listall': listall, 'a_name':a_name,"amenity_reserve":amenity_reserve,"a_id":a_id, "amenity_count":amenity_count})
        else:
            cursor = connection.cursor()
            cursor.execute(
                "select dayname(start_date) as we,start_time,count(*) as coun from housing_reservation as r, housing_amenity as a "
                "where a.amenity_id=r.Amenity_id and a.amenity_id = %s group by dayname(start_date),start_time;",[a_name])
            reservation_chart = cursor.fetchall()
            connection.close()
            listall = []
            list = [0, 0, 0]

            for d in range(len(days)):
                for h in range(len(hours)):
                    for reser in reservation_chart:
                        if (reser[1] == hours[h]):
                            if (reser[0] == days[d]):
                                list[0] = d
                                list[1] = h
                                list[2] = reser[2]
                    listall.append(list)
                    list = [0, 0, 0]
            return render(request, "index.html",
                          {"country_list": country_list, "gender": gender, "age_group": age_group, "room": room,
                           "list_20": list_20, "list_21_30": list_21_30, "list_30": list_30,
                           'category_chart': category_chart, 'location_chart': location_chart, 'list2b': list2b,
                           'list3b': list3b, 'list4b': list4b, 'listall': listall, 'a_name':a_name,"amenity_reserve":amenity_reserve,"a_id":a_id, "amenity_count":amenity_count})
    return render(request, "index.html", {"country_list": country_list, "gender":gender,"age_group":age_group, "room":room, "list_20":list_20, "list_21_30":list_21_30, "list_30":list_30,'category_chart': category_chart, 'location_chart': location_chart, 'list2b': list2b,
                   'list3b': list3b, 'list4b': list4b, 'listall': listall, "amenity_reserve":amenity_reserve,"a_id":a_id, "amenity_count":amenity_count})

