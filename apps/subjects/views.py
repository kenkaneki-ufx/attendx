from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from .models import Subject
from apps.common.mixins import AdminRequiredMixin


class SubjectListView(AdminRequiredMixin, LoginRequiredMixin, ListView):
    """Admin view to list all subjects."""
    model = Subject
    template_name = 'subjects/subject_list.html'
    context_object_name = 'subjects'
    login_url = '/accounts/login/'
    paginate_by = 20

    def get_queryset(self):
        queryset = Subject.objects.select_related('department').all()
        search = self.request.GET.get('search', '').strip()
        department = self.request.GET.get('department', '')
        semester = self.request.GET.get('semester', '')
        status = self.request.GET.get('status', '')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )

        if department:
            queryset = queryset.filter(department_id=department)

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


class SubjectCreateView(AdminRequiredMixin, LoginRequiredMixin, CreateView):
    """Admin view to create a new subject."""
    model = Subject
    template_name = 'subjects/subject_form.html'
    fields = ['code', 'name', 'department', 'semester', 'credits', 'description', 'is_active']
    login_url = '/accounts/login/'
    success_url = reverse_lazy('subjects:subject_list')

    def form_valid(self, form):
        code = form.cleaned_data.get('code')

        if self.model.objects.filter(code=code).exists():
            form.add_error('code', 'A subject with this code already exists.')
            return self.form_invalid(form)

        messages.success(self.request, f'Subject "{form.instance.name}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.departments.models import Department
        context['departments'] = Department.objects.all()
        context['semester_choices'] = range(1, 9)
        context['page_title'] = 'Add Subject'
        context['is_create'] = True
        return context


class SubjectUpdateView(AdminRequiredMixin, LoginRequiredMixin, UpdateView):
    """Admin view to edit a subject."""
    model = Subject
    template_name = 'subjects/subject_form.html'
    fields = ['code', 'name', 'department', 'semester', 'credits', 'description', 'is_active']
    login_url = '/accounts/login/'
    success_url = reverse_lazy('subjects:subject_list')

    def form_valid(self, form):
        code = form.cleaned_data.get('code')

        if self.model.objects.filter(code=code).exclude(pk=self.object.pk).exists():
            form.add_error('code', 'A subject with this code already exists.')
            return self.form_invalid(form)

        messages.success(self.request, f'Subject "{form.instance.name}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.departments.models import Department
        context['departments'] = Department.objects.all()
        context['semester_choices'] = range(1, 9)
        context['page_title'] = 'Edit Subject'
        context['is_create'] = False
        return context


class AssignedSubjectsView(LoginRequiredMixin, TemplateView):
    """View showing subjects assigned to the current faculty member."""
    template_name = 'subjects/assigned_subjects.html'
    context_object_name = 'assignments'
    login_url = '/accounts/login/'

    def get_queryset(self):
        from apps.faculty.models import FacultySubjectAssignment
        return FacultySubjectAssignment.objects.filter(
            faculty=self.request.user,
            is_active=True
        ).select_related('subject', 'section', 'subject__department')
