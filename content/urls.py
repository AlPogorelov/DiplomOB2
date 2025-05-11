from django.urls import path
from content.apps import ContentConfig
from content.views import HomeView, ContentCreateView, ContentUpdateView, ContentDeleteView, ContentDetailView, \
    ContentListView, CategoryListView, CategoryDetailView, CategoryUpdateView, CategoryDeleteView, CategoryCreateView, \
    FreeContentList, MyContentList, CategoryContentList

app_name = ContentConfig.name

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('contents/', ContentListView.as_view(), name='contents_list'),
    path('filter_contents/<int:category_pk>/', CategoryContentList.as_view(), name='category_content'),
    path('<int:pk>/', ContentDetailView.as_view(), name='content_detail'),
    path('<int:pk>/delete/', ContentDeleteView.as_view(), name='content_delete'),
    path('<int:pk>/update/', ContentUpdateView.as_view(), name='content_update'),
    path('create/', ContentCreateView.as_view(), name='content_create'),
    path('free/', FreeContentList.as_view(), name='free_content'),
    path('my/', MyContentList.as_view(), name='my_content'),


    path('categories/', CategoryListView.as_view(), name='categories_list'),
    path('category/<int:category_pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('category/<int:category_pk>/update/', CategoryUpdateView.as_view(), name='category_update'),
    path('category/<int:category_pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    path('category/create/', CategoryCreateView.as_view(), name='category_create'),


]
