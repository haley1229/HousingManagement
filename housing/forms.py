from django import forms


class renterForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", max_length=30, widget=forms.PasswordInput(attrs={'class': 'form-control'}))

