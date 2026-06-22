type Profile = {
  id: string;
  google_location_name: string;
  primary_category: string | null;
  website_url: string | null;
  updated_at: string;
};

type ProfileListProps = {
  profiles: Profile[];
};

export function ProfileList({ profiles }: ProfileListProps): JSX.Element {
  return (
    <article className="rounded-3xl border border-border bg-card p-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Recent Google Business Profiles</h2>
        <span className="text-sm text-slate-400">{profiles.length} visible</span>
      </div>
      <div className="mt-5 overflow-hidden rounded-2xl border border-border">
        <table className="min-w-full divide-y divide-slate-800 text-left text-sm">
          <thead className="bg-slate-950/60 text-slate-400">
            <tr>
              <th className="px-4 py-3 font-medium">Business</th>
              <th className="px-4 py-3 font-medium">Category</th>
              <th className="px-4 py-3 font-medium">Website</th>
              <th className="px-4 py-3 font-medium">Updated</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 bg-card">
            {profiles.length === 0 ? (
              <tr>
                <td className="px-4 py-6 text-slate-400" colSpan={4}>
                  No profiles have been synced yet.
                </td>
              </tr>
            ) : (
              profiles.map((profile) => (
                <tr key={profile.id}>
                  <td className="px-4 py-4">{profile.google_location_name}</td>
                  <td className="px-4 py-4 text-slate-300">{profile.primary_category ?? "Uncategorized"}</td>
                  <td className="px-4 py-4 text-slate-300">
                    {profile.website_url ? (
                      <a
                        href={profile.website_url}
                        className="text-emerald-300 hover:text-emerald-200"
                        target="_blank"
                        rel="noreferrer"
                      >
                        Visit
                      </a>
                    ) : (
                      "Not provided"
                    )}
                  </td>
                  <td className="px-4 py-4 text-slate-400">
                    {new Date(profile.updated_at).toLocaleString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </article>
  );
}
