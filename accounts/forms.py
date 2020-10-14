# from pycountry import countries
# from django.core import validators
# from django import forms
#
#
# class RegistrationForm(forms.Form):
#     name = forms.CharField(required=True, max_length=20)
#     middlename = forms.CharField(max_length=20)
#     lastname = forms.CharField(required=True, max_length=20)
#     # birthday = forms.DateField(required=True)
#     username = forms.CharField(required=True, min_length=3, max_length=20)
#     # email = forms.EmailField(required=True)
#     country = forms.CharField(required=True)
#     password = forms.CharField(required=True, min_length=8, max_length=20)
#     confirm_password = forms.CharField(required=True, min_length=3, max_length=20)
#     company = forms.CharField()
#
#     def clean(self):
#         cleaned_data = super(RegistrationForm, self).clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")
#         country = cleaned_data.get("country")
#
#         if password != confirm_password:
#             raise forms.ValidationError(
#                 "Passwords don't match"
#             )
#
#         if not countries.get(name=country):
#             raise forms.ValidationError(
#                 "Not a valid country"
#             )
#
#
# class LoginForm(forms.Form):
#     pass
