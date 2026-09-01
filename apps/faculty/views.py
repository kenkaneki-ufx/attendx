from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from apps.common.mixins import AdminRequiredMixin

Faculty = get_user_model()


class FacultyListView(AdminRequiredMixin, LoginRequiredMixin, ListView):
    """Admin view to list all faculty members."""
    model = Faculty
    template_name = 'faculty/faculty_list.html'
    context_object_name = 'faculty_list'
    login_url = '/accounts/login/'
    paginate_by = 20

    # Allowed sort fields and their directions
    SORT_FIELDS = {
        'name': 'first_name',
        'email': 'email',
        'employee_id': 'employee_id',
        'department': 'department__name',
        'role': 'is_admin',
        'status': 'is_active',
    }

    def get_paginate_by(self, queryset):
        """Allow per_page parameter to override default."""
        per_page = self.request.GET.get('per_page', '')
        if per_page and per_page.isdigit() and int(per_page) in [10, 20, 50, 100]:
            return int(per_page)
        return self.paginate_by

    def get_queryset(self):
        queryset = Faculty.objects.all().select_related('department')
        search = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '')
        department = self.request.GET.get('department', '')
        sort_by = self.request.GET.get('sort', 'name')
        sort_dir = self.request.GET.get('dir', 'asc')

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search)
            )

        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status == 'admin':
            queryset = queryset.filter(is_admin=True)

        if department:
            queryset = queryset.filter(department_id=department)

        # Apply sorting
        if sort_by in self.SORT_FIELDS:
            field = self.SORT_FIELDS[sort_by]
            if sort_dir == 'desc':
                queryset = queryset.order_by(f'-{field}')
            else:
                queryset = queryset.order_by(field)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['department_filter'] = self.request.GET.get('department', '')
        context['sort_by'] = self.request.GET.get('sort', 'name')
        context['sort_dir'] = self.request.GET.get('dir', 'asc')
        context['paginate_by'] = self.get_paginate_by(None)
        from apps.departments.models import Department
        context['departments'] = Department.objects.all()
        context['total_count'] = self.get_queryset().count()
        return context


class FacultyCreateView(AdminRequiredMixin, LoginRequiredMixin, CreateView):
    """Admin view to create a new faculty member."""
    model = Faculty
    template_name = 'faculty/faculty_form.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'employee_id',
              'phone', 'department', 'is_active', 'is_staff', 'is_admin']
    login_url = '/accounts/login/'
    success_url = reverse_lazy('faculty:faculty_list')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        employee_id = form.cleaned_data.get('employee_id')

        if Faculty.objects.filter(username=username).exists():
            form.add_error('username', 'A faculty member with this username already exists.')
            return self.form_invalid(form)
        if Faculty.objects.filter(email=email).exists():
            form.add_error('email', 'A faculty member with this email already exists.')
            return self.form_invalid(form)
        if Faculty.objects.filter(employee_id=employee_id).exists():
            form.add_error('employee_id', 'A faculty member with this employee ID already exists.')
            return self.form_invalid(form)

        password = self.request.POST.get('password', '')
        if not password:
            messages.error(self.request, 'Password is required.')
            return self.form_invalid(form)
        if len(password) < 8:
            messages.error(self.request, 'Password must be at least 8 characters.')
            return self.form_invalid(form)

        form.instance.password = make_password(password)
        messages.success(self.request, f'Faculty "{form.instance.username}" created successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Faculty Member'
        context['is_create'] = True
        return context


class FacultyUpdateView(AdminRequiredMixin, LoginRequiredMixin, UpdateView):
    """Admin view to edit a faculty member."""
    model = Faculty
    template_name = 'faculty/faculty_form.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'employee_id',
              'phone', 'department', 'is_active', 'is_staff', 'is_admin']
    login_url = '/accounts/login/'
    success_url = reverse_lazy('faculty:faculty_list')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        employee_id = form.cleaned_data.get('employee_id')

        if Faculty.objects.filter(username=username).exclude(pk=self.object.pk).exists():
            form.add_error('username', 'A faculty member with this username already exists.')
            return self.form_invalid(form)
        if Faculty.objects.filter(email=email).exclude(pk=self.object.pk).exists():
            form.add_error('email', 'A faculty member with this email already exists.')
            return self.form_invalid(form)
        if Faculty.objects.filter(employee_id=employee_id).exclude(pk=self.object.pk).exists():
            form.add_error('employee_id', 'A faculty member with this employee ID already exists.')
            return self.form_invalid(form)

        messages.success(self.request, f'Faculty "{form.instance.username}" updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Faculty Member'
        context['is_create'] = False
        context['edit_user'] = self.object
        return context


@require_POST
def faculty_toggle_status(request, pk):
    """AJAX endpoint to toggle faculty active status."""
    if not request.user.is_authenticated or not request.user.is_admin:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    faculty = get_object_or_404(Faculty, pk=pk)

    # Prevent self-deactivation
    if faculty.pk == request.user.pk:
        return JsonResponse({'success': False, 'message': 'Cannot deactivate your own account'})

    faculty.is_active = not faculty.is_active
    faculty.save(update_fields=['is_active'])

    return JsonResponse({
        'success': True,
        'is_active': faculty.is_active,
        'message': f'Faculty {faculty.username} {"activated" if faculty.is_active else "deactivated"}'
    })


class FacultySubjectAssignmentView(AdminRequiredMixin, LoginRequiredMixin, ListView):
    """Admin view to manage faculty-subject assignments."""
    template_name = 'faculty/assignments.html'
    context_object_name = 'assignments'
    login_url = '/accounts/login/'

    def get_queryset(self):
        from apps.faculty.models import FacultySubjectAssignment
        return FacultySubjectAssignment.objects.all().select_related(
            'faculty', 'subject', 'section', 'subject__department'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faculty_list'] = Faculty.objects.filter(is_active=True, is_admin=False)
        from apps.subjects.models import Subject
        context['subjects'] = Subject.objects.all()
        from apps.sections.models import Section
        context['sections'] = Section.objects.all()
        return context


@require_POST
def create_assignment(request):
    """AJAX endpoint to create a faculty-subject assignment."""
    if not request.user.is_authenticated or not request.user.is_admin:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    from apps.faculty.models import FacultySubjectAssignment

    faculty_id = request.POST.get('faculty_id')
    subject_id = request.POST.get('subject_id')
    section_id = request.POST.get('section_id')
    academic_year = request.POST.get('academic_year', '2025-2026')

    if not all([faculty_id, subject_id, section_id]):
        return JsonResponse({'success': False, 'message': 'All fields are required'})

    # Check for duplicate assignment
    if FacultySubjectAssignment.objects.filter(
        faculty_id=faculty_id,
        subject_id=subject_id,
        section_id=section_id,
        academic_year=academic_year,
    ).exists():
        return JsonResponse({'success': False, 'message': 'This assignment already exists for this academic year'})

    try:
        assignment = FacultySubjectAssignment.objects.create(
            faculty_id=faculty_id,
            subject_id=subject_id,
            section_id=section_id,
            academic_year=academic_year,
        )
        return JsonResponse({
            'success': True,
            'message': f'Assignment created: {assignment.faculty.get_full_name()} -> {assignment.subject.code}'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
def delete_assignment(request, pk):
    """AJAX endpoint to delete a faculty-subject assignment."""
    if not request.user.is_authenticated or not request.user.is_admin:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    from apps.faculty.models import FacultySubjectAssignment
    assignment = get_object_or_404(FacultySubjectAssignment, pk=pk)
    assignment.delete()
    return JsonResponse({'success': True, 'message': 'Assignment deleted'})
