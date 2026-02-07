import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, FileText, CheckCircle, AlertCircle, BarChart2, Plus, Trash2, Download, Zap, RefreshCw, Loader } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import ThemeSwitcher from '../components/ThemeSwitcher';

const Dashboard = () => {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [newProjectName, setNewProjectName] = useState('');
    const [showNewProject, setShowNewProject] = useState(false);
    const navigate = useNavigate();

    // Polling for updates
    useEffect(() => {
        console.log("Dashboard mounted");
        fetchProjects();
        const interval = setInterval(fetchProjects, 3000); // Poll every 3s
        return () => clearInterval(interval);
    }, []);

    const fetchProjects = async () => {
        try {
            const token = localStorage.getItem('token');
            console.log("Token present:", !!token);
            if (!token) {
                console.log("No token, redirecting to login");
                navigate('/login');
                return;
            }

            console.log("Fetching projects...");
            const res = await axios.get('http://localhost:8000/api/v1/projects/', {
                headers: { Authorization: `Bearer ${token}` }
            });
            console.log("Projects fetched:", res.data);
            setProjects(res.data);
            setLoading(false);
        } catch (err) {
            console.error("Failed to fetch projects", err);
            if (err.response && err.response.status === 401) {
                console.log("Unauthorized, clearing token and redirecting");
                localStorage.removeItem('token');
                navigate('/login');
            }
        }
    };

    const createProject = async () => {
        if (!newProjectName) return;
        try {
            const token = localStorage.getItem('token');
            await axios.post('http://localhost:8000/api/v1/projects/',
                { name: newProjectName, company_name: newProjectName, website: "" },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setNewProjectName('');
            setShowNewProject(false);
            fetchProjects();
        } catch (err) {
            console.error("Create project failed", err);
            alert('Failed to create project');
        }
    };

    return (
        <div
            className="pt-24 px-4 max-w-7xl mx-auto min-h-screen bg-brand-dark"
        >
            <div className="flex justify-between items-center mb-10">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <h1 className="text-3xl font-bold font-display text-white">Deal Flow</h1>
                    <p className="text-slate-400 text-sm">Manage your teaser generation pipeline.</p>
                </motion.div>
                <div className="flex items-center gap-4">
                    <ThemeSwitcher />
                    <motion.button
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setShowNewProject(true)}
                        className="btn-primary flex items-center gap-2 shadow-lg shadow-brand-primary/20"
                    >
                        <Plus className="w-5 h-5" /> New Deal
                    </motion.button>
                </div>
            </div>

            <motion.div layout>
                {showNewProject && (
                    <motion.div
                        initial={{ opacity: 0, y: -20, height: 0 }}
                        animate={{ opacity: 1, y: 0, height: 'auto' }}
                        exit={{ opacity: 0, y: -20, height: 0 }}
                        className="mb-8 p-6 glass-card border-brand-primary/50 overflow-hidden"
                    >
                        <h3 className="text-lg font-bold mb-4 text-white">Initialize New Deal</h3>
                        <div className="flex flex-col sm:flex-row gap-4">
                            <input
                                type="text"
                                value={newProjectName}
                                onChange={(e) => setNewProjectName(e.target.value)}
                                placeholder="Client Name (e.g. Project Titan)"
                                className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 focus:ring-2 focus:ring-brand-primary outline-none text-white transition-all"
                            />
                            <div className="flex gap-2">
                                <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={createProject} className="btn-primary whitespace-nowrap">Create Workspace</motion.button>
                                <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={() => setShowNewProject(false)} className="px-4 py-2 text-slate-400 hover:text-white transition-colors">Cancel</motion.button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </motion.div>

            <motion.div
                layout
                className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
                {projects.map((project, i) => (
                    <motion.div
                        key={project.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        layout
                    >
                        <ProjectCard project={project} refresh={fetchProjects} />
                    </motion.div>
                ))}
            </motion.div>

            {projects.length === 0 && !loading && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center py-20 opacity-50 border-2 border-dashed border-slate-700 rounded-xl"
                >
                    <motion.div
                        animate={{ y: [0, -10, 0] }}
                        transition={{ duration: 3, repeat: Infinity }}
                    >
                        <Zap className="w-16 h-16 mx-auto mb-4 text-slate-600" />
                    </motion.div>
                    <p className="text-slate-400">No active deals. Start a new workflow above.</p>
                </motion.div>
            )}
        </div>
    );
};

const ProjectCard = ({ project, refresh }) => {
    const [uploading, setUploading] = useState(false);

    const handleFileUpload = async (e) => {
        if (!e.target.files) return;
        setUploading(true);
        const file = e.target.files[0];
        const formData = new FormData();
        formData.append('file', file);

        try {
            const token = localStorage.getItem('token');
            await axios.post(`http://localhost:8000/api/v1/projects/${project.id}/upload`, formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });
            refresh();
        } catch (err) {
            alert('Upload failed');
        } finally {
            setUploading(false);
        }
    };

    const handleGenerate = async () => {
        try {
            const token = localStorage.getItem('token');
            await axios.post(`http://localhost:8000/api/v1/projects/${project.id}/generate`, {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            refresh();
        } catch (err) {
            alert('Generation failed');
        }
    };

    const handleDownload = async (type = 'ppt') => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`http://localhost:8000/api/v1/projects/${project.id}/download/${type}`, {
                headers: { Authorization: `Bearer ${token}` },
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            const ext = type === 'ppt' ? 'pptx' : 'pdf';
            link.setAttribute('download', `${project.company_name}_${type === 'ppt' ? 'Teaser' : 'Citations'}.${ext}`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            alert("Download failed");
        }
    };

    const handleDelete = async () => {
        if (!window.confirm(`Are you sure you want to delete "${project.company_name}"? This cannot be undone.`)) {
            return;
        }
        try {
            const token = localStorage.getItem('token');
            await axios.delete(`http://localhost:8000/api/v1/projects/${project.id}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            refresh();
        } catch (err) {
            alert('Failed to delete project');
        }
    };

    const StatusBadge = ({ status }) => {
        const styles = {
            pending: "bg-slate-700/50 text-slate-400 border-slate-600",
            processing: "bg-brand-primary/10 text-brand-primary border-brand-primary animate-pulse",
            completed: "bg-teal-500/10 text-teal-400 border-teal-500",
            failed: "bg-red-500/10 text-red-400 border-red-500"
        };
        const icons = {
            pending: <div className="w-2 h-2 rounded-full bg-slate-400" />,
            processing: <Loader className="w-3 h-3 animate-spin" />,
            completed: <CheckCircle className="w-3 h-3" />,
            failed: <AlertCircle className="w-3 h-3" />
        };
        return (
            <motion.div
                layout
                className={`flex items-center gap-2 px-3 py-1 rounded-full border text-[10px] font-bold uppercase tracking-wider ${styles[status]}`}
            >
                {icons[status]}
                {status}
            </motion.div>
        );
    };

    return (
        <motion.div
            whileHover={{ y: -5, borderColor: "rgba(14, 165, 233, 0.3)" }}
            className="glass-card p-0 flex flex-col h-full group transition-all duration-300 overflow-hidden"
        >
            {/* Header */}
            <div className="p-6 border-b border-white/5 bg-gradient-to-br from-white/5 to-transparent">
                <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-bold text-white truncate flex-1 mr-2" title={project.company_name}>
                        {project.company_name}
                    </h3>
                    <div className="flex items-center gap-2">
                        <StatusBadge status={project.status} />
                        <motion.button
                            whileHover={{ scale: 1.1, color: "#f87171" }}
                            whileTap={{ scale: 0.9 }}
                            onClick={handleDelete}
                            className="p-1.5 rounded-lg text-slate-500 transition-colors"
                            title="Delete project"
                        >
                            <Trash2 className="w-4 h-4" />
                        </motion.button>
                    </div>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                    {project.sector && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="flex items-center gap-1.5 text-xs text-brand-accent px-2 py-0.5 rounded-md bg-brand-accent/10 border border-brand-accent/20 font-medium"
                        >
                            <Zap className="w-3 h-3" /> {project.sector}
                        </motion.div>
                    )}
                    <div className="flex items-center gap-1.5 text-xs text-slate-400 px-2 py-0.5 rounded-md bg-white/5 border border-white/10 uppercase tracking-tighter">
                        <FileText className="w-3 h-3" /> {project.files?.length || 0} Docs
                    </div>
                </div>
            </div>

            {/* Body */}
            <div className="p-6 flex-1 max-h-[300px] overflow-y-auto">
                <div className="space-y-4">
                    {/* Document List */}
                    {project.files && project.files.length > 0 && (
                        <div className="space-y-2">
                            <div className="text-[10px] uppercase text-slate-500 font-bold mb-1 tracking-wider">Attached Documents</div>
                            {project.files.map((file, i) => (
                                <motion.div
                                    key={file.id}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: i * 0.05 }}
                                    className="flex items-center gap-2 p-2 rounded bg-white/5 border border-white/5 text-xs text-slate-300 hover:bg-white/10 transition-colors"
                                >
                                    <FileText className="w-3 h-3 text-brand-primary" />
                                    <span className="truncate flex-1">{file.filename}</span>
                                    <span className="text-[10px] text-slate-500 uppercase font-mono">{file.file_type}</span>
                                </motion.div>
                            ))}
                        </div>
                    )}
                    {project.status === 'completed' ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="space-y-4"
                        >
                            <div className="grid grid-cols-2 gap-3 mt-2">
                                <motion.div
                                    whileHover={{ scale: 1.05 }}
                                    className="bg-slate-800/40 p-3 rounded-lg border border-white/5 text-center"
                                >
                                    <div className="text-[10px] uppercase text-slate-500 font-bold mb-1">
                                        REVENUE ({project.metrics?.year || 'FY'})
                                    </div>
                                    <div className="text-lg text-white font-display font-bold">
                                        {project.metrics?.revenue ? `$${project.metrics.revenue}M` : 'N/A'}
                                    </div>
                                </motion.div>
                                <motion.div
                                    whileHover={{ scale: 1.05 }}
                                    className="bg-slate-800/40 p-3 rounded-lg border border-white/5 text-center"
                                >
                                    <div className="text-[10px] uppercase text-slate-500 font-bold mb-1">EBITDA %</div>
                                    <div className="text-lg text-white font-display font-bold">
                                        {project.metrics?.ebitda_margin || 'N/A'}
                                    </div>
                                </motion.div>
                            </div>
                            <div className="bg-slate-800/20 p-2 rounded text-[10px] text-slate-500 flex justify-between items-center px-3">
                                <span className="font-bold tracking-wider">ARTIFACTS GENERATED</span>
                                <span className="px-1.5 py-0.5 rounded bg-brand-primary/10 text-brand-primary font-bold">
                                    {project.artifacts ? project.artifacts.length : 0}
                                </span>
                            </div>
                        </motion.div>
                    ) : (
                        <div className="space-y-3 pt-2">
                            <div className="text-xs text-slate-400 italic flex items-center gap-2">
                                {project.status === 'processing' && <RefreshCw className="w-3 h-3 animate-spin text-brand-primary" />}
                                {project.status === 'pending' ? 'Upload data to begin generation.' : 'Kelp AI is synthesizing insights...'}
                            </div>
                            <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{
                                        width: project.status === 'processing' ? '100%' : '0%',
                                        x: project.status === 'processing' ? ['-100%', '100%'] : 0
                                    }}
                                    transition={{
                                        width: { duration: 0.5 },
                                        x: { duration: 1.5, repeat: Infinity, ease: "linear" }
                                    }}
                                    className="h-full bg-gradient-to-r from-brand-primary to-brand-accent"
                                />
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Actions */}
            <div className="p-4 border-t border-white/5 bg-black/20">
                {project.status === 'pending' && (
                    <div className="flex gap-2">
                        <motion.label
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className={`flex-1 btn-secondary text-center cursor-pointer text-sm py-2 flex items-center justify-center gap-2 ${uploading ? 'opacity-50' : ''}`}
                        >
                            <Upload className="w-4 h-4" />
                            {uploading ? 'Uploading...' : 'Upload'}
                            <input type="file" onChange={handleFileUpload} className="hidden" accept=".pdf,.xlsx" disabled={uploading} />
                        </motion.label>

                        <motion.button
                            whileHover={(!project.files || project.files.length === 0) ? {} : { scale: 1.02 }}
                            whileTap={(!project.files || project.files.length === 0) ? {} : { scale: 0.98 }}
                            onClick={handleGenerate}
                            disabled={!project.files || project.files.length === 0}
                            className={`flex-1 btn-primary text-sm py-2 flex items-center justify-center gap-2 shadow-lg shadow-brand-primary/10 ${(!project.files || project.files.length === 0) ? 'opacity-50 grayscale cursor-not-allowed' : ''}`}
                            title={(!project.files || project.files.length === 0) ? "Upload a document first" : "Synthesize insights"}
                        >
                            <Zap className="w-4 h-4" /> Generate
                        </motion.button>
                    </div>
                )}

                {project.status === 'processing' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="w-full py-2 flex items-center justify-center gap-3 text-brand-primary text-sm font-bold uppercase tracking-widest"
                    >
                        <Loader className="w-4 h-4 animate-spin" />
                        Analyzing...
                    </motion.div>
                )}

                {project.status === 'completed' && (
                    <div className="flex flex-col gap-2">
                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => handleDownload('ppt')}
                            className="w-full btn-primary text-sm py-2.5 flex items-center justify-center gap-2 shadow-lg shadow-brand-primary/10"
                        >
                            <Download className="w-4 h-4" /> Download Teaser (PPT)
                        </motion.button>
                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => handleDownload('citation_doc')}
                            className="w-full btn-secondary text-sm py-2 flex items-center justify-center gap-2 border-slate-700 hover:border-slate-500"
                        >
                            <FileText className="w-4 h-4" /> Download Citations (PDF)
                        </motion.button>
                    </div>
                )}

                {project.status === 'failed' && (
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleGenerate}
                        className="w-full btn-secondary text-red-400 border-red-900/50 hover:bg-red-500/10 text-sm py-2 flex items-center justify-center gap-2 font-bold"
                    >
                        <RefreshCw className="w-4 h-4" /> Retry Generation
                    </motion.button>
                )}
            </div>
        </motion.div>
    );
};

export default Dashboard;
