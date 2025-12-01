import React, { useState } from 'react';
import { AlertTriangle, ExternalLink, ChevronDown, ChevronUp, Activity, Server, ShieldAlert } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function EventCard({ event }) {
    const [expanded, setExpanded] = useState(false);
    const { analysis } = event;

    const getImpactColor = (impact) => {
        switch (impact?.toLowerCase()) {
            case 'critical': return 'text-red-400 border-red-500/30 bg-red-500/10';
            case 'high': return 'text-orange-400 border-orange-500/30 bg-orange-500/10';
            case 'medium': return 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10';
            default: return 'text-blue-400 border-blue-500/30 bg-blue-500/10';
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 transition-colors"
        >
            <div className="p-6">
                <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                            <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${getImpactColor(analysis.impact_level)}`}>
                                {analysis.impact_level || 'Unknown'} Impact
                            </span>
                            <span className="text-xs text-slate-500 dark:text-slate-400">
                                {analysis.published_date || new Date(event.scan_date).toLocaleDateString()}
                            </span>
                            <span className="flex items-center gap-1 text-xs font-medium text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700">
                                {new URL(event.url).hostname.replace(/^www\./, '')}
                            </span>
                        </div>
                        <h3
                            className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2 leading-tight cursor-help"
                            title={event.title}
                        >
                            {event.title.split(' ').length > 30
                                ? event.title.split(' ').slice(0, 30).join(' ') + '...'
                                : event.title}
                        </h3>
                        <p className="text-slate-600 dark:text-slate-400 text-sm line-clamp-2">
                            {analysis.summary}
                        </p>
                    </div>
                    <a
                        href={event.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-slate-400 hover:text-blue-500 dark:hover:text-blue-400 transition-colors rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
                    >
                        <ExternalLink className="w-5 h-5" />
                    </a>
                </div>

                <button
                    onClick={() => setExpanded(!expanded)}
                    className="w-full mt-4 flex items-center justify-center gap-2 py-2 text-xs font-medium text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors border-t border-slate-200 dark:border-slate-800/50"
                >
                    {expanded ? (
                        <>Show Less <ChevronUp className="w-3 h-3" /></>
                    ) : (
                        <>Deep Analysis <ChevronDown className="w-3 h-3" /></>
                    )}
                </button>
            </div>

            <AnimatePresence>
                {expanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="bg-slate-50/50 dark:bg-slate-900/50 border-t border-slate-200 dark:border-slate-800"
                    >
                        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <h4 className="flex items-center gap-2 text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">
                                    <ShieldAlert className="w-4 h-4 text-red-500 dark:text-red-400" />
                                    Attack Vectors
                                </h4>
                                <ul className="space-y-2">
                                    {analysis.attack_vectors.map((vector, i) => (
                                        <li key={i} className="text-sm text-slate-600 dark:text-slate-400 flex items-start gap-2">
                                            <span className="w-1.5 h-1.5 rounded-full bg-red-400/50 mt-1.5" />
                                            {vector}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div>
                                <h4 className="flex items-center gap-2 text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">
                                    <Activity className="w-4 h-4 text-yellow-500 dark:text-yellow-400" />
                                    Vulnerabilities
                                </h4>
                                <ul className="space-y-2">
                                    {analysis.vulnerabilities.map((vuln, i) => (
                                        <li key={i} className="text-sm text-slate-600 dark:text-slate-400 flex items-start gap-2">
                                            <span className="w-1.5 h-1.5 rounded-full bg-yellow-400/50 mt-1.5" />
                                            {vuln}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div className="md:col-span-2">
                                <h4 className="flex items-center gap-2 text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">
                                    <Server className="w-4 h-4 text-blue-500 dark:text-blue-400" />
                                    Technical Details
                                </h4>
                                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed bg-white/50 dark:bg-slate-950/50 p-4 rounded-lg border border-slate-200 dark:border-slate-800">
                                    {analysis.technical_details}
                                </p>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}
