"use client";

import { useEffect, useState } from "react";
import { RotateCcw, Search, Database, Layers } from "lucide-react";

export default function LogsPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [now, setNow] = useState(Date.now());
  
  // Layer 4 state
  const [query, setQuery] = useState("");
  const [recallResults, setRecallResults] = useState<any>(null);
  const [searching, setSearching] = useState(false);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/memories");
      const data = await res.json();
      setLogs(data);
      setNow(Date.now());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };
  
  const handleRecall = async (e: any) => {
    e.preventDefault();
    if (!query) return;
    
    setSearching(true);
    try {
      const res = await fetch("http://localhost:8000/api/recall", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 3 })
      });
      const data = await res.json();
      setRecallResults(data);
      
      fetchLogs();
    } catch (e) {
      console.error(e);
    } finally {
      setSearching(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className="min-h-screen bg-black text-white p-8 font-sans">
      <div className="max-w-7xl mx-auto pt-16">
        
        {/* HEADER */}
        <div className="flex justify-between items-end mb-12 border-b border-[#333333] pb-6">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight text-white mb-2">
              Synapse Internals
            </h1>
            <p className="text-[#888888] text-sm">Real-time view of the 4-layer biomimetic pipeline.</p>
          </div>
          <button 
            onClick={fetchLogs}
            className="px-4 py-2 bg-white hover:bg-[#E5E5E5] text-black transition-colors rounded text-sm font-medium flex items-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Sync State
          </button>
        </div>

        {/* LAYER DEFINITIONS */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-12">
          {[
            { id: 1, name: "Sensory Buffer", desc: "Ingests raw text and normalizes it." },
            { id: 2, name: "Evaluator", desc: "LLM scores Valence & assigns weights." },
            { id: 3, name: "Consolidation", desc: "Background sweep decays and prunes." },
            { id: 4, name: "Retrieval", desc: "Searches & triggers Rehearsal resets." }
          ].map(layer => (
            <div key={layer.id} className="bg-[#0A0A0A] border border-[#333333] p-4 rounded-md hover:bg-[#111111] transition-colors">
              <div className="text-xs text-[#888888] font-mono mb-2">LAYER 0{layer.id}</div>
              <h2 className="text-sm font-medium text-white mb-1">{layer.name}</h2>
              <p className="text-xs text-[#555555]">{layer.desc}</p>
            </div>
          ))}
        </div>
        
        {/* LAYER 4 TESTER */}
        <div className="bg-[#0A0A0A] border border-[#333333] rounded-md p-6 mb-12 relative overflow-hidden">
          <div className="flex items-center gap-2 mb-4">
            <Search className="w-4 h-4 text-[#888888]" />
            <h2 className="text-sm font-medium text-white">Test Layer 4 (Recall & Reinforce)</h2>
          </div>
          
          <form onSubmit={handleRecall} className="flex gap-3 mb-6 relative z-10">
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Query the memory graph..." 
              className="flex-1 bg-black border border-[#333333] rounded-md px-4 py-2 text-sm text-white placeholder-[#555555] focus:outline-none focus:border-[#888888] transition-colors"
            />
            <button 
              type="submit"
              disabled={searching || !query.trim()}
              className="px-6 py-2 bg-white text-black hover:bg-[#E5E5E5] disabled:opacity-50 transition-colors rounded-md text-sm font-medium"
            >
              {searching ? 'Searching...' : 'Recall'}
            </button>
          </form>
          
          {recallResults && (
            <div className="bg-black border border-[#333333] rounded-md p-4 relative z-10">
              <div className="text-xs text-[#888888] mb-4 uppercase tracking-widest font-medium">Top Results</div>
              
              {recallResults.error && (
                <div className="text-red-400 text-sm font-mono">Error: {recallResults.error}</div>
              )}
              
              {!recallResults.error && recallResults.matches?.length === 0 && (
                <div className="text-[#555555] text-sm italic">No relevant memories found in graph.</div>
              )}
              
              {!recallResults.error && recallResults.matches?.length > 0 && (
                <div className="space-y-2">
                  {recallResults.matches.map((m: any, i: number) => (
                    <div key={m.node_id} className="bg-[#0A0A0A] border border-[#333333] rounded p-3 flex justify-between items-center group hover:border-[#555555] transition-colors">
                      <div>
                        <div className="text-sm text-white mb-1">{m.text}</div>
                        <div className="text-[10px] text-[#555555] font-mono">{m.node_id}</div>
                      </div>
                      <div className="text-right flex gap-6">
                        <div>
                          <div className="text-[9px] text-[#888888] uppercase tracking-wider mb-1">Semantic Match</div>
                          <div className="text-xs text-white font-mono">{(m.semantic_similarity * 100).toFixed(1)}%</div>
                        </div>
                        <div>
                          <div className="text-[9px] text-[#888888] uppercase tracking-wider mb-1">Composite Score</div>
                          <div className="text-xs text-white font-mono">{(m.composite_score * 100).toFixed(1)}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* GLOBAL REGISTRY TABLE */}
        <div className="flex items-center gap-2 mb-4">
          <Database className="w-4 h-4 text-[#888888]" />
          <h2 className="text-sm font-medium text-white">Registry State (Layers 1-3)</h2>
        </div>
        
        {loading ? (
          <div className="animate-pulse space-y-2">
            <div className="h-10 bg-[#0A0A0A] rounded-md border border-[#333333]"></div>
            <div className="h-20 bg-[#0A0A0A] rounded-md border border-[#333333]"></div>
          </div>
        ) : (
          <div className="bg-[#0A0A0A] border border-[#333333] rounded-md overflow-hidden">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#111111] border-b border-[#333333] text-[10px] uppercase tracking-widest text-[#888888]">
                  <th className="p-3 font-medium border-r border-[#333333]">ID / Text (L1)</th>
                  <th className="p-3 font-medium border-r border-[#333333] text-center">Valence (L2)</th>
                  <th className="p-3 font-medium border-r border-[#333333] text-center">Weight (L2)</th>
                  <th className="p-3 font-medium border-r border-[#333333] text-center">Decay (L2)</th>
                  <th className="p-3 font-medium border-r border-[#333333] text-right">Age (L3)</th>
                  <th className="p-3 font-medium text-center">Status (L3)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#333333]">
                {logs.map((log: any) => {
                  const created = new Date(log.created_at);
                  const aliveHours = Math.max(0, (now - created.getTime()) / (1000 * 60 * 60));
                  
                  return (
                  <tr key={log.node_id} className="hover:bg-[#111111] transition-colors">
                    <td className="p-3 border-r border-[#333333] max-w-xs">
                      <div className="text-[10px] text-[#555555] font-mono mb-1 leading-none">{log.node_id.substring(0, 8)}</div>
                      <div className="text-sm text-[#E5E5E5] truncate" title={log.text}>{log.text}</div>
                    </td>
                    
                    <td className="p-3 border-r border-[#333333] text-center align-middle">
                      <span className="text-sm text-white font-mono">{log.valence_score}</span>
                    </td>
                    <td className="p-3 border-r border-[#333333] text-center align-middle">
                      <span className="text-sm text-[#A1A1AA] font-mono">
                        {log.weight_initial === null ? '∞' : log.weight_initial}
                      </span>
                    </td>
                    <td className="p-3 border-r border-[#333333] text-center align-middle">
                      <span className="text-sm text-[#A1A1AA] font-mono">
                        {log.decay_rate}
                      </span>
                    </td>
                    
                    <td className="p-3 border-r border-[#333333] text-right align-middle">
                      <span className="text-sm text-[#A1A1AA] font-mono">
                        {aliveHours.toFixed(2)}h
                      </span>
                    </td>
                    <td className="p-3 text-center align-middle">
                      <div className="flex justify-center">
                        <span className={`px-2 py-0.5 rounded text-[10px] uppercase tracking-wider font-medium border ${
                          log.status === 'active' ? 'bg-[#0A0A0A] border-[#333333] text-white' :
                          log.status === 'pending_prune' ? 'bg-[#1a1a1a] border-[#555555] text-[#A1A1AA]' :
                          'bg-transparent border-[#333333] text-[#555555]'
                        }`}>
                          {log.status}
                        </span>
                      </div>
                    </td>
                  </tr>
                )})}
                {logs.length === 0 && (
                  <tr>
                    <td colSpan={6} className="p-8 text-center text-[#555555] text-sm">
                      No memory traces found in registry.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
