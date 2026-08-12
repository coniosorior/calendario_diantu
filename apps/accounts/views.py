from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistroForm


def registro(request):
    """
    FBV porque además de crear el User, dispara la creación de las
    categorías predeterminadas mediante la señal post_save (ver
    diantu-autenticacion.md). No es un CRUD estándar de Django.
    """
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Cuenta creada. ¡Bienvenido a Diantu, {user.username}!')
            return redirect('login')
        else:
            messages.error(request, 'Revisa los datos ingresados.')
    else:
        form = RegistroForm()

    return render(request, 'accounts/register.html', {'form': form})
