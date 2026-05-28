import { User, Zap, BookOpen, Shield } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

export const RiskBadge = ({ status }: { status: string }) => {
  const colors: Record<string, string> = {
    'Normal': 'bg-risk-normal text-white',
    'Elevated': 'bg-risk-elevated text-white',
    'High': 'bg-risk-high text-white',
    'Burnout Risk': 'bg-risk-burnout text-white',
  };
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-bold ${colors[status] || 'bg-gray-500 text-white'}`}>
      {status}
    </span>
  );
};

export const EngineerCard = ({ engineer, load }: { engineer: any, load: any }) => {
  const radarData = [
    { subject: 'Tickets', A: load.breakdown.active_tickets },
    { subject: 'Priority', A: load.breakdown.high_priority },
    { subject: 'Context', A: load.breakdown.context_switching },
    { subject: 'Deps', A: load.breakdown.dependencies },
    { subject: 'Repos', A: load.breakdown.repo_ownership },
    { subject: 'Prod', A: load.breakdown.prod_support },
    { subject: 'Incidents', A: load.breakdown.active_incidents },
  ];

  return (
    <div className="bg-clm-card rounded-xl p-6 border border-slate-700 hover:border-clm-accent transition-all shadow-xl">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-bold text-white">{engineer.name}</h3>
          <p className="text-slate-400 text-sm">{engineer.role} • {engineer.team}</p>
        </div>
        <RiskBadge status={load.status} />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="h-40 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
              <PolarGrid stroke="#475569" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar name="Load" dataKey="A" stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.6} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="flex flex-col justify-center items-center text-center">
          <span className="text-5xl font-black text-white">{load.score}</span>
          <span className="text-slate-500 text-xs uppercase tracking-widest">Cognitive Score</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
        <div className="flex items-center gap-2"><Zap size={14} className="text-yellow-400" /> {engineer.current_sprint.active_incidents} Incidents</div>
        <div className="flex items-center gap-2"><BookOpen size={14} className="text-blue-400" /> {engineer.structural_load.repos_owned} Repos</div>
        <div className="flex items-center gap-2"><Shield size={14} className="text-green-400" /> Prod Support</div>
        <div className="flex items-center gap-2"><User size={14} className="text-purple-400" /> {engineer.current_sprint.cross_team_dependencies} Deps</div>
      </div>
    </div>
  );
};
