from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import ContactInfo

@method_decorator(csrf_exempt, name='dispatch')
class ContactInfoAPI(View):

    def get(self, request, *args, **kwargs):
        contact = ContactInfo.objects.first()  # Gets the first contact record
        if contact:
            return JsonResponse({
                # "user_email": contact.user_email,  # Uncomment if needed
                "telegram_username": contact.telegram_username
            })
        else:
            return JsonResponse({"error": "Contact info not found."}, status=404)
