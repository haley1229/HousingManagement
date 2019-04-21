"""HousingManagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from housing import views

from django.conf import settings
from django.conf.urls.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),

    path('user_index/', views.user_index),
    path('login/', views.login),
    path('logout/', views.logout),
    path('profile/', views.profile),
    path('maintenance/', views.maintain),
    path('maintenance_add/', views.maintenance_add),
    path('maintenance_edit/', views.maintenance_edit),
    path('maintenance_delete/', views.maintenance_delete),
    path('check_date/', views.check_date),

    path('payment/', views.payments),
    path('make_pay/', views.make_pay),

    path('reservation/', views.reservations),
    path('reservation_add/',views.reservation_add),
    path('reservation_edit/', views.reservation_edit),
    path('reservation_delete/',views.reservation_delete),




    path('login_admin/',views.login_admin),
    path('logout_admin/', views.logout_admin),
    path('maintenance_admin/', views.maintenance_admin),
    path('amenity_admin/', views.amenity_admin),
    path('reservation_admin/', views.reservation_admin),

    path('payment_admin/', views.payment_admin),
    path('maintenance_changestatus/', views.maintenance_changestatus),
    path('amenity_admin_update/', views.amenity_admin_update),
    path('amenity_admin_delete/', views.amenity_admin_delete),
    path('amenity_admin_update2/', views.amenity_admin_update2),
    path('payment_admin_add/', views.payment_admin_add),

    path('housing_room/', views.housing_room),
    path('housing_renter/', views.housing_renter),
    path('forgot-password/', views.forgot_password),
    # path('update_room/', views.update_room),
    # path('update_renter/', views.update_renter)
    path('renter_admin_update2/', views.renter_admin_update2),
    path('renter_admin_update/', views.renter_admin_update),
    path('room_admin_update2/', views.room_admin_update2),
    path('room_admin_update/', views.room_admin_update),
    path('housing_renter_addform/', views.housing_renter_addform),
    path('housing_renter_add/', views.housing_renter_add),
    path('housing_renter_delete/', views.housing_renter_delete),



    path('forum/', views.forum),
    path('post_add/', views.post_add),
    re_path(r'^media/(.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('post_view/', views.post_view),
    path('post_reply/', views.post_reply),
    path('reply_add/', views.reply_add),
    path('reply_reply/', views.reply_reply),
    path('reply_reply_add/', views.reply_reply_add),
    path('mypost/', views.mypost),
    path('post_delete/', views.post_delete),
    path('myreply/', views.myreply),
    path('reply_delete/', views.reply_delete),



]

