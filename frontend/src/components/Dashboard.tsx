import { useEffect } from 'react';
import { useCLMStore } from '../store/useCLMStore';
import { EngineerCard } from './EngineerCard';
import { AlertCircle, BrainCircuit, RefreshCw, TrendingUp, Sparkles } from 'lucide-react';

export const Dashboard = () => {
  const {
    engineers,
    recommendations,
    optimizationAction,
    isLoading,
    isOptimizing,
    error,
    fetchData,
    triggerIncident,
    fetchRecommendations
  } = useCLMStore();

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const burnoutCount = engineers.filter(e => e.load.status === 'Burnout Risk').length;
  const avgLoad = engineers.length > 0
    ? (engineers.reduce((acc, e) => acc + e.load.score, 0) / engineers.length).toFixed(1)
    : 0;

  return (
    <div className="min-h-screen bg-clm-dark text-slate-200 p-8 font-sans">
      {/* Header */}
      <div className="flex justify-between items-center mb-12">
        <div>
          <h1 className="text-4xl font-black text-white flex items-center gap-3">
            <BrainCircuit className="text-clm-accent" size={40} />
            Cognitive Load <span className="text-clm-accent">Manager</span>
          </h1>
          <p className="text-slate-400 mt-2">Human Observability & Burnout Prevention System</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => triggerIncident()}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg transition-all border border-slate-600 text-sm"
          >
            <AlertCircle size={16} className="text-red-400" />
            Simulate Incident
          </button>
          <button
            onClick={fetchData}
            className="flex items-center gap-2 bg-clm-accent hover:bg-sky-400 text-clm-dark font-bold px-4 py-2 rounded-lg transition-all text-sm"
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="bg-clm-card p-6 rounded-2xl border border-slate-700 flex items-center gap-6">
          <div className="p-4 bg-sky-500/10 rounded-full text-clm-accent"><TrendingUp size={32} /></div>
          <div>
            <p className="text-slate-400 text-sm uppercase tracking-wider">Avg Team Load</p>
            <p className="text-3xl font-bold text-white">{avgLoad}%</p>
          </div>
        </div>
        <div className="bg-clm-card p-6 rounded-2xl border border-slate-700 flex items-center gap-6">
          <div className="p-4 bg-red-500/10 rounded-full text-red-400"><AlertCircle size={32} /></div>
          <div>
            <p className="text-slate-400 text-sm uppercase tracking-wider">Burnout Risk</p>
            <p className="text-3xl font-bold text-white">{burnoutCount} Engineers</p>
          </div>
        </div>
        <div className="bg-clm-card p-6 rounded-2xl border border-slate-700 flex items-center gap-6">
          <div className="p-4 bg-purple-500/10 rounded-full text-purple-400"><BrainCircuit size={32} /></div>
          <div>
            <p className="text-slate-400 text-sm uppercase tracking-wider">System Health</p>
            <p className="text-3xl font-bold text-white">Saturated</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Engineer Grid */}
        <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
          {isLoading ? (
            <div className="col-span-2 text-center py-20 text-slate-500">Loading workload data...</div>
          ) : (
            engineers.map(({ engineer, load }) => (
              <EngineerCard key={engineer.id} engineer={engineer} load={load} />
            ))
          )}
        </div>

        {/* AI Panel */}
        <div className="bg-clm-card p-8 rounded-2xl border border-slate-700 h-fit sticky top-8">
          <div className="flex items-center gap-2 text-clm-accent mb-6">
            <Sparkles size={24} />
            <h2 className="text-xl font-bold text-white">AI Recommendations</h2>
          </div>

          {recommendations ? (
            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 text-slate-300 text-sm leading-relaxed whitespace-pre-wrap italic">
              "{recommendations}"
            </div>
          ) : isOptimizing ? (
            <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 text-slate-300 text-sm leading-relaxed">
              Analyzing team load and generating recommendations...
            </div>
          ) : (
            <div className="text-slate-500 text-sm italic mb-6">
              No recommendations generated yet.
            </div>
          )}

          {error && (
            <div className="mt-4 bg-red-500/10 border border-red-500/30 text-red-200 text-sm leading-relaxed p-3 rounded-xl">
              {error}
            </div>
          )}

          {optimizationAction && (
            <div className="mt-4 bg-emerald-500/10 border border-emerald-500/30 text-emerald-200 text-sm leading-relaxed p-3 rounded-xl">
              {optimizationAction}
            </div>
          )}

          <button
            onClick={fetchRecommendations}
            disabled={isOptimizing}
            className="w-full mt-6 py-3 bg-clm-accent text-clm-dark font-bold rounded-xl hover:bg-sky-400 transition-all disabled:opacity-50"
          >
            {isOptimizing ? 'Analyzing...' : 'Optimize Distribution'}
          </button>
        </div>
      </div>
    </div>
  );
};
