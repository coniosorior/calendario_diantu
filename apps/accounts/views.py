from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
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


@login_required
@require_POST
def eliminar_cuenta(request):
    """
    Solo responde a POST para que la baja de cuenta nunca se dispare
    por accidente con un simple link (GET).
    """
    user = request.user
    user.is_active = False
    user.save()
    logout(request)
    messages.success(request, 'Tu cuenta fue eliminada. ¡Gracias por usar Diantu!')
    return redirect('login')
