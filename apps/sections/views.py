from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from .models import Section
from apps.common.mixins import AdminRequiredMixin


class SectionListView(AdminRequiredMixin, LoginRequiredMixin, ListView):
    """Admin view to list all sections."""
    template_name = 'sections/section_list.html'
    context_object_name = 'sections'
    login_url = '/accounts/login/'
    paginate_by = 20

    def get_queryset(self):
        queryset = Section.objects.select_related('branch', 'branch__department').all()
        search = self.request.GET.get('search', '').strip()
        department = self.request.GET.get('department', '')
        semester = self.request.GET.get('semester', '')
        status = self.request.GET.get('status', '')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(branch__name__icontains=search) |
                Q(branch__code__icontains=search)
            )

        if department:
            queryset = queryset.filter(branch__department_id=department)

        if semester:
            queryset = queryset.filter(semester=semester)

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
        context['semester_filter'] = self.request.GET.get('semester', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['semester_choices'] = range(1, 9)
        return context


class SectionCreateView(AdminRequiredMixin, LoginRequiredMixin, CreateView):
    """Admin view to create a new section."""
    model = Section
    template_name = 'sections/section_form.html'
    fields = ['branch', 'name', 'semester', 'is_active']
    login_url = '/accounts/login/'
    success_url = reverse_lazy('sections:section_list')

    def form_valid(self, form):
        branch = form.cleaned_data.get('branch')
        name = form.cleaned_data.get('name')
        semester = form.cleaned_data.get('semester')

        if self.model.objects.filter(branch=branch, name=name, semester=semester).exists():
            form.add_error('name', 'A section with this name already exists for this branch and semester.')
            return self.form_invalid(form)

        messages.success(self.request, f'Section "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.branches.models import Branch
        context['branches'] = Branch.objects.filter(is_active=True)
        context['semester_choices'] = range(1, 9)
        context['page_title'] = 'Add Section'
        context['is_create'] = True
        return context


class SectionUpdateView(AdminRequiredMixin, LoginRequiredMixin, UpdateView):
    """Admin view to edit a section."""
    model = Section
    template_name = 'sections/section_form.html'
    fields = ['branch', 'name', 'semester', 'is_active']
    login_url = '/accounts/login/'
    success_url = reverse_lazy('sections:section_list')

    def form_valid(self, form):
        branch = form.cleaned_data.get('branch')
        name = form.cleaned_data.get('name')
        semester = form.cleaned_data.get('semester')

        if self.model.objects.filter(branch=branch, name=name, semester=semester).exclude(pk=self.object.pk).exists():
            form.add_error('name', 'A section with this name already exists for this branch and semester.')
            return self.form_invalid(form)

        messages.success(self.request, f'Section "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.branches.models import Branch
        context['branches'] = Branch.objects.filter(is_active=True)
        context['semester_choices'] = range(1, 9)
        context['page_title'] = 'Edit Section'
        context['is_create'] = False
        return context
