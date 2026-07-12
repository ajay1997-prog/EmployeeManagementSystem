from django import forms
from django.forms.widgets import DateInput, TextInput

from .models import *


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput)
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError(
                        "The given email is already registered")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email',
                  'gender',  'password', 'profile_pic', 'address']


class EmployeeForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Employee
        fields = CustomUserForm.Meta.fields + [
            'division',
            'department',
            'employee_code',
            'designation',
            'branch',
            'joining_date',
            'date_of_birth',
            'father_name',
            'mother_name',
            'native_place',
            'phone_number',
            'emergency_contact',
            'bank_name',
            'account_number',
            'ifsc_code',
            'pf_number',
        ]

        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class ManagerForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(ManagerForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Manager
        fields = CustomUserForm.Meta.fields + \
            ['division']


class DivisionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(DivisionForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name']
        model = Division


class DepartmentForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Department
        fields = ['name', 'division']


class LeaveReportManagerForm(forms.ModelForm):

    LEAVE_TYPES = [
        ('Casual Leave', 'Casual Leave'),
        ('Sick Leave', 'Sick Leave'),
        ('Earned Leave', 'Earned Leave'),
        ('Emergency Leave', 'Emergency Leave'),
        ('Work From Home', 'Work From Home'),
        ('Marriage Leave', 'Marriage Leave'),
        ('Comp Off', 'Comp Off'),
        ('Half Day', 'Half Day'),
        ('Leave Without Pay', 'Leave Without Pay'),
        ('Other', 'Other'),
    ]

    leave_type = forms.ChoiceField(
        choices=LEAVE_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    from_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    to_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = LeaveReportManager
        fields = ['leave_type', 'from_date', 'to_date', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control'})
        }

    def save(self, commit=True):
        obj = super().save(commit=False)

        obj.date = f"{self.cleaned_data['from_date']} to {self.cleaned_data['to_date']}"

        obj.message = (
            f"Leave Type: {self.cleaned_data['leave_type']}\n\n"
            f"{self.cleaned_data['message']}"
        )

        if commit:
            obj.save()

        return obj


class FeedbackManagerForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackManagerForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackManager
        fields = ['feedback']


class LeaveReportEmployeeForm(forms.ModelForm):

    LEAVE_TYPES = [
        ('Casual Leave', 'Casual Leave'),
        ('Sick Leave', 'Sick Leave'),
        ('Earned Leave', 'Earned Leave'),
        ('Emergency Leave', 'Emergency Leave'),
        ('Work From Home', 'Work From Home'),
        ('Marriage Leave', 'Marriage Leave'),
        ('Comp Off', 'Comp Off'),
        ('Half Day', 'Half Day'),
        ('Leave Without Pay', 'Leave Without Pay'),
        ('Other', 'Other'),
    ]

    leave_type = forms.ChoiceField(
        choices=LEAVE_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    from_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    to_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = LeaveReportEmployee
        fields = ['leave_type', 'from_date', 'to_date', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control'})
        }

    def save(self, commit=True):
        obj = super().save(commit=False)

        # Save both dates into the existing "date" field
        obj.date = f"{self.cleaned_data['from_date']} to {self.cleaned_data['to_date']}"

        # Save leave type together with the message
        obj.message = (
            f"Leave Type: {self.cleaned_data['leave_type']}\n\n"
            f"{self.cleaned_data['message']}"
        )

        if commit:
            obj.save()

        return obj

class FeedbackEmployeeForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackEmployeeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackEmployee
        fields = ['feedback']


class EmployeeEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(EmployeeEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Employee
        fields = CustomUserForm.Meta.fields


class ManagerEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(ManagerEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Manager
        fields = CustomUserForm.Meta.fields


class EditSalaryForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(EditSalaryForm, self).__init__(*args, **kwargs)

    class Meta:
        model = EmployeeSalary
        fields = ['department', 'employee', 'base', 'ctc']
