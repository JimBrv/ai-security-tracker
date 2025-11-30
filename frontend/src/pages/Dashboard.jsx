import React, { useState, useEffect } from 'react';
import axios from 'axios';
import EventCard from '../components/EventCard';
import { RefreshCw, Search, ShieldAlert, Activity, AlertTriangle } from 'lucide-react';

export default function Dashboard({ darkMode }) {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedTags, setSelectedTags] = useState(new Set());

    const fetchEvents = async () => {
        setLoading(true);
        try {
            const response = await axios.get('http://localhost:8000/events');
            // Sort by published_at desc
            const sorted = response.data.sort((a, b) => new Date(b.published_at) - new Date(a.published_at));
            setEvents(sorted);
        } catch (error) {
            console.error("Failed to fetch events", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEvents();
    }, []);

    // Extract unique tags from events
    const availableTags = React.useMemo(() => {
        const tags = {
            impact: new Set(),
            vectors: new Set(),
            vulns: new Set()
        };
        events.forEach(e => {
            if (e.analysis.impact_level) tags.impact.add(e.analysis.impact_level);
            e.analysis.attack_vectors?.forEach(v => tags.vectors.add(v));
            e.analysis.vulnerabilities?.forEach(v => tags.vulns.add(v));
        });
        return {
            impact: Array.from(tags.impact).sort(),
            vectors: Array.from(tags.vectors).sort().slice(0, 10),
            vulns: Array.from(tags.vulns).sort().slice(0, 10)
        };
    }, [events]);

    const toggleTag = (tag) => {
        const newTags = new Set(selectedTags);
        if (newTags.has(tag)) {
            newTags.delete(tag);
        } else {
            newTags.add(tag);
        }
        setSelectedTags(newTags);
    };

    const filteredEvents = events.filter(event => {
        const matchesSearch = event.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            event.analysis.summary.toLowerCase().includes(searchTerm.toLowerCase());

        if (selectedTags.size === 0) return matchesSearch;

        const eventTags = new Set([
            event.analysis.impact_level,
            ...(event.analysis.attack_vectors || []),
            ...(event.analysis.vulnerabilities || [])
        ].filter(Boolean));

        // OR logic: Show event if it has ANY of the selected tags
        const hasSelectedTag = Array.from(selectedTags).some(tag => eventTags.has(tag));

        return matchesSearch && hasSelectedTag;
    });

    // Diversify latest events: Try to get 1 from each domain first
    const latestEvents = React.useMemo(() => {
        if (events.length === 0) return [];

        const eventsByDomain = {};
        const uniqueEvents = [];
        const usedIds = new Set();

        // Group by domain
        events.forEach(event => {
            try {
                const domain = new URL(event.url).hostname;
                if (!eventsByDomain[domain]) {
                    eventsByDomain[domain] = [];
                }
                eventsByDomain[domain].push(event);
            } catch (e) {
                // Fallback if URL is invalid
                const domain = 'unknown';
                if (!eventsByDomain[domain]) eventsByDomain[domain] = [];
                eventsByDomain[domain].push(event);
            }
        });

        // 1. Pick the newest event from each domain
        Object.keys(eventsByDomain).forEach(domain => {
            const domainEvents = eventsByDomain[domain];
            if (domainEvents.length > 0) {
                uniqueEvents.push(domainEvents[0]);
                usedIds.add(domainEvents[0].id);
            }
        });

        // 2. Sort by date desc
        uniqueEvents.sort((a, b) => new Date(b.published_at) - new Date(a.published_at));

        // 3. If we don't have 5 yet, fill with remaining newest events
        if (uniqueEvents.length < 5) {
            for (const event of events) {
                if (uniqueEvents.length >= 5) break;
                if (!usedIds.has(event.id)) {
                    uniqueEvents.push(event);
                    usedIds.add(event.id);
                }
            }
            // Re-sort after adding fillers
            uniqueEvents.sort((a, b) => new Date(b.published_at) - new Date(a.published_at));
        }

        return uniqueEvents.slice(0, 5);
    }, [events]);

    const FilterSection = ({ title, tags, icon: Icon, theme }) => {
        if (tags.length === 0) return null;

        const getThemeClasses = (isActive) => {
            const baseClasses = "px-3 py-1 rounded-full text-xs font-medium transition-all border";

            if (isActive) {
                switch (theme) {
                    case 'red': return `${baseClasses} bg-red-500 text-white border-red-500`;
                    case 'amber': return `${baseClasses} bg-amber-500 text-white border-amber-500`;
                    case 'purple': return `${baseClasses} bg-purple-500 text-white border-purple-500`;
                    default: return `${baseClasses} bg-blue-500 text-white border-blue-500`;
                }
            }

            // Inactive state
            if (darkMode) {
                switch (theme) {
                    case 'red': return `${baseClasses} bg-red-500/10 text-red-400 border-red-500/20 hover:border-red-500/40`;
                    case 'amber': return `${baseClasses} bg-amber-500/10 text-amber-400 border-amber-500/20 hover:border-amber-500/40`;
                    case 'purple': return `${baseClasses} bg-purple-500/10 text-purple-400 border-purple-500/20 hover:border-purple-500/40`;
                    default: return `${baseClasses} bg-slate-800 text-slate-400 border-slate-700 hover:border-slate-600`;
                }
            } else {
                switch (theme) {
                    case 'red': return `${baseClasses} bg-red-50 text-red-600 border-red-200 hover:border-red-300`;
                    case 'amber': return `${baseClasses} bg-amber-50 text-amber-600 border-amber-200 hover:border-amber-300`;
                    case 'purple': return `${baseClasses} bg-purple-50 text-purple-600 border-purple-200 hover:border-purple-300`;
                    default: return `${baseClasses} bg-white text-slate-600 border-slate-200 hover:border-slate-300`;
                }
            }
        };

        const getTitleColor = () => {
            if (darkMode) {
                switch (theme) {
                    case 'red': return 'text-red-400';
                    case 'amber': return 'text-amber-400';
                    case 'purple': return 'text-purple-400';
                    default: return 'text-slate-500';
                }
            }
            switch (theme) {
                case 'red': return 'text-red-600';
                case 'amber': return 'text-amber-600';
                case 'purple': return 'text-purple-600';
                default: return 'text-slate-400';
            }
        };

        return (
            <div className="mb-6 last:mb-0">
                <h3 className={`flex items-center gap-2 text-xs font-bold uppercase tracking-wider mb-3 ${getTitleColor()}`}>
                    <Icon className="w-4 h-4" />
                    {title}
                </h3>
                <div className="flex flex-wrap gap-2">
                    {tags.map(tag => (
                        <button
                            key={tag}
                            onClick={() => toggleTag(tag)}
                            className={getThemeClasses(selectedTags.has(tag))}
                        >
                            {tag}
                        </button>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className="pt-24 pb-12 px-4 max-w-7xl mx-auto space-y-12">
            {/* Upper Section: Description & Latest 5 */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Left: Description */}
                <div className="lg:col-span-4 space-y-6">
                    <div>
                        <h1 className={`text-4xl font-bold mb-4 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                            AI Security Tracker
                        </h1>
                        <p className={`text-lg leading-relaxed ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                            Welcome to the AI Security Tracker. This platform automatically collects, analyzes, and summarizes the latest security events, vulnerabilities, and research related to Artificial Intelligence.
                        </p>
                        <p className={`mt-4 text-lg leading-relaxed ${darkMode ? 'text-slate-300' : 'text-slate-600'}`}>
                            Our goal is to provide a centralized, real-time intelligence feed for security researchers and AI practitioners to stay ahead of emerging threats in the rapidly evolving AI landscape.
                        </p>
                    </div>
                </div>

                {/* Right: Latest 5 Events */}
                <div className="lg:col-span-8">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                            Latest Intelligence
                        </h2>
                    </div>

                    {loading ? (
                        <div className="grid gap-4">
                            {[1, 2].map(i => (
                                <div key={i} className={`h-32 rounded-xl animate-pulse ${darkMode ? 'bg-slate-800/50' : 'bg-slate-200'}`} />
                            ))}
                        </div>
                    ) : (
                        <div className="grid gap-4">
                            {latestEvents.map(event => (
                                <EventCard key={event.id} event={event} compact={true} />
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Divider */}
            <div className={`h-px w-full ${darkMode ? 'bg-slate-800' : 'bg-slate-200'}`} />

            {/* Lower Section: All Events */}
            <div>
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-8">
                    <div className="flex-1">
                        <h2 className={`text-2xl font-bold mb-2 ${darkMode ? 'text-white' : 'text-slate-900'}`}>
                            All Security Events
                        </h2>
                        <p className={`mb-6 ${darkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                            Comprehensive list of all tracked security incidents.
                        </p>

                        {/* Filters */}
                        {!loading && (
                            <div className={`p-4 rounded-xl border mb-6 ${darkMode ? 'bg-slate-900/30 border-slate-800' : 'bg-slate-50 border-slate-200'}`}>
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className={`text-sm font-semibold ${darkMode ? 'text-slate-300' : 'text-slate-700'}`}>
                                        Filter by Tags
                                    </h3>
                                    {selectedTags.size > 0 && (
                                        <button
                                            onClick={() => setSelectedTags(new Set())}
                                            className="text-xs text-blue-500 hover:text-blue-400"
                                        >
                                            Clear all
                                        </button>
                                    )}
                                </div>
                                <FilterSection
                                    title="Impact Level"
                                    tags={availableTags.impact}
                                    icon={AlertTriangle}
                                    theme="purple"
                                />
                                <FilterSection
                                    title="Attack Vectors"
                                    tags={availableTags.vectors}
                                    icon={ShieldAlert}
                                    theme="red"
                                />
                                <FilterSection
                                    title="Vulnerabilities"
                                    tags={availableTags.vulns}
                                    icon={Activity}
                                    theme="amber"
                                />
                            </div>
                        )}
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                            <input
                                type="text"
                                placeholder="Search events..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className={`pl-9 pr-4 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 w-64 transition-colors ${darkMode
                                    ? 'bg-slate-900/50 border border-slate-800 text-slate-200'
                                    : 'bg-white border border-slate-200 text-slate-900'
                                    }`}
                            />
                        </div>
                        <button
                            onClick={fetchEvents}
                            className={`p-2 rounded-lg transition-colors border ${darkMode
                                ? 'bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700'
                                : 'bg-white hover:bg-slate-50 text-slate-600 border-slate-200'
                                }`}
                        >
                            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                        </button>
                    </div>
                </div>

                {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[1, 2, 3].map(i => (
                            <div key={i} className={`h-64 rounded-xl animate-pulse ${darkMode ? 'bg-slate-800/50' : 'bg-slate-200'}`} />
                        ))}
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {filteredEvents.map(event => (
                            <EventCard key={event.id} event={event} />
                        ))}
                        {filteredEvents.length === 0 && (
                            <div className="col-span-full text-center py-20 text-slate-500">
                                No events found matching your criteria.
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
