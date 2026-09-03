from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from .models import Department
from apps.common.mixins import AdminRequiredMixin


class DepartmentListView(AdminRequiredMixin, LoginRequiredMixin, ListView):
    """Admin view to list all departments."""
    model = Department
    template_name = 'departments/department_list.html'
    context_object_name = 'departments'
    login_url = '/accounts/login/'
    paginate_by = 20

    def get_queryset(self):
        queryset = Department.objects.all()
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )

        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class DepartmentCreateView(AdminRequiredMixin, LoginRequiredMixin, CreateView):
    """Admin view to create a new department."""
    model = Department
    template_name = 'departments/department_form.html'
    fields = ['name', 'code', 'description', 'is_active']
    login_url = '/accounts/login/'
    success_url = reverse_lazy('departments:department_list')

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        code = form.cleaned_data.get('code')

        if self.model.objects.filter(name=name).exists():
            form.add_error('name', 'A department with this name already exists.')
            return self.form_invalid(form)
        if self.model.objects.filter(code=code).exists():
            form.add_error('code', 'A department with this code already exists.')
            return self.form_invalid(form)

        messages.success(self.request, f'Department "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Department'
        context['is_create'] = True
        return context


class DepartmentUpdateView(AdminRequiredMixin, LoginRequiredMixin, UpdateView):
    """Admin view to edit a department."""
    model = Department
    template_name = 'departments/department_form.html'
    fields = ['name', 'code', 'description', 'is_active']
    login_url = '/accounts/login/'
    success_url = reverse_lazy('departments:department_list')

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        code = form.cleaned_data.get('code')

        if self.model.objects.filter(name=name).exclude(pk=self.object.pk).exists():
            form.add_error('name', 'A department with this name already exists.')
            return self.form_invalid(form)
        if self.model.objects.filter(code=code).exclude(pk=self.object.pk).exists():
            form.add_error('code', 'A department with this code already exists.')
            return self.form_invalid(form)

        messages.success(self.request, f'Department "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Department'
        context['is_create'] = False
        return context
