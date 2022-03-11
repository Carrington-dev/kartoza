from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.urls import reverse
from account.models import UserAccount
import folium
from folium import plugins
from django.utils.safestring import mark_safe
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin



# Create your views here.
def home(request):
    data = UserAccount.objects.all()
    # data_list = UserAccount.objects.values_list('latitude', 'longitude', ')

    # map1 = folium.Map(location=[19, -12],
    #                   tiles='CartoDB Dark_Matter', zoom_start=2)

    # plugins.HeatMap(data_list).add_to(map1)
    # plugins.Fullscreen(position='topright').add_to(map1)
    map1 = folium.Map(location=[19, -34],
    tiles='Stamen Terrain',
    zoom_start=2)
    tooltip = "Click me!"
    for user in data:
        # folium.Circle(
        #     radius=100,
        #     location=[user.latitude, user.longitude],
        #     popup=f"<b>{user.location}</b>",
        #     color="crimson",
        #     fill=False,
        # mark_safe(f'<a href="{url}">View</a>')
        # ).add_to(map1)
        url = reverse('user_detail', args=(user.id,))
        
        folium.Marker([user.latitude, user.longitude],
         popup=mark_safe(f'<a href="{url}"><b>{user.email}<br/>{user.username}<br/>{user.first_name} {user.last_name}</b></a>'), tooltip=f"<b>{user.location}</b>",
         icon=folium.Icon(color="green", icon_color="white", tint="cadetblue")
         ).add_to(map1)
        # folium.Marker([45.3288, -121.6625], popup=f"<b>{user.location}</b>", tooltip=tooltip).add_to(map1)

    map1 = map1._repr_html_()
    context = {
        'map1': map1
    }
    return render(request, "account/index.html", context)


class UserListView(ListView):
    model = UserAccount
    template_name = "account/home.html"
    context_object_name = 'accounts'
    # paginate_by = 2
    queryset = UserAccount.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['title'] = "Home"
        return context

class UserDetailView(LoginRequiredMixin, DetailView):
    model = UserAccount
    template_name = "account/home.html"
    context_object_name = 'account'
    # paginate_by = 2
    queryset = UserAccount.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['title'] = "Home"

        map1 = folium.Map(location=[19, -34],
        tiles='Stamen Terrain',
        zoom_start=2)
        tooltip = "Click me!"
        user = self.request.user
        
        url = reverse('user_detail', args=(user.id,))
        
        folium.Marker([user.latitude, user.longitude],
        popup=mark_safe(f'<a href="{url}"><b>{user.email}<br/>{user.username}<br/>{user.first_name} {user.last_name}</b></a>'), tooltip=f"<b>{user.location}</b>",
        icon=folium.Icon(color="green", icon_color="white", tint="cadetblue")
        ).add_to(map1)
        # folium.Marker([45.3288, -121.6625], popup=f"<b>{user.location}</b>", tooltip=tooltip).add_to(map1)

        map1 = map1._repr_html_()
        context = {
            'user_map': map1
        }
        return context
    
    def dispatch(self, request, *args, **kwargs):
        handler = super().dispatch(request, *args, **kwargs)
        user = request.user
        user_check = self.get_object()
        if not (user_check == user or user.is_superuser):
            raise PermissionDenied
        return handler