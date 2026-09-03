from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from .models import Branch
from apps.common.mixins import AdminRequiredMixin


class BranchListView(AdminRequiredMixin, LoginRequiredMixin, ListView):
    """Admin view to list all branches."""
    template_name = 'branches/branch_list.html'
    context_object_name = 'branches'
    login_url = '/accounts/login/'
    paginate_by = 20

    def get_queryset(self):
        queryset = Branch.objects.select_related('department').all()
        search = self.request.GET.get('search', '').strip()
        department = self.request.GET.get('department', '')
        status = self.request.GET.get('status', '')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )

        if department:
            queryset = queryset.filter(department_id=department)

        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.departments.models import Department
        context['departments'] = Department.objects.all()
        context['search'] = self.request.GET.get('search', '')
        context['department_filter'] = self.request.GET.get('department', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class BranchCreateView(AdminRequiredMixin, LoginRequiredMixin, CreateView):
    """Admin view to create a new branch."""
    model = Branch
    template_name = 'branches/branch_form.html'
    fields = ['department', 'name', 'code', 'is_active']
    login_url = '/accounts/login/'
    success_url = reverse_lazy('branches:branch_list')

    def form_valid(self, form):
        department = form.cleaned_data.get('department')
        code = form.cleaned_data.get('code')

        if self.model.objects.filter(department=department, code=code).exists():
            form.add_error('code', 'A branch with this code already exists in this department.')
            return self.form_invalid(form)

        messages.success(self.request, f'Branch "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.departments.models import Department
        context['departments'] = Department.objects.all()
        context['page_title'] = 'Add Branch'
        context['is_create'] = True
        return context


class BranchUpdateView(AdminRequiredMixin, LoginRequiredMixin, UpdateView):
    """Admin view to edit a branch."""
    model = Branch
    template_name = 'branches/branch_form.html'
    fields = ['department', 'name', 'code', 'is_active']
    login_url = '/accounts/login/'
    success_url = reverse_lazy('branches:branch_list')

    def form_valid(self, form):
        department = form.cleaned_data.get('department')
        code = form.cleaned_data.get('code')

        if self.model.objects.filter(department=department, code=code).exclude(pk=self.object.pk).exists():
            form.add_error('code', 'A branch with this code already exists in this department.')
            return self.form_invalid(form)

        messages.success(self.request, f'Branch "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.departments.models import Department
        context['departments'] = Department.objects.all()
        context['page_title'] = 'Edit Branch'
        context['is_create'] = False
        return context
