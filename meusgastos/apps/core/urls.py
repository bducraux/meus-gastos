from django.urls import path

from . import views

app_name = 'core'
urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('data/', views.dashboard_data_view, name='dashboard_data'),
    # ex: /polls/5/
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # ex: /polls/5/results/
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # ex: /polls/5/vote/
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]