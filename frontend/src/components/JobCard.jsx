import { Link } from "react-router-dom";

export default function JobCard({ job }) {
  return (
    <Link
      to={`/jobs/${job.id}`}
      className="block bg-white rounded-lg shadow p-5 hover:shadow-lg transition"
    >
      <h3 className="font-semibold text-lg text-slate-800">{job.title}</h3>
      <p className="text-sm text-slate-500 mb-1">
        {job.company_name || job.recruiter_username} · {job.location}
      </p>
      <p className="text-sm text-slate-600 mb-3">
        {job.package || "Package not specified"}
      </p>

      <div className="flex flex-wrap gap-2">
        {(job.skills_required || []).slice(0, 4).map((skill) => (
          <span
            key={skill}
            className="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded"
          >
            {skill}
          </span>
        ))}
      </div>

      <div className="flex justify-between items-center mt-3 text-xs text-slate-500">
        <span className="uppercase">{job.job_type.replace("_", " ")}</span>
        {job.deadline && <span>Apply by {job.deadline}</span>}
      </div>
    </Link>
  );
}