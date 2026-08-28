# Diantu — Testing

> Documento de referencia para desarrollo humano y agentic coding (IA). Define los casos de prueba de cada app de Diantu, siguiendo el patrón `TestCase` + `setUp()` de Django. Los tests se escriben en paralelo al desarrollo de cada funcionalidad, no al final del proyecto.

---

## Por qué testing en Diantu

Más allá de la buena práctica general, hay una razón específica para Diantu: el aislamiento de datos por usuario (`owner=request.user` en cada consulta) es una regla de seguridad crítica que es fácil de olvidar en una vista nueva. Un test que verifica "el usuario A no puede ver bloques del usuario B" atrapa ese error antes de que llegue a producción, cosa que probar manualmente con el admin (que ve todo) no logra — ver `diantu-admin.md`.

---

## Tests de `apps/categories/tests/`

> Diantu usa el patrón de carpeta `tests/` (con `__init__.py` y un archivo por tipo de test: `test_models.py`, `test_views.py`, etc.) en todas las apps del proyecto, en vez de un único archivo `tests.py` — más escalable a medida que cada app acumula más casos de prueba.

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Category
```

Va en `test_models.py`:

```python
class CategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ana', password='claveSegura123')

    def test_str_representation(self):
        cat = Category.objects.create(
            owner=self.user, name='Trabajo', color='#006EE9', icon='ti-briefcase'
        )
        self.assertEqual(str(cat), 'Trabajo (ana)')

    def test_categorias_predeterminadas_se_crean_al_registrar(self):
        """
        Verifica que la señal post_save (ver diantu-autenticacion.md)
        creó las 8 categorías predeterminadas automáticamente.
        """
        categorias = Category.objects.filter(owner=self.user)
        self.assertEqual(categorias.count(), 8)

    def test_categoria_otros_es_default(self):
        otros = Category.objects.get(owner=self.user, name='Otros')
        self.assertTrue(otros.is_default)

    def test_no_se_puede_eliminar_categoria_otros(self):
        otros = Category.objects.get(owner=self.user, name='Otros')
        with self.assertRaises(Exception):
            otros.delete()

    def test_nombre_unico_por_usuario(self):
        with self.assertRaises(Exception):
            Category.objects.create(
                owner=self.user, name='Otros', color='#000000', icon='ti-bulb'
            )

    def test_mismo_nombre_permitido_entre_usuarios_distintos(self):
        """Dos usuarios distintos SÍ pueden tener una categoría con el mismo nombre."""
        otro_user = User.objects.create_user(username='beto', password='claveSegura123')
        # 'Trabajo' ya existe para self.user (predeterminada) y para otro_user también
        cat_ana = Category.objects.get(owner=self.user, name='Trabajo/Estudio')
        cat_beto = Category.objects.get(owner=otro_user, name='Trabajo/Estudio')
        self.assertNotEqual(cat_ana.pk, cat_beto.pk)
```

Va en `test_views.py`:

```python
class CategoryListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='ana', password='claveSegura123')
        # other_user no se usa directo en los tests, pero su existencia (con sus
        # propias 8 categorías vía la señal) es lo que hace significativo el
        # test de aislamiento de abajo: sin otro usuario con categorías propias
        # en la base de datos, ese test pasaría aunque el filtro por owner fallara.
        self.other_user = User.objects.create_user(username='beto', password='claveSegura123')
        self.client.login(username='ana', password='claveSegura123')

    def test_lista_requiere_login(self):
        self.client.logout()
        response = self.client.get(reverse('categories:list'))
        self.assertEqual(response.status_code, 302)  # redirige a login

    def test_lista_status_200(self):
        response = self.client.get(reverse('categories:list'))
        self.assertEqual(response.status_code, 200)

    def test_lista_solo_muestra_categorias_propias(self):
        """
        CRÍTICO: un usuario nunca debe ver categorías de otro usuario,
        aunque tengan el mismo nombre (ej: ambos tienen 'Otros').
        """
        response = self.client.get(reverse('categories:list'))
        categorias_mostradas = response.context['categories']
        for cat in categorias_mostradas:
            self.assertEqual(cat.owner, self.user)
```

---

## Tests de `apps/planner/tests/`

> Diantu usa el patrón de carpeta `tests/` (con `__init__.py` y un archivo por tipo de test: `test_models.py`, `test_views.py`, etc.) en todas las apps del proyecto, en vez de un único archivo `tests.py` — más escalable a medida que cada app acumula más casos de prueba.

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from apps.categories.models import Category
from .models import Block, InboxItem
```

Va en `test_models.py`:

