# about/views.py
from django.views.generic.base import TemplateView


# Описать класс AboutAuthorView для страницы about/author
class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Здесь можно произвести какие-то действия для создания контекста.

        return context


# Описать класс AboutTechView для страницы about/tech
class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Здесь можно произвести какие-то действия для создания контекста.

        return context
