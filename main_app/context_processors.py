from .models import Employee, Manager, NotificationEmployee, NotificationManager


def notification_count(request):
    count = 0

    if request.user.is_authenticated:
        try:
            if request.user.user_type == "3":
                employee = Employee.objects.get(admin=request.user)
                count = NotificationEmployee.objects.filter(
                    employee=employee,
                    is_read=False
                ).count()

            elif request.user.user_type == "2":
                manager = Manager.objects.get(admin=request.user)
                count = NotificationManager.objects.filter(
                    manager=manager,
                    is_read=False
                ).count()

        except Exception:
            pass

    return {
        "notification_count": count
    }