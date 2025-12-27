from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget

from apps.users.models import User
from apps.vpn.models import Subscription, SubscriptionMode


class SubscriptionManagementForm(forms.Form):
    mode = forms.ChoiceField(
        choices=SubscriptionMode.choices,
        label="Режим начисления",
        widget=forms.Select(attrs={"class": "ui-select"}),
    )

    target_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Пользователь",
        required=False,
        widget=ForeignKeyRawIdWidget(
            Subscription._meta.get_field("user").remote_field,
            admin.site,
            attrs={
                "class": "vForeignKeyRawIdAdminField ui-input",
                "style": "width: auto; display: inline-block;",
            },
        ),
    )

    days = forms.IntegerField(
        label="Дней начисления",
        min_value=1,
        initial=7,
        widget=forms.NumberInput(attrs={"class": "ui-input", "placeholder": "7"}),
    )

    send_notification = forms.BooleanField(
        label="Отправить уведомление",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "ui-toggle"}),
    )

    notification_text = forms.CharField(
        label="Текст уведомления",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "class": "ui-textarea",
                "placeholder": "Уважаемый пользователь, мы дарим вам...",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        mode = cleaned_data.get("mode")
        target_user = cleaned_data.get("target_user")
        send_notification = cleaned_data.get("send_notification")
        notification_text = cleaned_data.get("notification_text")

        if mode == SubscriptionMode.USER and not target_user:
            self.add_error(
                "target_user",
                'Для режима "Конкретный пользователь" необходимо выбрать пользователя.',
            )

        if send_notification and not notification_text:
            self.add_error(
                "notification_text", "Текст уведомления не может быть пустым."
            )

        return cleaned_data
