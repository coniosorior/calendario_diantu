from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
# TODO: descomentar cuando exista apps.planner
# from apps.planner.models import Block
from .models import Category
from .forms import CategoryForm


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'categories/list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user)


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/form.html'
    success_url = reverse_lazy('categories:list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Categoría creada.')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/form.html'
    success_url = reverse_lazy('categories:list')

    def get_queryset(self):
        # Filtro por owner: un usuario no puede editar categorías ajenas
        return Category.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada.')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'categories/confirm_delete.html'
    success_url = reverse_lazy('categories:list')

    def get_queryset(self):
        # No se puede eliminar la categoría "Otros" (is_default=True)
        return Category.objects.filter(owner=self.request.user, is_default=False)

    def form_valid(self, form):
        """
        Antes de eliminar, reasigna todos los Block de esta categoría
        a la categoría "Otros" del mismo usuario. Este es el patrón
        manual que reemplaza on_delete=SET_DEFAULT (ver diantu-modelos.md).
        """
        category = self.get_object()
        fallback = Category.objects.get(owner=self.request.user, is_default=True)
        # TODO: descomentar cuando exista apps.planner
        # Block.objects.filter(category=category).update(category=fallback)
        messages.success(self.request, f'Categoría eliminada. Sus bloques pasaron a "Otros".')
        return super().form_valid(form)
