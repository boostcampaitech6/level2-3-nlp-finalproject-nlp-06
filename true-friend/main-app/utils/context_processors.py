import os


# Setting global variables in Django templates
# https://medium.com/@malvin.lok/how-to-add-global-variable-on-django-template-83e57a96a8b5
# https://velog.io/@dhleeone/django-template-context-processors%EB%A5%BC-%ED%86%B5%ED%95%B4-%EB%8F%99%EC%8B%9C%EC%97%90-%EC%97%AC%EB%9F%AC-%ED%85%9C%ED%94%8C%EB%A6%BF%EC%97%90-view-%EC%A0%81%EC%9A%A9%ED%95%98%EA%B8%B0
def settings_context_processor(request):
    context = {
        'hostname': os.environ.get('HOST_NAME', 'localhost'),
    }
    return context