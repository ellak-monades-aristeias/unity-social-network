from django import forms

basic_target_options = (
    ('Public', 'Public'),
    ('Private', 'Private'),
    ('User', 'User'),
)
# TODO Give Option to Post based on relations
# from relationships.models import RelationshipStatus
# relationship_target_options = [(RS.name, RS.name) for RS in RelationshipStatus.objects.all() ]
# target_options = basic_target_options + tuple(relationship_target_options)

class Post_Form(forms.Form):
	content = forms.CharField()
	target = forms.ChoiceField(choices=basic_target_options)
	actor_name = forms.CharField()