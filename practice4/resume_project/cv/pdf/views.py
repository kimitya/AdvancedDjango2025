from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from .models import Profile
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse


def accept(request):
    if request.method == "POST":
        name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        phone = request.POST.get("phone", "")
        summary = request.POST.get("summary", "")
        degree = request.POST.get("degree", "")
        school = request.POST.get("school", "")
        university = request.POST.get("university", "")
        previous_work = request.POST.get("previous_work", "")
        skills = request.POST.get("skills", "")
        employed = request.POST.get("employed", "")
        picture = request.FILES.get("picture", "")
        if employed == 'on':
            employed = True
        else:
            employed = False
        profile = Profile(name=name, phone=phone, email=email, summary=summary, degree=degree, school=school, university=university, previous_work=previous_work, skills=skills, employed=employed, picture=picture)
        profile.save()
    return render(request, 'pdf/accept.html')

def resume(request, id):
    user_profile = Profile.objects.get(pk=id)
    template = get_template('pdf/resume.html')

    if user_profile.picture:
        picture_url = request.build_absolute_uri(user_profile.picture.url)
    else:
        picture_url = None

    html = template.render({'user_profile': user_profile, 'picture_url': picture_url})

    # html = template.render({'user_profile': user_profile})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resume_test.pdf"'

    pdf_file = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_file)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', content_type='text/plain')

    response.write(pdf_file.getvalue())
    return response
    
def list(request):
    profiles = Profile.objects.all()
    return render(request, 'pdf/list.html', {'profiles':profiles})


def share_email(request, id):
    profile = get_object_or_404(Profile, id=id)
    recipient_email = request.POST.get('email')

    if recipient_email:
        subject = f"{profile.name}'s CV"
        message = f"Check out {profile.name}'s CV at {request.build_absolute_uri(profile.picture.url)}"
        sender_email = settings.EMAIL_HOST_USER
        send_mail(subject, message, sender_email, [recipient_email])

        messages.success(request, "Resume shared successfully via email.")
    else:
        messages.error(request, "Please provide a valid email.")

    return redirect('list')

from django.shortcuts import render


from .forms import ContactForm


def contact(request):
    if request.method == "POST":

        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()
            # return redirect('success')
            name = form.cleaned_data['name']
            return redirect('success', name=name)
        else:
            form = ContactForm()
    return render(request, 'pdf/contact.html', {'form': form})

def success(request, name):
    return render(request, 'pdf/success.html', {'name': name})


