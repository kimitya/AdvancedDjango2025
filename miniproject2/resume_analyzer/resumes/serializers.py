

# # resumes/serializers.py
# from rest_framework import serializers
# from .models import Resume
#
# class ResumeSerializer(serializers.ModelSerializer):
#     feedback = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Resume
#         fields = ['id', 'file', 'uploaded_at', 'skills', 'experience', 'education',
#                   'rating', 'recommendations', 'feedback']
#         read_only_fields = ['uploaded_at', 'skills', 'experience', 'education',
#                           'rating', 'recommendations', 'feedback']
#
#     def get_feedback(self, obj):
#         return obj.get_feedback()

# resumes/serializers.py
from rest_framework import serializers
from .models import Resume, JobDescription

class ResumeSerializer(serializers.ModelSerializer):
    feedback = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = ['id', 'file', 'uploaded_at', 'skills', 'experience', 'education',
                  'rating', 'recommendations', 'feedback']
        read_only_fields = ['uploaded_at', 'skills', 'experience', 'education',
                          'rating', 'recommendations', 'feedback']

    def get_feedback(self, obj):
        return obj.get_feedback()

class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields = ['id', 'description', 'required_skills', 'required_experience', 'created_at']
        read_only_fields = ['required_skills', 'required_experience', 'created_at']