```python
class BlockModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ana', password='claveSegura123')
        self.category = Category.objects.get(owner=self.user, name='Trabajo/Estudio')

    def test_str_representation(self):
        block = Block.objects.create(
            owner=self.user, category=self.category, title='Reunión',
            date=date(2026, 7, 10), start_time='09:00', end_time='10:00',
        )
        self.assertIn('Reunión', str(block))

    def test_duration_minutes(self):
        block = Block.objects.create(
            owner=self.user, category=self.category, title='Estudio',
            date=date(2026, 7, 10), start_time='09:00', end_time='11:30',
        )
        self.assertEqual(block.duration_minutes, 150)

    def test_completed_default_false(self):
        block = Block.objects.create(
            owner=self.user, category=self.category, title='Tarea',
            date=date(2026, 7, 10), start_time='09:00', end_time='10:00',
        )
        self.assertFalse(block.completed)

    def test_clean_rechaza_hora_fin_anterior_a_inicio(self):
        block = Block(
            owner=self.user, category=self.category, title='Inválido',
            date=date(2026, 7, 10), start_time='10:00', end_time='09:00',
        )
        with self.assertRaises(Exception):
            block.full_clean()
```

Va en `test_forms.py`:

```python
class BlockFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ana', password='claveSegura123')
        self.category = Category.objects.get(owner=self.user, name='Trabajo/Estudio')
        Block.objects.create(
            owner=self.user, category=self.category, title='Existente',
            date=date(2026, 7, 10), start_time='09:00', end_time='11:00',
        )

    def test_rechaza_solapamiento_de_horario(self):
        from .forms import BlockForm
        form = BlockForm(data={
            'title': 'Nuevo bloque',
            'date': date(2026, 7, 10),
            'start_time': '10:00',   # se solapa con el bloque existente (09:00-11:00)
            'end_time': '12:00',
            'category': self.category.pk,
            'has_alarm': False,
            'note': '',
        }, owner=self.user)
        self.assertFalse(form.is_valid())

    def test_acepta_horario_sin_solapamiento(self):
        from .forms import BlockForm
        form = BlockForm(data={
            'title': 'Nuevo bloque',
            'date': date(2026, 7, 10),
            'start_time': '11:00',   # justo después del existente, sin solaparse
            'end_time': '12:00',
            'category': self.category.pk,
            'has_alarm': False,
            'note': '',
        }, owner=self.user)
        self.assertTrue(form.is_valid())
```

Va en `test_views.py`:

```python
class DayViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='ana', password='claveSegura123')
        self.other_user = User.objects.create_user(username='beto', password='claveSegura123')
        self.category = Category.objects.get(owner=self.user, name='Trabajo/Estudio')
        self.client.login(username='ana', password='claveSegura123')

    def test_day_view_requiere_login(self):
        self.client.logout()
        response = self.client.get(reverse('planner:day'))
        self.assertEqual(response.status_code, 302)

    def test_day_view_status_200(self):
        response = self.client.get(reverse('planner:day'))
        self.assertEqual(response.status_code, 200)

    def test_day_view_solo_muestra_bloques_propios(self):
        """
        CRÍTICO: verifica el aislamiento de datos por usuario descrito
        en diantu-vistas-urls.md — un usuario nunca ve bloques ajenos.
        """
        cat_beto = Category.objects.get(owner=self.other_user, name='Trabajo/Estudio')
        Block.objects.create(
            owner=self.user, category=self.category, title='Bloque de Ana',
            date=date.today(), start_time='09:00', end_time='10:00',
        )
        Block.objects.create(
            owner=self.other_user, category=cat_beto, title='Bloque de Beto',
            date=date.today(), start_time='09:00', end_time='10:00',
        )

        response = self.client.get(reverse('planner:day'))
        titulos = [b.title for b in response.context['blocks']]
        self.assertIn('Bloque de Ana', titulos)
        self.assertNotIn('Bloque de Beto', titulos)

    def test_block_update_404_si_es_de_otro_usuario(self):
        cat_beto = Category.objects.get(owner=self.other_user, name='Trabajo/Estudio')
        block_ajeno = Block.objects.create(
            owner=self.other_user, category=cat_beto, title='Bloque de Beto',
            date=date.today(), start_time='09:00', end_time='10:00',
        )
        response = self.client.get(reverse('planner:block_update', kwargs={'pk': block_ajeno.pk}))
        self.assertEqual(response.status_code, 404)

    def test_toggle_complete_cambia_estado(self):
        block = Block.objects.create(
            owner=self.user, category=self.category, title='Tarea',
            date=date.today(), start_time='09:00', end_time='10:00',
        )
        self.assertFalse(block.completed)
        self.client.post(reverse('planner:block_toggle_complete', kwargs={'pk': block.pk}))
        block.refresh_from_db()
        self.assertTrue(block.completed)
```

Va en `test_views.py`:

