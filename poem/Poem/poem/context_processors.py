from django.conf import settings # import the settings file


def admin_settings(context):
    """
    Simple context processor that adds settings.POEM_NAMESPACE to templates.
    """
    # return the value you want as a dictionnary. you may add multiple values in there.
    return { 'POEM_NAMESPACE': settings.POEM_NAMESPACE }