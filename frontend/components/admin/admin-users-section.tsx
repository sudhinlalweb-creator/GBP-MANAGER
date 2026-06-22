type AdminUser = {
  id: string;
  name: string;
  email: string;
  role: string;
  organization: string;
  status: string;
  lastActive: string;
  isActive: boolean;
};

type AdminUsersSectionProps = {
  users: AdminUser[];
  pendingUserId: string | null;
  onToggleUserStatus: (userId: string, nextIsActive: boolean) => void;
};

function statusClasses(status: string): string {
  if (status === "suspended") {
    return "border-rose-500/30 bg-rose-500/10 text-rose-200";
  }
  if (status === "trial") {
    return "border-amber-500/30 bg-amber-500/10 text-amber-200";
  }
  return "border-emerald-500/30 bg-emerald-500/10 text-emerald-200";
}

function formatStatusLabel(status: string): string {
  return status.charAt(0).toUpperCase() + status.slice(1);
}

export function AdminUsersSection({
  users,
  pendingUserId,
  onToggleUserStatus
}: AdminUsersSectionProps): JSX.Element {
  return (
    <section id="users" className="rounded-3xl border border-border bg-card p-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-emerald-300">Users</p>
          <h2 className="text-2xl font-semibold tracking-tight">User Access Control</h2>
        </div>
        <p className="text-sm text-slate-400">Recent accounts, tenant roles, and access state.</p>
      </div>

      {users.length === 0 ? (
        <div className="mt-6 rounded-2xl border border-dashed border-border px-4 py-8 text-sm text-slate-400">
          No users are available yet.
        </div>
      ) : (
        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full divide-y divide-border text-sm">
            <thead>
              <tr className="text-left text-slate-400">
                <th className="pb-3 pr-4 font-medium">User</th>
                <th className="pb-3 pr-4 font-medium">Role</th>
                <th className="pb-3 pr-4 font-medium">Organization</th>
                <th className="pb-3 pr-4 font-medium">Status</th>
                <th className="pb-3 pr-4 font-medium">Last Active</th>
                <th className="pb-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/80">
              {users.map((user) => (
                <tr key={user.id}>
                  <td className="py-4 pr-4">
                    <p className="font-medium text-slate-100">{user.name}</p>
                    <p className="mt-1 text-slate-400">{user.email}</p>
                  </td>
                  <td className="py-4 pr-4 text-slate-200">{user.role}</td>
                  <td className="py-4 pr-4 text-slate-300">{user.organization}</td>
                  <td className="py-4 pr-4">
                    <span
                      className={`inline-flex rounded-full border px-3 py-1 text-xs uppercase tracking-[0.2em] ${statusClasses(user.status)}`}
                    >
                      {formatStatusLabel(user.status)}
                    </span>
                  </td>
                  <td className="py-4 pr-4 text-slate-400">{user.lastActive}</td>
                  <td className="py-4">
                    <button
                      type="button"
                      onClick={() => onToggleUserStatus(user.id, !user.isActive)}
                      disabled={pendingUserId === user.id}
                      className="rounded-xl border border-border px-3 py-2 text-xs font-medium text-slate-200 transition hover:border-emerald-500/40 hover:bg-emerald-500/5 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {pendingUserId === user.id
                        ? "Saving..."
                        : user.isActive
                          ? "Suspend"
                          : "Reactivate"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
