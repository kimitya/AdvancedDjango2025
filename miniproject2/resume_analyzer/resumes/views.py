# resumes/views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Resume, JobDescription, Log
from .serializers import ResumeSerializer, JobDescriptionSerializer
from .utils import process_resume, process_job_description, match_resume_to_job
from .permissions import IsRecruiter


class ResumeUploadView(generics.CreateAPIView):
    queryset = Resume.objects.using('mongo').all()
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        resume = serializer.save(user=self.request.user)
        try:
            analysis = process_resume(resume.file)
            resume.skills = analysis['skills']
            resume.experience = analysis['experience']
            resume.education = analysis['education']
            resume.rating = analysis['rating']
            resume.recommendations = analysis['recommendations']
            resume.set_feedback(analysis['feedback'])
            resume.save(using='mongo')

            Log.objects.using('mysql').create(
                user_id=self.request.user.id,
                action="Uploaded resume",
                details=f"Resume ID: {resume.id}"
            )

            serializer = self.get_serializer(resume)
            return Response(serializer.data)
        except Exception as e:
            resume.delete(using='mongo')
            return Response({'error': f"Failed to process resume: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)

class ResumeDetailView(generics.RetrieveAPIView):
    queryset = Resume.objects.using('mongo').all()
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.using('mongo').filter(user=self.request.user)


class JobDescriptionCreateView(generics.CreateAPIView):
    queryset = JobDescription.objects.all()
    serializer_class = JobDescriptionSerializer
    permission_classes = [IsRecruiter]

    def perform_create(self, serializer):
        job = serializer.save(recruiter=self.request.user)
        analysis = process_job_description(job.description)
        job.required_skills = ', '.join(analysis['required_skills'])
        job.required_experience = analysis['required_experience']
        job.save()

        Log.objects.using('mysql').create(
            user_id=self.request.user.id,
            action="Created job description",
            details=f"Job ID: {job.id}"
        )

        resumes = Resume.objects.using('mongo').all()
        if not resumes.exists():
            return Response({
                'job': JobDescriptionSerializer(job).data,
                'matches': [],
                'message': 'No resumes available for matching'
            })

        matches = []
        for resume in resumes:
            try:
                match = match_resume_to_job(resume, job)
                matches.append(match)
            except Exception as e:
                print(f"Error matching resume {resume.id}: {str(e)}")
                continue

        matches = sorted(matches, key=lambda x: x['compatibility_score'], reverse=True)
        return Response({
            'job': JobDescriptionSerializer(job).data,
            'matches': matches[:10]
        })


class JobDescriptionMatchView(generics.ListAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsRecruiter]

    def get_queryset(self):
        job_id = self.kwargs['job_id']
        try:
            job = JobDescription.objects.get(id=job_id, recruiter=self.request.user)
            resumes = Resume.objects.using('mongo').all()
            matches = [match_resume_to_job(resume, job) for resume in resumes]
            matches = sorted(matches, key=lambda x: x['compatibility_score'], reverse=True)
            matched_resume_ids = [match['resume_id'] for match in matches[:10]]
            return Resume.objects.using('mongo').filter(id__in=matched_resume_ids)
        except JobDescription.DoesNotExist:
            return Resume.objects.using('mongo').none()

    def list(self, request, *args, **kwargs):
        job_id = self.kwargs['job_id']
        job = JobDescription.objects.get(id=job_id, recruiter=self.request.user)
        queryset = self.get_queryset()
        matches = [match_resume_to_job(resume, job) for resume in queryset]
        return Response(matches)


class JobDescriptionListView(generics.ListAPIView):
    queryset = JobDescription.objects.all()
    serializer_class = JobDescriptionSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class JobDescriptionDetailView(generics.RetrieveAPIView):
    queryset = JobDescription.objects.all()
    serializer_class = JobDescriptionSerializer
    permission_classes = [IsAuthenticated]