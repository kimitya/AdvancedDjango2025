// src/pages/JobMatches.tsx
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getJobMatches } from '../services/api'
import toast from 'react-hot-toast'

export default function JobMatches() {
  const { jobId } = useParams()
  const { data: matches, isLoading, error } = useQuery({
    queryKey: ['jobMatches', jobId],
    queryFn: () => getJobMatches(jobId!),
    onError: (err: any) => {
      console.error('Error fetching job matches:', err.response?.data || err.message)
      toast.error(
        err.response?.data?.error || 
        err.message || 
        'Failed to fetch matching resumes. Please try again.'
      )
    },
  })

  if (isLoading) return <div className="text-center">Loading...</div>

  if (error) {
    return (
      <div className="text-center text-red-600">
        Error loading matches: {error.message}
      </div>
    )
  }

  if (!matches?.data || matches.data.length === 0) {
    return (
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Resume Matches</h1>
        <p>No matching resumes found for this job.</p>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 text-center">Resume Matches</h1>
      <div className="grid gap-6">
        {matches.data.map((match: any) => (
          <div
            key={match.resume_id}
            className="border p-6 rounded-lg shadow-md bg-white hover:shadow-lg transition-shadow"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-lg font-semibold text-gray-800">
                  <strong>User:</strong> {match.user || 'Unknown'}
                </p>
                <p className="text-gray-600">
                  <strong>Resume ID:</strong> {match.resume_id || 'N/A'}
                </p>
                <p className="text-gray-600">
                  <strong>Compatibility Score:</strong> {match.compatibility_score?.toFixed(2) || 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-gray-600">
                  <strong>Matched Skills:</strong>{' '}
                  {match.matched_skills ? match.matched_skills : 'None'}
                </p>
                <p className="text-gray-600">
                  <strong>All Skills:</strong>{' '}
                  {match.resume_skills ? match.resume_skills : 'None'}
                </p>
                <p className="text-gray-600">
                  <strong>Experience:</strong>{' '}
                  {match.resume_experience ? match.resume_experience : 'Not specified'}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}