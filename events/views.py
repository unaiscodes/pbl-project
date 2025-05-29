from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    DeleteView,
    View,
)
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import (
    EventCategory,
    Event,
    JobCategory,
    EventJobCategoryLinking,
    EventMember,
    EventUserWishList,
    UserCoin,
    EventImage,
    EventAgenda

)
from .forms import EventForm, EventImageForm, EventAgendaForm, EventCreateMultiForm


# Event category list view
class EventCategoryListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = EventCategory
    template_name = 'events/event_category.html'
    context_object_name = 'event_category'


class EventCategoryCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = EventCategory
    fields = ['name', 'code', 'image', 'priority', 'status']
    template_name = 'events/create_event_category.html'

    def form_valid(self, form):
        form.instance.created_user = self.request.user
        form.instance.updated_user = self.request.user
        return super().form_valid(form)


class EventCategoryUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = EventCategory
    fields = ['name', 'code', 'image', 'priority', 'status']
    template_name = 'events/edit_event_category.html'


class EventCategoryDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model =  EventCategory
    template_name = 'events/event_category_delete.html'
    success_url = reverse_lazy('event-category-list')

@login_required(login_url='login')
def create_event(request):
    event_form = EventForm()
    event_image_form = EventImageForm()
    event_agenda_form = EventAgendaForm()
    job_categories = JobCategory.objects.all()
    
    if request.method == 'POST':
        event_form = EventForm(request.POST)
        event_image_form = EventImageForm(request.POST, request.FILES)
        event_agenda_form = EventAgendaForm(request.POST)
        
        # Handle job category input
        job_category_name = request.POST.get('job_category_name')
        
        if event_form.is_valid() and event_image_form.is_valid() and event_agenda_form.is_valid():
            # Save the event form first
            ef = event_form.save(commit=False)
            
            # Process job category
            if job_category_name and job_category_name.strip():
                job_category, created = JobCategory.objects.get_or_create(
                    name=job_category_name.strip()
                )
                ef.job_category = job_category
                
            # Set category to None (removing the category requirement)
            ef.category = None
            
            # Save the event
            ef.save()
            
            # Handle the event image
            event_image = event_image_form.save(commit=False)
            event_image.event = ef  # Correct attribute name
            event_image.save()
            
            # Handle the event agenda
            event_agenda = event_agenda_form.save(commit=False)
            event_agenda.event = ef  # Correct attribute name
            event_agenda.save()
            
            # Set created_user and updated_user fields directly
            ef.created_user = request.user
            ef.updated_user = request.user
            ef.save()
                
            return redirect('event-list')
    
    context = {
        'form': event_form,
        'form_1': event_image_form,
        'form_2': event_agenda_form,
        'job_categories': job_categories  # Include job_categories in context
    }
    return render(request, 'events/create.html', context)

class EventCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    form_class = EventCreateMultiForm
    template_name = 'events/create_event.html'
    success_url = reverse_lazy('event-list')

    def form_valid(self, form):
        evt = form['event'].save(commit=False)
        
        # Handle job_category as text input
        job_category_name = self.request.POST.get('job_category_name')
        if job_category_name and job_category_name.strip():
            # Try to find an existing job category with this name
            job_category, created = JobCategory.objects.get_or_create(
                name=job_category_name.strip()
            )
            evt.job_category = job_category
            
        # Set category to None (removing the category requirement)
        evt.category = None
                
        evt.save()
        
        event_image = form['event_image'].save(commit=False)
        event_image.event = evt
        event_image.save()

        event_agenda = form['event_agenda'].save(commit=False)
        event_agenda.event = evt
        event_agenda.save()

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['job_categories'] = JobCategory.objects.all()
        return context


class EventListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'


class EventUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Event
    fields = ['name', 'description', 'scheduled_status', 'venue', 'start_date', 'end_date', 'location', 'points', 'maximum_attende', 'status']
    template_name = 'events/edit_event.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add job category to context
        if self.object.job_category:
            context['job_category_name'] = self.object.job_category.name
        return context
        
    def form_valid(self, form):
        event = form.save(commit=False)
        
        # Handle job category
        job_category_name = self.request.POST.get('job_category_name')
        if job_category_name and job_category_name.strip():
            job_category, created = JobCategory.objects.get_or_create(
                name=job_category_name.strip()
            )
            event.job_category = job_category
            
        # Set category to None (removing the category requirement)
        event.category = None
            
        event.save()
        return super().form_valid(form)


class EventDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'


class EventDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = Event
    template_name = 'events/delete_event.html'
    success_url = reverse_lazy('event-list')


class AddEventMemberCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = EventMember
    fields = ['event', 'user', 'attend_status', 'status']
    template_name = 'events/add_event_member.html'

    def form_valid(self, form):
        form.instance.created_user = self.request.user
        form.instance.updated_user = self.request.user
        return super().form_valid(form)


class JoinEventListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = EventMember
    template_name = 'events/joinevent_list.html'
    context_object_name = 'eventmember'


class RemoveEventMemberDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = EventMember
    template_name = 'events/remove_event_member.html'
    success_url = reverse_lazy('join-event-list')


class EventUserWishListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = EventUserWishList
    template_name = 'events/event_user_wish_list.html'
    context_object_name = 'eventwish'


class AddEventUserWishListCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = EventUserWishList
    fields = ['event', 'user', 'status']
    template_name = 'events/add_event_user_wish.html'

    def form_valid(self, form):
        form.instance.created_user = self.request.user
        form.instance.updated_user = self.request.user
        return super().form_valid(form)


class RemoveEventUserWishDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = EventUserWishList
    template_name = 'events/remove_event_user_wish.html'
    success_url = reverse_lazy('event-wish-list')


class UpdateEventStatusView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = Event
    fields = ['status']
    template_name = 'events/update_event_status.html'


class CompleteEventList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = Event
    template_name = 'events/complete_event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(status='completed')


class AbsenseUserList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = EventMember
    template_name = 'events/absense_user_list.html'
    context_object_name = 'absenseuser'

    def get_queryset(self):
        return EventMember.objects.filter(attend_status='absent')


class CompleteEventUserList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = EventMember
    template_name = 'events/complete_event_user_list.html'
    context_object_name = 'completeuser'

    def get_queryset(self):
        return EventMember.objects.filter(attend_status='completed')


class CreateUserMark(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = UserCoin
    fields = ['user', 'gain_type', 'gain_coin', 'status']
    template_name = 'events/create_user_mark.html'

    def form_valid(self, form):
        form.instance.created_user = self.request.user
        form.instance.updated_user = self.request.user
        return super().form_valid(form)


class UserMarkList(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = UserCoin
    template_name = 'events/user_mark_list.html'
    context_object_name = 'usermark'


@login_required(login_url='login')
def search_event_category(request):
    if request.method == 'POST':
       data = request.POST['search']
       event_category = EventCategory.objects.filter(name__icontains=data)
       context = {
           'event_category': event_category
       }
       return render(request, 'events/event_category.html', context)
    return render(request, 'events/event_category.html')

@login_required(login_url='login')
def search_event(request):
    if request.method == 'POST':
       data = request.POST['search']
       events = Event.objects.filter(name__icontains=data)
       context = {
           'events': events
       }
       return render(request, 'events/event_list.html', context)
    return render(request, 'events/event_list.html')


# Job Category Views
class JobCategoryListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    model = JobCategory
    template_name = 'events/job_category_list.html'
    context_object_name = 'job_categories'


class JobCategoryCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login'
    model = JobCategory
    fields = ['name']
    template_name = 'events/create_job_category.html'
    success_url = reverse_lazy('job-category-list')


class JobCategoryUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    model = JobCategory
    fields = ['name']
    template_name = 'events/edit_job_category.html'
    success_url = reverse_lazy('job-category-list')


class JobCategoryDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'login'
    model = JobCategory
    template_name = 'events/delete_job_category.html'
    success_url = reverse_lazy('job-category-list')
