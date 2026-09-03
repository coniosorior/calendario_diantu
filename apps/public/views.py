from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm


def landing(request):
    """
    Página de inicio pública del sitio. No requiere sesión iniciada.
    """
    return render(request, 'public/landing.html')


def contact(request):
    """
    Formulario público de contacto. No requiere sesión iniciada.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu mensaje fue enviado. Gracias por escribirnos.')
            return redirect('public:contact')
        else:
            messages.error(request, 'Revisa los datos ingresados.')
    else:
        form = ContactForm()

    return render(request, 'public/contact.html', {'form': form})


def privacy(request):
    """
    Política de privacidad. No requiere sesión iniciada.
    """
    return render(request, 'public/privacy.html')
