from django import forms

class PersonForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, label="Your name")
    age = forms.IntegerField(label="Your age")
    email = forms.EmailField(label="Your email")