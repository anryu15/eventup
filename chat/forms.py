from .models import Event, CustomUser, CustomUser, Category, SubCategory
from django.contrib.auth.forms import UserCreationForm
from django import forms


class EventForm(forms.ModelForm):
    hashtags = forms.CharField(
        required=False,
        label='ハッシュタグ',
        help_text='ハッシュタグを入力してください（例：#初心者大歓迎#フットサル好きと繋がりたい#交流）。',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Event
        fields = [
            'category', 'subcategory', 'title', 'capacity', 'registration_deadline',
            'location', 'description', 'image', 'participation_method', 'event_date', 'hashtags'
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subcategory': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'participation_method': forms.Select(attrs={'class': 'form-control'}),
            'event_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }


class CustomUserRegistrationForm(UserCreationForm):
    account_id = forms.CharField(max_length=30)
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    subcategories = forms.ModelMultipleChoiceField(
        queryset=SubCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'account_id', 'password1', 'password2', 'bio', 'profile_picture', 'gender', 'age', 'preferred_region', 'categories', 'subcategories']

    def clean_account_id(self):
        account_id = self.cleaned_data['account_id']
        if not account_id.startswith('@'):
            account_id = '@' + account_id
        return account_id

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user.categories.set(self.cleaned_data['categories'])
            user.subcategories.set(self.cleaned_data['subcategories'])
        return user