```python
class InboxItemTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='ana', password='claveSegura123')
        self.category = Category.objects.get(owner=self.user, name='Trabajo/Estudio')
        self.client.login(username='ana', password='claveSegura123')

    def test_mover_a_timeline_crea_block_y_borra_inbox_item(self):
        item = InboxItem.objects.create(owner=self.user, title='Llamar al médico')

        response = self.client.post(
            reverse('planner:inbox_move', kwargs={'pk': item.pk}),
            data={
                'title': 'Llamar al médico',
                'date': date.today(),
                'start_time': '15:00',
                'end_time': '15:30',
                'category': self.category.pk,
                'has_alarm': False,
                'note': '',
            }
        )

        self.assertFalse(InboxItem.objects.filter(pk=item.pk).exists())
        self.assertTrue(Block.objects.filter(owner=self.user, title='Llamar al médico').exists())
```

---

## Tests de `apps/accounts/tests/`

> Diantu usa el patrón de carpeta `tests/` (con `__init__.py` y un archivo por tipo de test: `test_models.py`, `test_views.py`, etc.) en todas las apps del proyecto, en vez de un único archivo `tests.py` — más escalable a medida que cada app acumula más casos de prueba.

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.categories.models import Category
```

Va en `test_views.py`:

```python
class RegistroTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registro_status_200_get(self):
        response = self.client.get(reverse('accounts:registro'))
        self.assertEqual(response.status_code, 200)

    def test_registro_crea_usuario(self):
        response = self.client.post(reverse('accounts:registro'), data={
            'username': 'nuevo_usuario',
            'email': 'nuevo@ejemplo.com',
            'password1': 'claveSegura123',
            'password2': 'claveSegura123',
        })
        self.assertTrue(User.objects.filter(username='nuevo_usuario').exists())

    def test_registro_dispara_creacion_de_categorias(self):
        self.client.post(reverse('accounts:registro'), data={
            'username': 'nuevo_usuario',
            'email': 'nuevo@ejemplo.com',
            'password1': 'claveSegura123',
            'password2': 'claveSegura123',
        })
        user = User.objects.get(username='nuevo_usuario')
        self.assertEqual(Category.objects.filter(owner=user).count(), 8)

    def test_registro_password_no_coincidentes_falla(self):
        response = self.client.post(reverse('accounts:registro'), data={
            'username': 'otro_usuario',
            'email': 'otro@ejemplo.com',
            'password1': 'claveSegura123',
            'password2': 'claveDiferente456',
        })
        self.assertFalse(User.objects.filter(username='otro_usuario').exists())
```

Va en `test_models.py`:

```python
from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Profile


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ana', password='claveSegura123')

    def test_profile_se_crea_al_registrar_usuario(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_valores_por_defecto(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.time_format, '24h')
        self.assertEqual(profile.first_day_of_week, 'mon')
        self.assertEqual(profile.timezone, 'America/Santiago')

    def test_str_representation(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(str(profile), 'Perfil de ana')

    def test_relacion_one_to_one_con_user(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(self.user.profile, profile)
        self.assertEqual(profile.user, self.user)
```

Va en `test_views.py`:

```python
class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='ana', password='claveSegura123')

    def test_login_correcto_redirige_a_day(self):
        response = self.client.post(reverse('login'), data={
            'username': 'ana',
            'password': 'claveSegura123',
        })
        self.assertRedirects(response, reverse('planner:day'))

    def test_login_incorrecto_no_autentica(self):
        response = self.client.post(reverse('login'), data={
            'username': 'ana',
            'password': 'claveIncorrecta',
        })
        self.assertFalse(response.wsgi_request.user.is_authenticated)
```

---

## Ejecutar los tests

```bash
# Todos los tests del proyecto
python manage.py test

# Solo una app
python manage.py test apps.planner

# Un caso específico
python manage.py test apps.planner.tests.test_views.DayViewTest.test_day_view_solo_muestra_bloques_propios

# Con detalle de cada test ejecutado
python manage.py test -v 2
```

---

## Checklist mínimo de testing antes de dar por cerrada una funcionalidad

Para cada vista nueva que toque datos de un modelo con `owner`, verificar que exista al menos:

- [ ] Test de que la vista requiere `@login_required` (redirige si no hay sesión)
- [ ] Test de que un usuario **no puede ver** datos de otro usuario en esa vista
- [ ] Test de que un usuario **no puede editar/eliminar** datos de otro usuario (404 esperado)
- [ ] Test del caso "feliz" (happy path): la operación funciona como se espera con datos válidos
- [ ] Test de al menos un caso de validación fallida (datos inválidos → error esperado, no excepción sin manejar)

Este checklist aplica en particular a `Block`, `Category` e `InboxItem`, que son los tres modelos con datos privados por usuario en Diantu.

---

*Documento parte de la serie de arquitectura de Diantu. Ver también: `diantu-modelos.md`, `diantu-vistas-urls.md`, `diantu-autenticacion.md`.*
