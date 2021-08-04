from django.conf.urls import url
from cov19 import views
urlpatterns = [
    url('map', views.reptile,name='map'),
    url('time', views.time1,name='history'),
    url('index', views.index,name='index'),
    url('move', views.move,name='move'),
    url('wordcloud', views.wordc,name='wordcloud'),
    url('line', views.line,name='line'),
    url('world', views.world,name='world'),
    url('ranking', views.ranking,name='ranking'),
]
