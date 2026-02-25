import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    Mail,
    MessageSquare,
    Clock,
    Search,
    Filter,
    Trash2,
    CheckCircle,
    Eye,
    ChevronLeft,
    ChevronRight,
    User
} from 'lucide-react';
import { axiosInstance } from '../api/axios';
import toast from 'react-hot-toast';
import Sidebar from '../components/Sidebar';
import { useTheme } from '../context/ThemeContext';

const Queries = () => {
    const { isDarkMode } = useTheme();
    const [queries, setQueries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filter, setFilter] = useState('all'); // all, read, unread
    const [selectedQuery, setSelectedQuery] = useState(null);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);

    const fetchQueries = async () => {
        setLoading(true);
        try {
            const response = await axiosInstance.get('/superAdmin/api/contact-queries/');
            const data = response.data;
            setQueries(Array.isArray(data) ? data : (data?.results || []));
        } catch (error) {
            console.error('Error fetching queries:', error);
            toast.error('Failed to load queries');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchQueries();
    }, []);

    const handleMarkRead = async (id) => {
        try {
            await axiosInstance.post(`/superAdmin/api/contact-queries/${id}/mark_read/`);
            toast.success('Query marked as read');
            fetchQueries();
            if (selectedQuery?.id === id) {
                setSelectedQuery({ ...selectedQuery, is_read: true });
            }
        } catch (error) {
            console.error('Error marking as read:', error);
            toast.error('Failed to update status');
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure you want to delete this query?')) return;
        try {
            await axiosInstance.delete(`/superAdmin/api/contact-queries/${id}/`);
            toast.success('Query deleted');
            setSelectedQuery(null);
            fetchQueries();
        } catch (error) {
            console.error('Error deleting query:', error);
            toast.error('Failed to delete query');
        }
    };

    const filteredQueries = (Array.isArray(queries) ? queries : []).filter(q => {
        const matchesSearch =
            q.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            q.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            q.subject.toLowerCase().includes(searchTerm.toLowerCase());

        if (filter === 'read') return matchesSearch && q.is_read;
        if (filter === 'unread') return matchesSearch && !q.is_read;
        return matchesSearch;
    });

    return (
        <div className={`flex min-h-screen ${isDarkMode ? 'bg-slate-950' : 'bg-slate-50'}`}>
            <Sidebar isSidebarOpen={isSidebarOpen} activePage="Queries" />

            <main className="flex-1 p-8 overflow-y-auto">
                <div className="max-w-7xl mx-auto">
                    {/* Header */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                        <div>
                            <h1 className={`text-3xl font-bold ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>
                                Customer Queries
                            </h1>
                            <p className="text-slate-500 font-medium">Manage and respond to customer inquiries from the Contact Us form.</p>
                        </div>

                        <div className="flex items-center gap-3">
                            <div className={`flex items-center gap-2 px-4 py-2 rounded-xl border ${isDarkMode ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200 shadow-sm'}`}>
                                <Search className="w-4 h-4 text-slate-400" />
                                <input
                                    type="text"
                                    placeholder="Search queries..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="bg-transparent border-none focus:ring-0 text-sm w-48 font-medium placeholder-slate-500"
                                />
                            </div>

                            <select
                                value={filter}
                                onChange={(e) => setFilter(e.target.value)}
                                className={`px-4 py-2 rounded-xl border text-sm font-semibold focus:ring-2 focus:ring-blue-500 transition-all ${isDarkMode ? 'bg-slate-900 border-slate-800 text-slate-300' : 'bg-white border-slate-200 text-slate-600 shadow-sm'}`}
                            >
                                <option value="all">All Queries</option>
                                <option value="unread">Unread Only</option>
                                <option value="read">Read Only</option>
                            </select>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Query List */}
                        <div className="lg:col-span-1 space-y-4">
                            {loading ? (
                                [1, 2, 3].map(i => (
                                    <div key={i} className={`h-24 rounded-2xl animate-pulse ${isDarkMode ? 'bg-slate-900' : 'bg-slate-200'}`}></div>
                                ))
                            ) : filteredQueries.length > 0 ? (
                                filteredQueries.map((query) => (
                                    <motion.div
                                        layout
                                        key={query.id}
                                        onClick={() => setSelectedQuery(query)}
                                        className={`p-4 rounded-2xl border cursor-pointer transition-all ${selectedQuery?.id === query.id
                                            ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-500/30'
                                            : isDarkMode
                                                ? 'bg-slate-900 border-slate-800 hover:border-slate-700'
                                                : 'bg-white border-slate-200 hover:border-blue-200 shadow-sm'
                                            }`}
                                    >
                                        <div className="flex justify-between items-start mb-2">
                                            <h3 className={`font-bold truncate ${selectedQuery?.id === query.id ? 'text-white' : isDarkMode ? 'text-white' : 'text-slate-900'}`}>
                                                {query.subject}
                                            </h3>
                                            {!query.is_read && (
                                                <span className="w-2 h-2 rounded-full bg-blue-400 ring-4 ring-blue-400/20"></span>
                                            )}
                                        </div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <User className={`w-3 h-3 ${selectedQuery?.id === query.id ? 'text-blue-100' : 'text-slate-500'}`} />
                                            <p className={`text-xs font-semibold ${selectedQuery?.id === query.id ? 'text-blue-100' : 'text-slate-500'}`}>{query.name}</p>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Clock className={`w-3 h-3 ${selectedQuery?.id === query.id ? 'text-blue-100' : 'text-slate-500'}`} />
                                            <p className={`text-[10px] font-bold uppercase tracking-wider ${selectedQuery?.id === query.id ? 'text-blue-100' : 'text-slate-400'}`}>
                                                {new Date(query.created_at).toLocaleDateString()}
                                            </p>
                                        </div>
                                    </motion.div>
                                ))
                            ) : (
                                <div className={`text-center py-12 rounded-2xl border border-dashed ${isDarkMode ? 'border-slate-800 text-slate-500' : 'border-slate-200 text-slate-400'}`}>
                                    No queries found matching the filters.
                                </div>
                            )}
                        </div>

                        {/* Query Detail */}
                        <div className="lg:col-span-2">
                            {selectedQuery ? (
                                <motion.div
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    className={`rounded-3xl border p-8 ${isDarkMode ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200 shadow-xl'}`}
                                >
                                    <div className="flex justify-between items-start mb-8 border-b pb-6 border-slate-100 dark:border-slate-800">
                                        <div>
                                            <div className="flex items-center gap-3 mb-2">
                                                <h2 className={`text-2xl font-black ${isDarkMode ? 'text-white' : 'text-slate-900'}`}>
                                                    {selectedQuery.subject}
                                                </h2>
                                                {selectedQuery.is_read ? (
                                                    <span className="px-2 py-1 rounded-md bg-emerald-100 text-emerald-600 text-[10px] font-bold uppercase">Read</span>
                                                ) : (
                                                    <span className="px-2 py-1 rounded-md bg-blue-100 text-blue-600 text-[10px] font-bold uppercase">New</span>
                                                )}
                                            </div>
                                            <div className="flex flex-wrap gap-4 text-sm font-medium text-slate-500">
                                                <span className="flex items-center gap-2"><User className="w-4 h-4" /> {selectedQuery.name}</span>
                                                <span className="flex items-center gap-2 font-bold text-blue-500"><Mail className="w-4 h-4" /> {selectedQuery.email}</span>
                                                <span className="flex items-center gap-2"><Clock className="w-4 h-4" /> {new Date(selectedQuery.created_at).toLocaleString()}</span>
                                            </div>
                                        </div>
                                        <div className="flex gap-2">
                                            {!selectedQuery.is_read && (
                                                <button
                                                    onClick={() => handleMarkRead(selectedQuery.id)}
                                                    className="p-2 rounded-xl bg-emerald-50 text-emerald-600 hover:bg-emerald-100 transition-colors"
                                                    title="Mark as Read"
                                                >
                                                    <CheckCircle className="w-5 h-5" />
                                                </button>
                                            )}
                                            <button
                                                onClick={() => handleDelete(selectedQuery.id)}
                                                className="p-2 rounded-xl bg-rose-50 text-rose-600 hover:bg-rose-100 transition-colors"
                                                title="Delete Query"
                                            >
                                                <Trash2 className="w-5 h-5" />
                                            </button>
                                        </div>
                                    </div>

                                    <div className="space-y-6">
                                        <div className={`p-6 rounded-2xl ${isDarkMode ? 'bg-slate-800/50' : 'bg-slate-50'}`}>
                                            <h4 className={`text-xs font-black uppercase tracking-[0.2em] mb-4 ${isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                                                Customer Message
                                            </h4>
                                            <p className={`text-lg leading-relaxed whitespace-pre-wrap ${isDarkMode ? 'text-slate-300' : 'text-slate-800'}`}>
                                                {selectedQuery.message}
                                            </p>
                                        </div>

                                        <div className="flex gap-4">
                                            <a
                                                href={`mailto:${selectedQuery.email}?subject=RE: ${selectedQuery.subject}`}
                                                className="flex-1 flex items-center justify-center gap-3 px-8 py-4 rounded-2xl bg-blue-600 text-white font-black text-lg hover:bg-blue-700 shadow-xl shadow-blue-500/20 transition-all hover:-translate-y-1"
                                            >
                                                <Mail className="w-5 h-5" />
                                                Reply via Email
                                            </a>
                                        </div>
                                    </div>
                                </motion.div>
                            ) : (
                                <div className={`h-full flex flex-col items-center justify-center rounded-3xl border border-dashed p-12 ${isDarkMode ? 'bg-slate-900 border-slate-800 text-slate-500' : 'bg-white border-slate-200 text-slate-400'}`}>
                                    <MessageSquare className="w-20 h-20 mb-4 opacity-10" />
                                    <h3 className="text-xl font-bold">Select a query to view details</h3>
                                    <p className="font-medium">Responses will be sent via the customer's provide email address.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Queries;
