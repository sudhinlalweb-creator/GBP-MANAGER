type IntegrationStatusProps = {
  organizationName: string;
  organizationRole: string;
  googleOauthConfigured: boolean;
  googleMapsConfigured: boolean;
  workerConfigured: boolean;
  connectedAccounts: number;
  syncedProfiles: number;
  lastProfileSyncAt: string | null;
};

function statusLabel(value: boolean): string {
  return value ? "Configured" : "Missing";
}

export function IntegrationStatusPanel(props: IntegrationStatusProps): JSX.Element {
  const items = [
    { label: "Google OAuth", value: statusLabel(props.googleOauthConfigured) },
    { label: "Google Maps", value: statusLabel(props.googleMapsConfigured) },
    { label: "Worker Queue", value: statusLabel(props.workerConfigured) },
    { label: "Connected Accounts", value: String(props.connectedAccounts) },
    { label: "Synced Profiles", value: String(props.syncedProfiles) },
    {
      label: "Last Profile Sync",
      value: props.lastProfileSyncAt
        ? new Date(props.lastProfileSyncAt).toLocaleString()
        : "Not synced yet"
    }
  ];

  return (
    <article className="rounded-3xl border border-border bg-card p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Integration Status</h2>
          <p className="mt-2 text-sm text-slate-300">
            {props.organizationName} · {props.organizationRole}
          </p>
        </div>
      </div>
      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {items.map((item) => (
          <div key={item.label} className="rounded-2xl border border-border bg-slate-950/50 p-4">
            <p className="text-sm text-slate-400">{item.label}</p>
            <p className="mt-2 text-lg font-medium">{item.value}</p>
          </div>
        ))}
      </div>
    </article>
  );
}
